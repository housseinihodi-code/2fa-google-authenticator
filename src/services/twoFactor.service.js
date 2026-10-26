const totpService = require('./totp.service');
const qrCodeService = require('./qrCode.service');
const recoveryCodeService = require('./recoveryCode.service');
const model = require('../models/twoFactor.model');
const { encrypt, decrypt } = require('../utils/encryption');

class TwoFactorError extends Error {
  constructor(message, status = 400) {
    super(message);
    this.status = status;
  }
}

async function setup(userId, accountName) {
  const secret = totpService.generateSecret(accountName);
  await model.upsertSecret(userId, encrypt(secret.base32));
  const qrCodeDataUrl = await qrCodeService.generateQrCodeDataUrl(secret.otpauth_url);
  return { secret: secret.base32, qrCodeDataUrl };
}

async function enable(userId, token) {
  const record = await model.findByUserId(userId);
  if (!record) throw new TwoFactorError("Aucune configuration 2FA en attente pour cet utilisateur.", 404);
  if (record.enabled) throw new TwoFactorError('Le 2FA est déjà activé.', 409);

  const secret = decrypt(record.secret_encrypted);
  if (!totpService.verifyToken(secret, token)) {
    throw new TwoFactorError('Code invalide.', 401);
  }

  await model.setEnabled(userId, true);
  const recoveryCodes = await recoveryCodeService.generateAndStore(userId);
  return { recoveryCodes };
}

async function verify(userId, token) {
  const record = await model.findByUserId(userId);
  if (!record || !record.enabled) {
    throw new TwoFactorError("Le 2FA n'est pas activé pour cet utilisateur.", 404);
  }

  const secret = decrypt(record.secret_encrypted);
  if (totpService.verifyToken(secret, token)) {
    return { method: 'totp' };
  }

  const recoveryValid = await recoveryCodeService.verifyAndConsume(userId, token);
  if (recoveryValid) {
    return { method: 'recovery_code' };
  }

  throw new TwoFactorError('Code invalide.', 401);
}

async function disable(userId, token) {
  await verify(userId, token);
  await model.deleteByUserId(userId);
  return {};
}

async function regenerateRecoveryCodes(userId, token) {
  await verify(userId, token);
  const recoveryCodes = await recoveryCodeService.generateAndStore(userId);
  return { recoveryCodes };
}

async function getStatus(userId) {
  const record = await model.findByUserId(userId);
  return { enabled: Boolean(record && record.enabled) };
}

module.exports = {
  TwoFactorError,
  setup,
  enable,
  verify,
  disable,
  regenerateRecoveryCodes,
  getStatus,
};
