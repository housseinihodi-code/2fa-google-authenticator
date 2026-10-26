const express = require('express');
const cors = require('cors');
const twoFactorRoutes = require('./routes/twoFactor.routes');

const app = express();

app.use(cors());
app.use(express.json());

app.use('/api/2fa', twoFactorRoutes);

app.use((req, res) => {
  res.status(404).json({ success: false, message: 'Route introuvable.' });
});

module.exports = app;
