jest.mock('../src/models/twoFactor.model');

const model = require('../src/models/twoFactor.model');
const recoveryCodeService = require('../src/services/recoveryCode.service');

describe('recoveryCode.service', () => {
  const userId = 'user-1';
  let storedHashes = [];

  beforeEach(() => {
    storedHashes = [];
    model.replaceRecoveryCodes.mockImplementation(async (id, hashes) => {
      storedHashes = hashes.map((code_hash, idx) => ({ id: idx, code_hash, used_at: null }));
    });
    model.getUnusedRecoveryCodes.mockImplementation(async () => storedHashes.filter((c) => !c.used_at));
    model.markRecoveryCodeUsed.mockImplementation(async (id) => {
      const entry = storedHashes.find((c) => c.id === id);
      if (entry) entry.used_at = new Date();
    });
  });

  it('génère des codes de récupération au format XXXX-XXXX', async () => {
    const codes = await recoveryCodeService.generateAndStore(userId);
    expect(codes.length).toBeGreaterThan(0);
    codes.forEach((code) => expect(code).toMatch(/^[0-9A-F]{4}-[0-9A-F]{4}$/));
  });

  it('valide un code existant puis le consomme (usage unique)', async () => {
    const [code] = await recoveryCodeService.generateAndStore(userId);

    const firstAttempt = await recoveryCodeService.verifyAndConsume(userId, code);
    expect(firstAttempt).toBe(true);

    const secondAttempt = await recoveryCodeService.verifyAndConsume(userId, code);
    expect(secondAttempt).toBe(false);
  });

  it('rejette un code inconnu', async () => {
    await recoveryCodeService.generateAndStore(userId);
    const result = await recoveryCodeService.verifyAndConsume(userId, 'FFFF-FFFF');
    expect(result).toBe(false);
  });
});
