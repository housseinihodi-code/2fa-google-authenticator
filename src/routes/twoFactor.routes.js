const express = require('express');
const controller = require('../controllers/twoFactor.controller');
const authMiddleware = require('../middleware/auth.middleware');
const { verifyRateLimiter } = require('../middleware/rateLimit.middleware');

const router = express.Router();

router.use(authMiddleware);

router.get('/status', controller.status);
router.post('/setup', controller.setup);
router.post('/enable', controller.enable);
router.post('/verify', verifyRateLimiter, controller.verify);
router.post('/disable', verifyRateLimiter, controller.disable);
router.post('/recovery-codes/regenerate', verifyRateLimiter, controller.regenerateRecoveryCodes);

module.exports = router;
