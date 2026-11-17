const { get } = require('../database');

function findActiveCourse(db, courseId) {
    return get(db, 'SELECT * FROM courses WHERE id = ? AND active = 1', [courseId]);
}

module.exports = { findActiveCourse };
