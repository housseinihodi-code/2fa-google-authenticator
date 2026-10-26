const speakeasy = require('speakeasy');
const config = require('../config/env');

function generateSecret(accountName) {
  return speakeasy.generateSecret({
    name: `${config.totpIssuer}:${accountName}`,
    issuer: config.totpIssuer,
    length: 20,
  });
}

function verifyToken(base32Secret, token) {
  return speakeasy.totp.verify({
    secret: base32Secret,
    encoding: 'base32',
    token,
    window: config.totpWindow,
  });
}

module.exports = { generateSecret, verifyToken };
