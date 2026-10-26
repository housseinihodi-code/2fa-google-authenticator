#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generateur PDF pur stdlib (aucune dependance) pour le guide d'integration 2FA."""
import zlib, sys

PAGE_W, PAGE_H = 595.28, 841.89
ML, MR, MT, MB = 56, 56, 60, 58
CONTENT_W = PAGE_W - ML - MR
NAVY = (0.078, 0.129, 0.247)
GRAY_BG = (0.960, 0.965, 0.972)
GRID = (0.79, 0.82, 0.86)
NOTE_BG = (1.0, 0.972, 0.882)
WARN_BG = (0.992, 0.925, 0.925)

HELV = {
 32:278,33:278,34:355,35:556,36:556,37:889,38:667,39:191,40:333,41:333,42:389,43:584,
 44:278,45:333,46:278,47:278,48:556,49:556,50:556,51:556,52:556,53:556,54:556,55:556,
 56:556,57:556,58:278,59:278,60:584,61:584,62:584,63:556,64:1015,65:667,66:667,67:722,
 68:722,69:667,70:611,71:778,72:722,73:278,74:500,75:667,76:556,77:833,78:722,79:778,
 80:667,81:778,82:722,83:667,84:611,85:722,86:667,87:944,88:667,89:667,90:611,91:278,
 92:278,93:278,94:469,95:556,96:333,97:556,98:556,99:500,100:556,101:556,102:278,103:556,
 104:556,105:222,106:222,107:500,108:222,109:833,110:556,111:556,112:556,113:556,114:333,
 115:500,116:278,117:556,118:500,119:722,120:500,121:500,122:500,123:334,124:260,125:334,126:584}
HELVB = {
 32:278,33:333,34:474,35:556,36:556,37:889,38:722,39:238,40:333,41:333,42:389,43:584,
 44:278,45:333,46:278,47:278,48:556,49:556,50:556,51:556,52:556,53:556,54:556,55:556,
 56:556,57:556,58:333,59:333,60:584,61:584,62:584,63:611,64:975,65:722,66:722,67:722,
 68:722,69:667,70:611,71:778,72:722,73:278,74:556,75:722,76:611,77:833,78:722,79:778,
 80:667,81:778,82:722,83:667,84:611,85:722,86:667,87:944,88:667,89:667,90:611,91:333,
 92:278,93:333,94:584,95:556,96:333,97:556,98:611,99:556,100:611,101:556,102:333,103:611,
 104:611,105:278,106:278,107:556,108:278,109:889,110:611,111:611,112:611,113:611,114:389,
 115:556,116:333,117:611,118:556,119:778,120:556,121:556,122:500,123:389,124:280,125:389,126:584}
ACC = {"à":97,"â":97,"ä":97,"á":97,"é":101,"è":101,"ê":101,"ë":101,"ç":99,"î":105,"ï":105,
 "í":105,"ô":111,"ö":111,"ó":111,"û":117,"ü":117,"ù":117,"À":65,"Â":65,"É":69,"È":69,
 "Ê":69,"Ç":99,"Î":73,"Ô":79,"Û":85,"«":65,"»":65,"—":150,"–":85,"’":33,"°":60,"œ":170}

def cw(ch, bold):
    o = ord(ch)
    t = HELVB if bold else HELV
    if o in t: return t[o]
    if ch in ACC:
        b = ACC[ch]
        return t.get(b, 556) if b > 40 else b*10
    return 556

def text_width(s, size, bold=False, mono=False):
    if mono:
        return len(s) * size * 0.6
    return sum(cw(c, bold) for c in s) / 1000.0 * size

def sanitize(s):
    r = (s.replace("→","->").replace("⟶","->").replace("≥",">=").replace("≤","<=")
          .replace("✅","[x]").replace("⚠️","/!\\").replace("⚠","/!\\").replace("☐","[ ]")
          .replace(" "," ").replace("\t","    "))
    out = []
    for ch in r:
        try:
            ch.encode("cp1252"); out.append(ch)
        except UnicodeEncodeError:
            out.append("?")
    return "".join(out)

def esc(s):
    return s.replace("\\","\\\\").replace("(","\\(").replace(")","\\)")

def wrap(s, maxw, size, bold=False, mono=False):
    s = sanitize(s)
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_width(trial, size, bold, mono) <= maxw or not cur:
            if text_width(trial, size, bold, mono) <= maxw:
                cur = trial
            else:
                piece = ""
                for ch in w:
                    if text_width(piece + ch, size, bold, mono) <= maxw:
                        piece += ch
                    else:
                        lines.append(piece); piece = ch
                cur = piece
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines or [""]

