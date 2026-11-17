const { getDb } = require('../database');
const { deleteUser } = require('../models/enrollmentModel');

async function remove(req, res) {
    try {
        await deleteUser(getDb(), req.params.id);
        return res.send('Usuário deletado');
    } catch (err) {
        return res.status(500).send('Erro DB');
    }
}

module.exports = { remove };
