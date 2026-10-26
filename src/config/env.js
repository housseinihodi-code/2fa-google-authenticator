require('dotenv').config();

function required(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Variable d'environnement manquante : ${name}`);
  }
  return value;
}

module.exports = {
  port: parseInt(process.env.PORT || '4000', 10),

  db: {
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '3306', 10),
    user: process.env.DB_USERNAME || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'two_factor_auth',
  },

  jwtSecret: required('JWT_SECRET'),
  encryptionKey: required('ENCRYPTION_KEY'),

  totpIssuer: process.env.TOTP_ISSUER || 'MyApp',
  totpWindow: parseInt(process.env.TOTP_WINDOW || '1', 10),
  recoveryCodesCount: parseInt(process.env.RECOVERY_CODES_COUNT || '10', 10),
};
