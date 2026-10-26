const db = require('../config/database');

async function findByUserId(userId) {
  const [rows] = await db.query(
    'SELECT * FROM two_factor_secrets WHERE user_id = ? LIMIT 1',
    [userId]
  );
  return rows[0] || null;
}

async function upsertSecret(userId, encryptedSecret) {
  await db.query(
    `INSERT INTO two_factor_secrets (user_id, secret_encrypted, enabled)
     VALUES (?, ?, false)
     ON DUPLICATE KEY UPDATE secret_encrypted = VALUES(secret_encrypted), enabled = false`,
    [userId, encryptedSecret]
  );
}

async function setEnabled(userId, enabled) {
  await db.query('UPDATE two_factor_secrets SET enabled = ? WHERE user_id = ?', [enabled, userId]);
}

async function deleteByUserId(userId) {
  await db.query('DELETE FROM two_factor_secrets WHERE user_id = ?', [userId]);
  await db.query('DELETE FROM two_factor_recovery_codes WHERE user_id = ?', [userId]);
}

async function replaceRecoveryCodes(userId, hashedCodes) {
  await db.query('DELETE FROM two_factor_recovery_codes WHERE user_id = ?', [userId]);
  if (hashedCodes.length === 0) return;
  const values = hashedCodes.map((hash) => [userId, hash]);
  await db.query('INSERT INTO two_factor_recovery_codes (user_id, code_hash) VALUES ?', [values]);
}

async function getUnusedRecoveryCodes(userId) {
  const [rows] = await db.query(
    'SELECT * FROM two_factor_recovery_codes WHERE user_id = ? AND used_at IS NULL',
    [userId]
  );
  return rows;
}

async function markRecoveryCodeUsed(id) {
  await db.query('UPDATE two_factor_recovery_codes SET used_at = NOW() WHERE id = ?', [id]);
}

module.exports = {
  findByUserId,
  upsertSecret,
  setEnabled,
  deleteByUserId,
  replaceRecoveryCodes,
  getUnusedRecoveryCodes,
  markRecoveryCodeUsed,
};