class PDF:
    def __init__(self):
        self.pages = []
        self.ops = []
        self.y = PAGE_H - MT
        self.page_no = 0
        self._start_page()

    def _start_page(self):
        if self.ops:
            self._flush_page()
        self.ops = []
        self.y = PAGE_H - MT
        self.page_no += 1

    def _flush_page(self):
        foot = "Module 2FA v1.0.0   -   Guide d'integration   -   p. %d" % self.page_no
        w = text_width(foot, 8)
        self.ops.append("BT /F1 8 Tf 0.4 0.4 0.4 rg 1 0 0 1 %.2f %.2f Tm (%s) Tj ET"
                        % ((PAGE_W - w) / 2, MB - 24, esc(foot)))
        self.pages.append("\n".join(self.ops))

    def need(self, h):
        if self.y - h < MB:
            self._start_page()

    def _txt(self, s, x, y, size, font="F1", color=(0,0,0)):
        self.ops.append("BT /%s %.2f Tf %.3f %.3f %.3f rg 1 0 0 1 %.2f %.2f Tm (%s) Tj ET"
                        % (font, size, color[0], color[1], color[2], x, y, esc(sanitize(s))))

    def _rect(self, x, y, w, h, fill=None, stroke=None, lw=0.75):
        if fill:
            self.ops.append("%.3f %.3f %.3f rg %.2f %.2f %.2f %.2f re f" % (fill[0],fill[1],fill[2],x,y,w,h))
        if stroke:
            self.ops.append("%.3f %.3f %.3f RG %.2f w %.2f %.2f %.2f %.2f re S" % (stroke[0],stroke[1],stroke[2],lw,x,y,w,h))

    def heading(self, text, level=1):
        size = 15 if level == 1 else (12 if level == 2 else 10.5)
        top = 18 if level == 1 else (13 if level == 2 else 10)
        self.need(size + top + 16)
        self.y -= top
        self._txt(text, ML, self.y, size, "F2", NAVY)
        self.y -= 3
        if level == 1:
            self.ops.append("%.3f %.3f %.3f RG 1.2 w %.2f %.2f m %.2f %.2f l S"
                            % (NAVY[0],NAVY[1],NAVY[2], ML, self.y, ML + CONTENT_W, self.y))
        self.y -= (10 if level == 1 else 6)

    def para(self, text, size=10, gap_after=6, indent=0, bold=False, color=(0,0,0)):
        lead = size + 3.2
        for ln in wrap(text, CONTENT_W - indent, size, bold):
            self.need(lead)
            self._txt(ln, ML + indent, self.y - size, size, "F2" if bold else "F1", color)
            self.y -= lead
        self.y -= gap_after

    def bullets(self, items, size=10, ordered=False):
        lead = size + 3.2
        for i, it in enumerate(items):
            marker = ("%d." % (i + 1)) if ordered else "-"
            first = True
            for ln in wrap(it, CONTENT_W - 18, size):
                self.need(lead)
                if first:
                    self._txt(marker, ML + 2, self.y - size, size, "F1", NAVY if not ordered else (0,0,0))
                    first = False
                self._txt(ln, ML + 18, self.y - size, size, "F1")
                self.y -= lead
            self.y -= 1.5
        self.y -= 5

    def code(self, lines, size=8.3):
        lead = size + 2.6
        pad = 6
        flat = []
        maxc = int((CONTENT_W - 2 * pad - 8) / (size * 0.6))
        for l in lines:
            l = sanitize(l.replace("\t", "    "))
            while len(l) > maxc:
                flat.append(l[:maxc]); l = "    " + l[maxc:]
            flat.append(l)
        block_h = lead * len(flat) + 2 * pad
        self.need(block_h + 6)
        top = self.y
        self._rect(ML, top - block_h, CONTENT_W, block_h, fill=GRAY_BG, stroke=GRID, lw=0.6)
        self._rect(ML, top - block_h, 3, block_h, fill=NAVY)
        ty = top - pad - size
        for l in flat:
            self._txt(l, ML + pad + 4, ty, size, "F3", (0.12, 0.12, 0.16))
            ty -= lead
        self.y = top - block_h - 8

    def callout(self, text, kind="note"):
        size = 9.3
        lead = size + 3
        bg = NOTE_BG if kind == "note" else WARN_BG
        bar = (0.85, 0.64, 0.0) if kind == "note" else (0.75, 0.23, 0.17)
        lines = wrap(text, CONTENT_W - 22, size)
        h = lead * len(lines) + 12
        self.need(h + 6)
        top = self.y
        self._rect(ML, top - h, CONTENT_W, h, fill=bg, stroke=bar, lw=0.6)
        self._rect(ML, top - h, 3, h, fill=bar)
        ty = top - 6 - size
        for l in lines:
            self._txt(l, ML + 12, ty, size, "F1", (0.15, 0.12, 0.05))
            ty -= lead
        self.y = top - h - 8

    def table(self, headers, rows, weights, size=8.5):
        lead = size + 2.8
        cw_ = [w / sum(weights) * CONTENT_W for w in weights]
        def row_lines(cells):
            per = [wrap(str(c), cw_[i] - 8, size) for i, c in enumerate(cells)]
            return per, max(len(p) for p in per)
        def draw_row(cells, header=False):
            per, n = row_lines(cells)
            h = lead * n + 6
            self.need(h)
            top = self.y
            if header:
                self._rect(ML, top - h, CONTENT_W, h, fill=NAVY)
            x = ML
            for i, col in enumerate(per):
                self._rect(x, top - h, cw_[i], h, stroke=GRID, lw=0.5)
                ty = top - 5 - size
                for ln in col:
                    self._txt(ln, x + 4, ty, size, "F2" if header else "F1",
                              (1,1,1) if header else (0.12,0.12,0.12))
                    ty -= lead
                x += cw_[i]
            self.y = top - h
        self.need(lead + 14)
        draw_row(headers, header=True)
        for r in rows:
            draw_row(r)
        self.y -= 8

    def cover(self, title, subs, meta):
        self.y = PAGE_H - 250
        for ln in wrap(title, CONTENT_W, 22, bold=True):
            self._txt(ln, ML, self.y, 22, "F2", NAVY); self.y -= 28
        self.y -= 10
        for s in subs:
            for ln in wrap(s, CONTENT_W, 11.5):
                self._txt(ln, ML, self.y, 11.5, "F1", (0.33,0.33,0.33)); self.y -= 16
            self.y -= 4
        self.y -= 40
        for m in meta:
            self._txt(m, ML, self.y, 9.5, "F1", (0.4,0.4,0.4)); self.y -= 14
        self._start_page()

    def build(self):
        self._flush_page()
        objs = []
        def add(s):
            objs.append(s); return len(objs)
        font_ids = {}
        for name, base in [("F1","Helvetica"),("F2","Helvetica-Bold"),("F3","Courier"),("F4","Helvetica-Oblique")]:
            font_ids[name] = add("<< /Type /Font /Subtype /Type1 /BaseFont /%s /Encoding /WinAnsiEncoding >>" % base)
        page_obj_ids, content_ids = [], []
        for pg in self.pages:
            comp = zlib.compress(pg.encode("cp1252", "replace"))
            cid = add(None)
            objs[cid-1] = ("<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(comp), comp, "\nendstream")
            content_ids.append(cid)
        fonts = " ".join("/%s %d 0 R" % (n, font_ids[n]) for n in font_ids)
        for cid in content_ids:
            page_obj_ids.append(add("<< /Type /Page /Parent \x00PAGES\x00 0 R /MediaBox [0 0 %.2f %.2f] "
                                    "/Resources << /Font << %s >> >> /Contents %d 0 R >>"
                                    % (PAGE_W, PAGE_H, fonts, cid)))
        kids_str = " ".join("%d 0 R" % p for p in page_obj_ids)
        pages_id = add("<< /Type /Pages /Count %d /Kids [%s] >>" % (len(page_obj_ids), kids_str))
        cat_id = add("<< /Type /Catalog /Pages %d 0 R >>" % pages_id)
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0] * (len(objs) + 1)
        for i, ob in enumerate(objs, start=1):
            offsets[i] = len(out)
            out += ("%d 0 obj\n" % i).encode()
            if isinstance(ob, tuple):
                head, comp, tail = ob
                out += head.encode("latin-1") + comp + tail.encode("latin-1")
            else:
                out += ob.replace("\x00PAGES\x00", str(pages_id)).encode("cp1252", "replace")
            out += b"\nendobj\n"
        xref_pos = len(out)
        out += ("xref\n0 %d\n" % (len(objs) + 1)).encode()
        out += b"0000000000 65535 f \n"
        for i in range(1, len(objs) + 1):
            out += ("%010d 00000 n \n" % offsets[i]).encode()
        out += ("trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
                % (len(objs) + 1, cat_id, xref_pos)).encode()
        return bytes(out)


