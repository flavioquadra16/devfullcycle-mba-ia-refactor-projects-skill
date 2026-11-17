const APPROVED_CARD_PREFIX = '4';

function charge(cardNumber) {
    const approved = String(cardNumber).startsWith(APPROVED_CARD_PREFIX);
    return approved ? 'PAID' : 'DENIED';
}

module.exports = { charge, APPROVED_CARD_PREFIX };
