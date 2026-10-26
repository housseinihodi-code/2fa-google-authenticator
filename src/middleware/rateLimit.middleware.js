const rateLimit = require('express-rate-limit');

// Freine le brute-force sur la vérification de code (TOTP / recovery code).
const verifyRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 5,
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.userId || req.ip,
  message: { success: false, message: 'Trop de tentatives, réessayez plus tard.' },
});

module.exports = { verifyRateLimiter };
