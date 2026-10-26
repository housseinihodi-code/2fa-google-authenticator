const twoFactorService = require('../services/twoFactor.service');
const { success, error } = require('../utils/response');

function handleServiceError(res, err) {
  if (err instanceof twoFactorService.TwoFactorError) {
    return error(res, err.message, err.status);
  }
  console.error(err);
  return error(res, 'Erreur interne du serveur.', 500);
}

async function setup(req, res) {
  try {
    const accountName = req.body.accountName || req.userId;
    const data = await twoFactorService.setup(req.userId, accountName);
    return success(res, data);
  } catch (err) {
    return handleServiceError(res, err);
  }
}

async function enable(req, res) {
  try {
    const { token } = req.body;
    if (!token) return error(res, 'Le champ token est requis.');
    const data = await twoFactorService.enable(req.userId, token);
    return success(res, data);
  } catch (err) {
    return handleServiceError(res, err);
  }
}

async function verify(req, res) {
  try {
    const { token } = req.body;
    if (!token) return error(res, 'Le champ token est requis.');
    const data = await twoFactorService.verify(req.userId, token);
    return success(res, data);
  } catch (err) {
    return handleServiceError(res, err);
  }
}

async function disable(req, res) {
  try {
    const { token } = req.body;
    if (!token) return error(res, 'Le champ token est requis.');
    await twoFactorService.disable(req.userId, token);
    return success(res, {});
  } catch (err) {
    return handleServiceError(res, err);
  }
}

async function regenerateRecoveryCodes(req, res) {
  try {
    const { token } = req.body;
    if (!token) return error(res, 'Le champ token est requis.');
    const data = await twoFactorService.regenerateRecoveryCodes(req.userId, token);
    return success(res, data);
  } catch (err) {
    return handleServiceError(res, err);
  }
}

async function status(req, res) {
  try {
    const data = await twoFactorService.getStatus(req.userId);
    return success(res, data);
  } catch (err) {
    return handleServiceError(res, err);
  }
}

module.exports = { setup, enable, verify, disable, regenerateRecoveryCodes, status };
