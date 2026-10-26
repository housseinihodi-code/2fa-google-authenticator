# 2FA Google Authenticator — module d'intégration

Module d'authentification à double facteur (TOTP, compatible Google Authenticator)
sous forme d'API REST Node.js/Express, indépendant de tout frontend. Il s'intègre à
n'importe quelle application en réutilisant le JWT déjà émis par celle-ci pour
identifier l'utilisateur.

## Fonctionnalités

- Génération d'un secret TOTP et d'un QR code à scanner dans Google Authenticator
- Activation / désactivation du 2FA
- Vérification d'un code à 6 chiffres (login)
- Codes de récupération (usage unique) en cas de perte du téléphone
- Secrets chiffrés en base (AES-256-GCM) et codes de récupération hashés (bcrypt)
- Rate limiting sur les tentatives de vérification

## Installation

```bash
cd 2fa-google-authenticator
npm install
cp .env.example .env
```

Renseignez dans `.env` :

- `JWT_SECRET` : **le même secret** que celui utilisé par l'application hôte pour
  signer ses JWT (le module ne fait que vérifier les tokens, il ne gère pas la
  connexion).
- `ENCRYPTION_KEY` : une clé aléatoire de 32 octets (`openssl rand -hex 32`).
- `DB_*` : accès à une base MySQL (dédiée ou partagée).

Exécutez la migration SQL fournie sur votre base :

```bash
mysql -u root -p your_database < database/migrations/001_create_two_factor.sql
```

Démarrez le module :

```bash
npm start        # production
npm run dev      # avec rechargement automatique
```

## Intégration côté application hôte

Le module attend un header `Authorization: Bearer <jwt>` sur chaque requête. Le
payload du JWT doit contenir l'identifiant utilisateur dans `sub`, `userId` ou `id`.

### Flux d'activation

1. `POST /api/2fa/setup` → renvoie `{ secret, qrCodeDataUrl }`. Affichez le QR code
   à l'utilisateur pour qu'il le scanne avec Google Authenticator.
2. `POST /api/2fa/enable` avec `{ "token": "123456" }` (code affiché par l'app) →
   active le 2FA et renvoie `{ recoveryCodes: [...] }`. **Affichez ces codes une
   seule fois** et invitez l'utilisateur à les sauvegarder.

### Flux de connexion (une fois activé)

- `GET /api/2fa/status` → `{ enabled: true|false }`
- `POST /api/2fa/verify` avec `{ "token": "123456" }` (code TOTP ou un code de
  récupération au format `XXXX-XXXX`) → `{ method: "totp" | "recovery_code" }`
  si valide, sinon 401.

### Autres actions

- `POST /api/2fa/disable` avec `{ "token": "..." }` → désactive le 2FA (nécessite
  un code valide).
- `POST /api/2fa/recovery-codes/regenerate` avec `{ "token": "..." }` → invalide les
  anciens codes et en génère de nouveaux.

## Endpoints — résumé

| Méthode | Route | Body | Description |
|---|---|---|---|
| GET | `/api/2fa/status` | — | État d'activation |
| POST | `/api/2fa/setup` | `{ accountName? }` | Génère secret + QR code |
| POST | `/api/2fa/enable` | `{ token }` | Active le 2FA |
| POST | `/api/2fa/verify` | `{ token }` | Vérifie un code (login) |
| POST | `/api/2fa/disable` | `{ token }` | Désactive le 2FA |
| POST | `/api/2fa/recovery-codes/regenerate` | `{ token }` | Régénère les codes de secours |

## Tests

```bash
npm test
```
# conecteur_2FA_DC
