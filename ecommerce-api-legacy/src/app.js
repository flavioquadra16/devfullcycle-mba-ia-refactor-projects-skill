const express = require('express');
const { config } = require('./config/settings');
const { initDb } = require('./database');
const { registerRoutes } = require('./views/routes');
const { errorHandler } = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

async function bootstrap() {
    await initDb();
    registerRoutes(app);
    app.use(errorHandler);
    return app;
}

if (require.main === module) {
    bootstrap()
        .then(() => {
            app.listen(config.port, () => {
                console.log(`LMS API rodando na porta ${config.port}...`);
            });
        })
        .catch((err) => {
            console.error(err);
            process.exit(1);
        });
}

module.exports = { app, bootstrap };
