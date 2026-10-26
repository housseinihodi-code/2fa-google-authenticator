const crypto = require('crypto');
const bcrypt = require('bcrypt');
const config = require('../config/env');
const model = require('../models/twoFactor.model');

const SALT_ROUNDS = 10;

function formatCode(raw) {
  return `${raw.slice(0, 4)}-${raw.slice(4, 8)}`.toUpperCase();
}

function generatePlainCodes(count = config.recoveryCodesCount) {
  const codes = [];
  for (let i = 0; i < count; i += 1) {
    const raw = crypto.randomBytes(4).toString('hex');
    codes.push(formatCode(raw));
  }
  return codes;
}

async function generateAndStore(userId) {
  const plainCodes = generatePlainCodes();
  const hashedCodes = await Promise.all(plainCodes.map((code) => bcrypt.hash(code, SALT_ROUNDS)));
  await model.replaceRecoveryCodes(userId, hashedCodes);
  return plainCodes;
}

async function verifyAndConsume(userId, submittedCode) {
  const unused = await model.getUnusedRecoveryCodes(userId);
  for (const entry of unused) {
    const matches = await bcrypt.compare(submittedCode.toUpperCase(), entry.code_hash);
    if (matches) {
      await model.markRecoveryCodeUsed(entry.id);
      return true;
    }
  }
  return false;
}

module.exports = { generateAndStore, verifyAndConsume };
