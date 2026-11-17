const { all, run } = require('../database');

async function createEnrollment(db, userId, courseId) {
    return run(db, 'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
}

async function createPayment(db, enrollmentId, amount, status) {
    return run(
        db,
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollmentId, amount, status]
    );
}

async function writeAudit(db, action) {
    return run(
        db,
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [action]
    );
}

async function financialReport(db) {
    const courses = await all(db, 'SELECT id, title FROM courses ORDER BY id');
    const rows = await all(
        db,
        `
        SELECT
            e.course_id AS course_id,
            u.name AS student,
            p.amount AS amount,
            p.status AS status
        FROM enrollments e
        LEFT JOIN users u ON u.id = e.user_id
        LEFT JOIN payments p ON p.id = (
            SELECT id FROM payments WHERE enrollment_id = e.id ORDER BY id LIMIT 1
        )
        ORDER BY e.id
        `
    );

    const grouped = new Map();
    for (const course of courses) {
        grouped.set(course.id, { course: course.title, revenue: 0, students: [] });
    }
    for (const row of rows) {
        const bucket = grouped.get(row.course_id);
        if (!bucket) continue;
        const amount = row.amount == null ? 0 : row.amount;
        if (row.status === 'PAID') bucket.revenue += amount;
        bucket.students.push({
            student: row.student || 'Unknown',
            paid: row.amount == null ? 0 : row.amount,
        });
    }
    return courses.map((course) => grouped.get(course.id));
}

async function deleteUser(db, userId) {
    await run(db, 'BEGIN');
    try {
        await run(
            db,
            'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)',
            [userId]
        );
        await run(db, 'DELETE FROM enrollments WHERE user_id = ?', [userId]);
        await run(db, 'DELETE FROM users WHERE id = ?', [userId]);
        await run(db, 'COMMIT');
    } catch (err) {
        await run(db, 'ROLLBACK');
        throw err;
    }
}

module.exports = {
    createEnrollment,
    createPayment,
    writeAudit,
    financialReport,
    deleteUser,
};
