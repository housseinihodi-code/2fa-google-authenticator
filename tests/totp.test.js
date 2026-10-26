const speakeasy = require('speakeasy');
const totpService = require('../src/services/totp.service');

describe('totp.service', () => {
  it('génère un secret avec une URL otpauth exploitable par Google Authenticator', () => {
    const secret = totpService.generateSecret('user@example.com');
    expect(secret.base32).toBeTruthy();
    expect(secret.otpauth_url).toContain('otpauth://totp/');
  });

  it('valide un code TOTP généré à partir du même secret', () => {
    const secret = totpService.generateSecret('user@example.com');
    const token = speakeasy.totp({ secret: secret.base32, encoding: 'base32' });
    expect(totpService.verifyToken(secret.base32, token)).toBe(true);
  });

  it('rejette un code invalide', () => {
    const secret = totpService.generateSecret('user@example.com');
    expect(totpService.verifyToken(secret.base32, '000000')).toBe(false);
  });
});
