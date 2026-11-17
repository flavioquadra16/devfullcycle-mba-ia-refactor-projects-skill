const { getDb, run } = require('../database');
const { findUserByEmail, createUser } = require('../models/userModel');
const { findActiveCourse } = require('../models/courseModel');
const { createEnrollment, createPayment, writeAudit } = require('../models/enrollmentModel');
const { hashPassword } = require('../services/passwordService');
const { charge } = require('../services/paymentService');

async function checkout(req, res) {
    const name = req.body.usr;
    const email = req.body.eml;
    const password = req.body.pwd;
    const courseId = req.body.c_id;
    const card = req.body.card;

    if (!name || !email || !courseId || !card) {
        return res.status(400).send('Bad Request');
    }

    const db = getDb();
    let course;
    try {
        course = await findActiveCourse(db, courseId);
    } catch (err) {
        return res.status(500).send('Erro DB');
    }
    if (!course) return res.status(404).send('Curso não encontrado');

    let user;
    try {
        user = await findUserByEmail(db, email);
    } catch (err) {
        return res.status(500).send('Erro DB');
    }

    let userId;
    if (!user) {
        try {
            const created = await createUser(db, name, email, hashPassword(password || '123456'));
            userId = created.lastID;
        } catch (err) {
            return res.status(500).send('Erro ao criar usuário');
        }
    } else {
        userId = user.id;
    }

    if (charge(card) === 'DENIED') {
        return res.status(400).send('Pagamento recusado');
    }

    await run(db, 'BEGIN');
    try {
        const enrollment = await createEnrollment(db, userId, courseId);
        await createPayment(db, enrollment.lastID, course.price, 'PAID');
        await writeAudit(db, `Checkout curso ${courseId} por ${userId}`);
        await run(db, 'COMMIT');
        console.log(`[LOG] Checkout concluído para usuário ${userId}: ${course.title}`);
        return res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollment.lastID });
    } catch (err) {
        try {
            await run(db, 'ROLLBACK');
        } catch (rollbackErr) {
            console.error(rollbackErr);
        }
        return res.status(500).send('Erro Matrícula');
    }
}

module.exports = { checkout };
