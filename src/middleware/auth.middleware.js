const jwt = require('jsonwebtoken');
const config = require('../config/env');
const { error } = require('../utils/response');

// Le module ne gère pas la connexion : il fait confiance au JWT déjà émis par
// l'application hôte (même JWT_SECRET) pour identifier l'utilisateur courant.
module.exports = function authMiddleware(req, res, next) {
  const header = req.headers.authorization || '';
  const [scheme, token] = header.split(' ');

  if (scheme !== 'Bearer' || !token) {
    return error(res, 'Authentification requise.', 401);
  }

  try {
    const payload = jwt.verify(token, config.jwtSecret);
    const userId = payload.sub || payload.userId || payload.id;
    if (!userId) {
      return error(res, "Le token ne contient pas d'identifiant utilisateur.", 401);
    }
    req.userId = String(userId);
    next();
  } catch (err) {
    return error(res, 'Token invalide ou expiré.', 401);
  }
};
