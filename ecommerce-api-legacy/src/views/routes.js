const { checkout } = require('../controllers/checkoutController');
const { report } = require('../controllers/reportController');
const { remove } = require('../controllers/userController');

function asyncHandler(fn) {
    return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
}

function registerRoutes(app) {
    app.post('/api/checkout', asyncHandler(checkout));
    app.get('/api/admin/financial-report', asyncHandler(report));
    app.delete('/api/users/:id', asyncHandler(remove));
}

module.exports = { registerRoutes };
