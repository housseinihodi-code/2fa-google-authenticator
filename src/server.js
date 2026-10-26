const app = require('./app');
const config = require('./config/env');

app.listen(config.port, () => {
  console.log(`Module 2FA à l'écoute sur le port ${config.port}`);
});