def main(out_path):
    d = PDF()
    d.cover(
        "Module 2FA — Authentification à double facteur",
        ["Guide d'intégration pour l'équipe de développement du site hôte",
         "TOTP compatible Google Authenticator / Authy / FreeOTP — API REST Node.js autonome"],
        ["Version du module : 1.0.0",
         "Document rédigé le : 31 août 2026",
         "Nature : API REST, indépendante du frontend"])

    d.heading("Sommaire", 1)
    d.bullets([
        "1. Présentation et périmètre", "2. Principe d'intégration", "3. Prérequis",
        "4. Installation", "5. Configuration (.env)", "6. Base de données",
        "7. Référence des endpoints", "8. Parcours d'intégration côté site hôte",
        "9. Sécurité — points impératifs", "10. Codes d'erreur",
        "11. Tests et outils fournis", "12. Checklist de mise en production",
        "13. Dépannage rapide"])

    d.heading("1. Présentation et périmètre", 1)
    d.para("Le module ajoute une deuxième étape de connexion (code à 6 chiffres généré par une "
           "application d'authentification) à un site web existant, sans toucher à son système de connexion.")
    d.heading("Ce que le module fait", 3)
    d.bullets([
        "Génère un secret TOTP et le QR code à scanner dans Google Authenticator.",
        "Active / désactive le 2FA pour un utilisateur.",
        "Vérifie un code à 6 chiffres au moment de la connexion.",
        "Fournit des codes de récupération à usage unique (perte du téléphone).",
        "Chiffre les secrets en base (AES-256-GCM) et hache les codes de récupération (bcrypt).",
        "Applique un rate limiting sur les tentatives de vérification."])
    d.heading("Ce que le module ne fait PAS", 3)
    d.bullets([
        "Il ne gère pas la connexion (identifiant / mot de passe) ni les sessions : cela reste le rôle du site hôte.",
        "Il n'émet aucun jeton : il se contente de vérifier le JWT déjà produit par le site hôte.",
        "Il n'a pas d'interface graphique : c'est une API que le backend du site hôte appelle."])
    d.heading("Pile technique", 3)
    d.table(["Composant", "Détail"], [
        ["Exécution", "Node.js >= 18, Express 4"],
        ["Base de données", "MySQL 5.7+ / 8.x (dédiée ou partagée avec le site hôte)"],
        ["TOTP / QR", "speakeasy, qrcode"],
        ["Cryptographie", "AES-256-GCM (secrets), bcrypt (codes de récupération)"],
        ["Protection", "express-rate-limit sur /verify, /disable, /recovery-codes/regenerate"],
    ], [1, 3])

    d.heading("2. Principe d'intégration", 1)
    d.para("Le module se place derrière le backend du site hôte. Il ne parle jamais directement au navigateur.")
    d.code([
        "Navigateur",
        "   |  (identifiant + mot de passe, puis code 2FA)",
        "   v",
        "Backend du SITE HOTE    -- gere login, mot de passe, session, emet le JWT",
        "   |  Authorization: Bearer <JWT de l'utilisateur>",
        "   v",
        "MODULE 2FA (cette API)  -- verifie le JWT, applique la logique TOTP",
        "   |",
        "   v",
        "MySQL (tables two_factor_*)",
    ])
    d.para("Identification de l'utilisateur. Le module attend sur chaque requête le header "
           "Authorization: Bearer <jwt>. Ce JWT est celui que le site hôte émet déjà pour ses propres "
           "besoins. Le module le vérifie avec le même secret (JWT_SECRET) et lit l'identifiant de "
           "l'utilisateur dans le premier champ disponible du payload : sub, userId ou id.")
    d.callout("Le module ne signe aucun JWT. Il ne fait que les vérifier. Il faut donc lui communiquer "
              "la valeur de JWT_SECRET utilisée par le site hôte, et rien de plus.", "note")
    d.para("Variante possible (non activée par défaut) : si le module est appelé par une API centrale "
           "plutôt que directement par le backend applicatif, l'authentification par JWT peut être "
           "remplacée par une clé d'API de service (header X-Api-Key) accompagnée de l'identifiant "
           "utilisateur (header X-User-Id). Demander cette variante si besoin.", size=9, color=(0.4,0.4,0.4))

    d.heading("3. Prérequis", 1)
    d.bullets([
        "Node.js >= 18 et npm sur le serveur qui héberge le module.",
        "Une base MySQL accessible (base existante du site hôte, ou base dédiée).",
        "Le site hôte émet déjà des JWT signés en HS256, avec l'identifiant utilisateur dans sub, userId ou id.",
        "Communication HTTPS entre le backend hôte et le module (le JWT y circule)."])

    d.heading("4. Installation", 1)
    d.bullets([
        "Copier le dossier du module sur le serveur, par exemple dans /opt/2fa-google-authenticator.",
        "Installer les dépendances (voir bloc ci-dessous).",
        "Créer le fichier de configuration : cp .env.example .env  puis éditer .env (section 5).",
        "Créer la base (si dédiée) et jouer la migration SQL.",
        "Démarrer le module.",
        "Vérifier le log : « Module 2FA à l'écoute sur le port 4000 »."], ordered=True)
    d.code([
        "cd 2fa-google-authenticator",
        "npm install --production",
        "cp .env.example .env",
        "",
        "mysql -u <user> -p -e \"CREATE DATABASE IF NOT EXISTS two_factor_auth;\"",
        "mysql -u <user> -p two_factor_auth < database/migrations/001_create_two_factor.sql",
        "",
        "npm start          # production",
        "npm run dev        # developpement (rechargement auto)",
    ])
    d.para("En production, lancer le module via un gestionnaire de processus (pm2, systemd, Docker) "
           "avec redémarrage automatique.")

    d.heading("5. Configuration (.env)", 1)
    d.table(["Variable", "Oblig.", "Défaut", "Description"], [
        ["PORT", "non", "4000", "Port d'écoute du module."],
        ["DB_HOST", "non", "localhost", "Hôte MySQL."],
        ["DB_PORT", "non", "3306", "Port MySQL."],
        ["DB_USERNAME", "non", "root", "Utilisateur MySQL."],
        ["DB_PASSWORD", "non", "(vide)", "Mot de passe MySQL. S'il contient un #, l'encadrer de guillemets dans le .env."],
        ["DB_NAME", "non", "two_factor_auth", "Nom de la base."],
        ["JWT_SECRET", "OUI", "—", "Identique au secret JWT du site hôte. Le module refuse de démarrer sans."],
        ["ENCRYPTION_KEY", "OUI", "—", "Clé AES-256 : 32 octets hexadécimaux (64 caractères). openssl rand -hex 32."],
        ["TOTP_ISSUER", "non", "MyApp", "Nom affiché à côté du compte dans l'application d'authentification."],
        ["TOTP_WINDOW", "non", "1", "Tolérance : nombre de pas de 30 s acceptés avant / après l'instant courant."],
        ["RECOVERY_CODES_COUNT", "non", "10", "Nombre de codes de récupération générés à l'activation."],
    ], [2.1, 0.8, 1.4, 5])
    d.callout("ENCRYPTION_KEY est critique. Elle chiffre tous les secrets TOTP en base. La sauvegarder "
              "hors du serveur et ne jamais la modifier une fois en production : un changement rend tous "
              "les secrets illisibles et oblige chaque utilisateur à refaire l'activation.", "warn")
    d.para("Exemple de .env :")
    d.code([
        "PORT=4000",
        "DB_HOST=localhost",
        "DB_PORT=3306",
        "DB_USERNAME=app",
        "DB_PASSWORD=\"motdepasse\"",
        "DB_NAME=two_factor_auth",
        "JWT_SECRET=le-meme-secret-que-le-site-hote",
        "ENCRYPTION_KEY=3f9c1d...   (64 caracteres hexadecimaux)",
        "TOTP_ISSUER=MonSite",
        "TOTP_WINDOW=1",
        "RECOVERY_CODES_COUNT=10",
    ])

    d.heading("6. Base de données", 1)
    d.para("La migration database/migrations/001_create_two_factor.sql crée deux tables. Elles peuvent "
           "cohabiter avec les tables existantes du site hôte dans la même base.")
    d.table(["Table", "Colonnes", "Rôle"], [
        ["two_factor_secrets", "id, user_id (unique), secret_encrypted, enabled, created_at, updated_at",
         "Un enregistrement par utilisateur. Secret TOTP stocké chiffré (AES-256-GCM). enabled passe à vrai après /enable."],
        ["two_factor_recovery_codes", "id, user_id, code_hash, used_at, created_at",
         "Un enregistrement par code de récupération. Code haché (bcrypt). used_at renseigné à la consommation (usage unique)."],
    ], [1.4, 2.2, 3])
    d.para("user_id est un VARCHAR(64) : y placer l'identifiant utilisateur du site hôte, tel qu'il apparaît dans le JWT.")

    d.heading("7. Référence des endpoints", 1)
    d.para("Préfixe commun : /api/2fa. Toutes les requêtes exigent le header Authorization: Bearer <jwt>. "
           "Corps en JSON. Réponses : succès { \"success\": true, ... } ; erreur { \"success\": false, \"message\": \"...\" }.")
    d.heading("GET /api/2fa/status", 3)
    d.para("Indique si le 2FA est actif pour l'utilisateur. Aucun corps.")
    d.code(["200  { \"success\": true, \"enabled\": false }"])
    d.heading("POST /api/2fa/setup", 3)
    d.para("Génère (ou regénère) un secret TOTP et le QR code. Le 2FA n'est pas encore actif après cet appel.")
    d.code([
        "Corps   { \"accountName\": \"utilisateur@example.com\" }   // optionnel, sinon = user_id",
        "200     { \"success\": true,",
        "          \"secret\": \"LMWGKNKYJQRUCSJGEQYGKNCNF5FFORKH\",",
        "          \"qrCodeDataUrl\": \"data:image/png;base64,iVBORw0KGgo...\" }",
    ])
    d.para("qrCodeDataUrl est une image PNG encodée : l'injecter telle quelle dans <img src=\"...\">. "
           "secret peut être affiché pour une saisie manuelle dans l'application d'authentification.")
    d.heading("POST /api/2fa/enable", 3)
    d.para("Active le 2FA après vérification d'un premier code. Renvoie les codes de récupération.")
    d.code([
        "Corps   { \"token\": \"123456\" }",
        "200     { \"success\": true, \"recoveryCodes\": [\"E63E-EBAC\", \"C372-C18C\", ... 10 codes] }",
        "401     { \"success\": false, \"message\": \"Code invalide.\" }",
        "404     { \"success\": false, \"message\": \"Aucune configuration 2FA en attente pour cet utilisateur.\" }",
        "409     { \"success\": false, \"message\": \"Le 2FA est deja active.\" }",
    ])
    d.callout("Les recoveryCodes ne sont renvoyés qu'ici (et à la regénération). Ils ne sont jamais "
              "réaffichables ensuite. À présenter une seule fois à l'utilisateur.", "note")
    d.heading("POST /api/2fa/verify", 3)
    d.para("Vérifie un code au moment de la connexion. Accepte un code TOTP à 6 chiffres OU un code de "
           "récupération au format XXXX-XXXX. Rate limité.")
    d.code([
        "Corps   { \"token\": \"123456\" }              // ou \"E63E-EBAC\"",
        "200     { \"success\": true, \"method\": \"totp\" }",
        "200     { \"success\": true, \"method\": \"recovery_code\" }",
        "401     { \"success\": false, \"message\": \"Code invalide.\" }",
        "404     { \"success\": false, \"message\": \"Le 2FA n'est pas active pour cet utilisateur.\" }",
    ])
    d.heading("POST /api/2fa/disable", 3)
    d.para("Désactive le 2FA et supprime la configuration. Exige un code valide (TOTP ou récupération). Rate limité.")
    d.code(["Corps   { \"token\": \"123456\" }", "200     { \"success\": true }",
            "401     { \"success\": false, \"message\": \"Code invalide.\" }"])
    d.heading("POST /api/2fa/recovery-codes/regenerate", 3)
    d.para("Invalide les anciens codes de récupération et en génère de nouveaux. Exige un code valide. Rate limité.")
    d.code(["Corps   { \"token\": \"123456\" }",
            "200     { \"success\": true, \"recoveryCodes\": [ ... 10 nouveaux codes ] }"])
    d.heading("Rate limiting", 3)
    d.para("/verify, /disable et /recovery-codes/regenerate sont limités à 5 requêtes par 15 minutes et "
           "par utilisateur. Au-delà :")
    d.code(["429  { \"success\": false, \"message\": \"Trop de tentatives, reessayez plus tard.\" }"])

    d.heading("8. Parcours d'intégration côté site hôte", 1)
    d.para("Tous les appels ci-dessous sont faits par le backend du site hôte, en transmettant le JWT de l'utilisateur courant.")
    d.heading("8.1 Activation du 2FA (utilisateur déjà connecté)", 3)
    d.bullets([
        "Backend hôte -> POST /api/2fa/setup. Récupère qrCodeDataUrl (et secret).",
        "Le site affiche le QR code (<img src=\"{qrCodeDataUrl}\">), plus le secret en clair pour la saisie manuelle.",
        "L'utilisateur scanne dans Google Authenticator, lit le code à 6 chiffres et le saisit sur le site.",
        "Backend hôte -> POST /api/2fa/enable avec { token }. Récupère recoveryCodes.",
        "Le site affiche les codes de récupération une seule fois et invite à les sauvegarder."], ordered=True)
    d.code([
        "// Exemple Node.js (backend du site hote)",
        "const BASE = 'https://2fa.interne.monsite';",
        "",
        "async function startSetup(userJwt) {",
        "  const r = await fetch(`${BASE}/api/2fa/setup`, {",
        "    method: 'POST',",
        "    headers: { 'Authorization': `Bearer ${userJwt}`, 'Content-Type': 'application/json' },",
        "    body: JSON.stringify({ accountName: 'utilisateur@example.com' }),",
        "  });",
        "  return r.json();  // { secret, qrCodeDataUrl }",
        "}",
        "",
        "async function confirmSetup(userJwt, code) {",
        "  const r = await fetch(`${BASE}/api/2fa/enable`, {",
        "    method: 'POST',",
        "    headers: { 'Authorization': `Bearer ${userJwt}`, 'Content-Type': 'application/json' },",
        "    body: JSON.stringify({ token: code }),",
        "  });",
        "  if (!r.ok) throw new Error('Code invalide');",
        "  return r.json();  // { recoveryCodes: [...] }",
        "}",
    ])
    d.heading("8.2 Connexion avec 2FA", 3)
    d.bullets([
        "L'utilisateur saisit identifiant + mot de passe. Le site hôte les vérifie comme d'habitude.",
        "Avant d'ouvrir la session : GET /api/2fa/status. enabled:false -> connexion normale ; enabled:true -> demander le code.",
        "POST /api/2fa/verify avec { token } (code TOTP ou code de récupération). 200 -> ouvrir la session ; 401 -> refuser."], ordered=True)
    d.code([
        "// Exemple Node.js - apres validation du mot de passe",
        "async function loginSecondFactor(userJwt, code) {",
        "  const status = await fetch(`${BASE}/api/2fa/status`, {",
        "    headers: { 'Authorization': `Bearer ${userJwt}` },",
        "  }).then(r => r.json());",
        "",
        "  if (!status.enabled) return { ok: true };          // pas de 2FA",
        "",
        "  const r = await fetch(`${BASE}/api/2fa/verify`, {",
        "    method: 'POST',",
        "    headers: { 'Authorization': `Bearer ${userJwt}`, 'Content-Type': 'application/json' },",
        "    body: JSON.stringify({ token: code }),",
        "  });",
        "  return { ok: r.ok };                               // true => ouvrir la session",
        "}",
    ])
    d.heading("8.3 Désactivation", 3)
    d.para("Backend hôte -> POST /api/2fa/disable avec { token } (un code valide est exigé pour éviter une désactivation non consentie).")
    d.heading("8.4 Régénération des codes de récupération", 3)
    d.para("Backend hôte -> POST /api/2fa/recovery-codes/regenerate avec { token }. Les anciens codes "
           "cessent immédiatement de fonctionner. Afficher les nouveaux une seule fois.")

    d.heading("9. Sécurité — points impératifs", 1)
    d.bullets([
        "HTTPS entre le backend hôte et le module : le JWT et les codes y transitent.",
        "Ne pas exposer le module sur Internet. Le placer sur le réseau interne, joignable uniquement par le backend du site hôte.",
        "ENCRYPTION_KEY : secrète, sauvegardée hors serveur, jamais modifiée après mise en production.",
        "JWT_SECRET : strictement identique à celui du site hôte, stocké de façon sécurisée.",
        "Codes de récupération : hachés en base, non réaffichables. Présentés une seule fois.",
        "Rate limiting : déjà actif sur les vérifications (5 / 15 min / utilisateur). Ne pas le contourner côté hôte.",
        "Sauvegarde régulière des tables two_factor_secrets et two_factor_recovery_codes.",
        "Horloge serveur synchronisée (NTP) : le TOTP repose sur l'heure."])

    d.heading("10. Codes d'erreur", 1)
    d.table(["HTTP", "Message", "Cause probable"], [
        ["401", "Authentification requise.", "Header Authorization absent ou mal formé."],
        ["401", "Token invalide ou expiré.", "JWT invalide - le plus souvent JWT_SECRET différent de celui du site hôte, ou JWT expiré."],
        ["401", "Le token ne contient pas d'identifiant utilisateur.", "Payload JWT sans sub / userId / id."],
        ["401", "Code invalide.", "Code TOTP faux/expiré, ou code de récupération inconnu / déjà utilisé."],
        ["400", "Le champ token est requis.", "Corps JSON sans token."],
        ["404", "Aucune configuration 2FA en attente...", "/enable appelé sans /setup préalable."],
        ["404", "Le 2FA n'est pas activé pour cet utilisateur.", "/verify ou /disable alors que le 2FA n'est pas actif."],
        ["409", "Le 2FA est déjà activé.", "/enable alors qu'il l'est déjà."],
        ["429", "Trop de tentatives, réessayez plus tard.", "Rate limit atteint (5 / 15 min / utilisateur)."],
        ["500", "Erreur interne du serveur.", "Base injoignable, identifiants DB_* incorrects, ou ENCRYPTION_KEY mal formée."],
        ["404", "Route introuvable.", "URL hors du préfixe /api/2fa."],
    ], [0.7, 2.6, 3.4])

    d.heading("11. Tests et outils fournis", 1)
    d.bullets([
        "Tests unitaires : npm test (13 tests, sans base de données requise).",
        "Collection Postman — parcours pas à pas : 2fa-sequence-activation-verification.postman_collection.json. "
        "6 requêtes numérotées (statut -> setup -> enable -> statut -> verify -> verify par code de récupération). "
        "Le code à 6 chiffres est saisi à la main, comme un vrai utilisateur.",
        "Collection Postman — suite automatisée : 2fa-google-authenticator.postman_collection.json. "
        "Le JWT et le code TOTP sont calculés par les scripts de la collection ; exécutable avec newman run <fichier>."])
    d.para("Note : /verify, /disable et /regenerate étant limités à 5 appels / 15 min / utilisateur, un run "
           "complet de la collection automatisée consomme le quota. Pour rejouer dans la foulée, changer la "
           "variable userId de la collection.", size=9, color=(0.4,0.4,0.4))

    d.heading("12. Checklist de mise en production", 1)
    d.bullets([
        "Node.js >= 18 installé sur le serveur cible.",
        "Base MySQL créée et migration 001_create_two_factor.sql jouée.",
        ".env renseigné.",
        "JWT_SECRET identique à celui du site hôte (vérifié).",
        "ENCRYPTION_KEY générée (openssl rand -hex 32) et sauvegardée hors serveur.",
        "TOTP_ISSUER = nom de la marque (visible dans l'application d'authentification).",
        "Module lancé via pm2 / systemd / Docker avec redémarrage automatique.",
        "Module joignable uniquement depuis le backend du site hôte (réseau interne / firewall).",
        "HTTPS en place (reverse proxy si nécessaire).",
        "Sauvegarde planifiée des tables two_factor_*.",
        "Horloge serveur synchronisée (NTP).",
        "Parcours activation puis connexion validés en recette."])

    d.heading("13. Dépannage rapide", 1)
    d.table(["Symptôme", "Piste"], [
        ["401 sur tous les appels, JWT pourtant valide côté site hôte",
         "JWT_SECRET du module différent de celui du site hôte ; ou JWT expiré ; ou identifiant utilisateur absent du payload (sub / userId / id)."],
        ["500 systématique",
         "Voir les logs : Access denied ou ECONNREFUSED -> DB_* incorrects ; message sur ENCRYPTION_KEY -> elle doit faire 64 caractères hexadécimaux."],
        ["Le mot de passe MySQL contient # et la connexion échoue",
         "Encadrer la valeur de guillemets dans le .env : DB_PASSWORD=\"mot#depasse\"."],
        ["Le QR code ne s'affiche pas",
         "qrCodeDataUrl est déjà une image complète (data:image/png;base64,...) : la mettre telle quelle dans src d'une balise <img>, sans la retraiter."],
        ["« Code invalide » alors que le code affiché semble correct",
         "Horloge du serveur désynchronisée : activer NTP. En dépannage, augmenter TOTP_WINDOW à 2."],
        ["429 « Trop de tentatives »",
         "Rate limit atteint : attendre 15 minutes, ou réduire le nombre de tentatives côté site hôte."],
        ["Après /enable, l'utilisateur n'a pas noté ses codes de récupération",
         "Appeler /recovery-codes/regenerate (code valide requis) et réafficher les nouveaux codes une seule fois."],
    ], [2.2, 4])

    d.para(" ")
    d.para("Fin du document — Module 2FA v1.0.0 — 31 août 2026.", size=9, color=(0.4,0.4,0.4))

    data = d.build()
    with open(out_path, "wb") as f:
        f.write(data)
    print("PDF ecrit :", out_path, "-", len(data), "octets,", d.page_no, "pages")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "guide.pdf")
