const { get, run } = require('../database');

async function findUserByEmail(db, email) {
    return get(db, 'SELECT id FROM users WHERE email = ?', [email]);
}

async function createUser(db, name, email, passwordHash) {
    return run(db, 'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
}

module.exports = { findUserByEmail, createUser };
