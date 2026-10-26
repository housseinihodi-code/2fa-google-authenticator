jest.mock('../src/models/twoFactor.model');
jest.mock('../src/services/totp.service');
jest.mock('../src/services/qrCode.service');
jest.mock('../src/services/recoveryCode.service');

const model = require('../src/models/twoFactor.model');
const totpService = require('../src/services/totp.service');
const qrCodeService = require('../src/services/qrCode.service');
const recoveryCodeService = require('../src/services/recoveryCode.service');
const { encrypt } = require('../src/utils/encryption');
const twoFactorService = require('../src/services/twoFactor.service');

describe('twoFactor.service', () => {
  const userId = 'user-1';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('setup : crée un secret et retourne un QR code', async () => {
    totpService.generateSecret.mockReturnValue({ base32: 'BASE32SECRET', otpauth_url: 'otpauth://totp/x' });
    qrCodeService.generateQrCodeDataUrl.mockResolvedValue('data:image/png;base64,xxx');

    const result = await twoFactorService.setup(userId, 'user@example.com');

    expect(model.upsertSecret).toHaveBeenCalledWith(userId, expect.any(String));
    expect(result.secret).toBe('BASE32SECRET');
    expect(result.qrCodeDataUrl).toContain('data:image');
  });

  it('enable : refuse si aucune configuration en attente', async () => {
    model.findByUserId.mockResolvedValue(null);
    await expect(twoFactorService.enable(userId, '123456')).rejects.toThrow(twoFactorService.TwoFactorError);
  });

  it('enable : active le 2FA et retourne des codes de récupération si le token est valide', async () => {
    model.findByUserId.mockResolvedValue({ enabled: false, secret_encrypted: encrypt('BASE32SECRET') });
    totpService.verifyToken.mockReturnValue(true);
    recoveryCodeService.generateAndStore.mockResolvedValue(['AAAA-BBBB']);

    const result = await twoFactorService.enable(userId, '123456');

    expect(model.setEnabled).toHaveBeenCalledWith(userId, true);
    expect(result.recoveryCodes).toEqual(['AAAA-BBBB']);
  });

  it('verify : accepte un code TOTP valide', async () => {
    model.findByUserId.mockResolvedValue({ enabled: true, secret_encrypted: encrypt('BASE32SECRET') });
    totpService.verifyToken.mockReturnValue(true);

    const result = await twoFactorService.verify(userId, '123456');
    expect(result.method).toBe('totp');
  });

  it('verify : retombe sur un code de récupération si le TOTP échoue', async () => {
    model.findByUserId.mockResolvedValue({ enabled: true, secret_encrypted: encrypt('BASE32SECRET') });
    totpService.verifyToken.mockReturnValue(false);
    recoveryCodeService.verifyAndConsume.mockResolvedValue(true);

    const result = await twoFactorService.verify(userId, 'AAAA-BBBB');
    expect(result.method).toBe('recovery_code');
  });

  it("verify : rejette si ni le TOTP ni le code de récupération ne correspondent", async () => {
    model.findByUserId.mockResolvedValue({ enabled: true, secret_encrypted: encrypt('BASE32SECRET') });
    totpService.verifyToken.mockReturnValue(false);
    recoveryCodeService.verifyAndConsume.mockResolvedValue(false);

    await expect(twoFactorService.verify(userId, '000000')).rejects.toThrow(twoFactorService.TwoFactorError);
  });

  it('status : reflète l’état enabled stocké en base', async () => {
    model.findByUserId.mockResolvedValue({ enabled: true });
    const result = await twoFactorService.getStatus(userId);
    expect(result.enabled).toBe(true);
  });
});
