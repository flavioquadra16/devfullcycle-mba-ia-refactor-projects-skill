const sqlite3 = require('sqlite3');
const { hashPassword } = require('./services/passwordService');

let database;

function run(db, sql, params = []) {
    return new Promise((resolve, reject) => {
        db.run(sql, params, function onRun(err) {
            if (err) reject(err);
            else resolve(this);
        });
    });
}

function get(db, sql, params = []) {
    return new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    });
}

function all(db, sql, params = []) {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    });
}

function openDatabase() {
    return new Promise((resolve, reject) => {
        const instance = new sqlite3.Database(':memory:', (err) => {
            if (err) reject(err);
            else resolve(instance);
        });
    });
}

async function initDb() {
    database = await openDatabase();
    await run(database, 'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
    await run(database, 'CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
    await run(database, 'CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
    await run(database, 'CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
    await run(database, 'CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');
    await run(
        database,
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        ['Leonan', 'leonan@fullcycle.com.br', hashPassword('123')]
    );
    await run(
        database,
        "INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)"
    );
    await run(database, 'INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
    await run(database, "INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
    return database;
}

function getDb() {
    if (!database) throw new Error('Database not initialized');
    return database;
}

module.exports = { initDb, getDb, run, get, all };
