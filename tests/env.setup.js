process.env.JWT_SECRET = process.env.JWT_SECRET || 'test-jwt-secret';
process.env.ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || '0'.repeat(64);
process.env.DB_NAME = process.env.DB_NAME || 'two_factor_auth_test';
