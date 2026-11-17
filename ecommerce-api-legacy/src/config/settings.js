const fs = require('fs');
const path = require('path');

function loadEnvFile(filePath) {
    if (!fs.existsSync(filePath)) return;
    const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/);
    for (const raw of lines) {
        const line = raw.trim();
        if (!line || line.startsWith('#') || !line.includes('=')) continue;
        const index = line.indexOf('=');
        const key = line.slice(0, index).trim();
        const value = line.slice(index + 1).trim().replace(/^['"]|['"]$/g, '');
        if (process.env[key] === undefined) process.env[key] = value;
    }
}

const root = path.join(__dirname, '..', '..');
loadEnvFile(path.join(root, '.env'));
loadEnvFile(path.join(root, '.env.example'));

const config = {
    port: Number(process.env.PORT || 3000),
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
    dbUser: process.env.DB_USER || '',
    dbPass: process.env.DB_PASS || '',
};

module.exports = { config };
