import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http(exc):
        return jsonify({"erro": exc.description, "sucesso": False}), exc.code

    @app.errorhandler(Exception)
    def handle_unexpected(exc):
        logger.exception("erro nao tratado")
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
