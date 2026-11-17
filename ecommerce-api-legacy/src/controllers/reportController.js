const { getDb } = require('../database');
const { financialReport } = require('../models/enrollmentModel');

async function report(req, res) {
    try {
        const data = await financialReport(getDb());
        return res.json(data);
    } catch (err) {
        return res.status(500).send('Erro DB');
    }
}

module.exports = { report };
