const QRCode = require('qrcode');

async function generateQrCodeDataUrl(otpAuthUrl) {
  return QRCode.toDataURL(otpAuthUrl);
}

module.exports = { generateQrCodeDataUrl };
