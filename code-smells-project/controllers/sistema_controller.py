from flask import jsonify, request

from config.settings import settings
from database import get_db


def health_check():
    try:
        db = get_db()
        db.execute("SELECT 1")
        produtos = db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
        usuarios = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
        return (
            jsonify(
                {
                    "status": "ok",
                    "database": "connected",
                    "counts": {
                        "produtos": produtos,
                        "usuarios": usuarios,
                        "pedidos": pedidos,
                    },
                    "versao": settings.APP_VERSION,
                    "ambiente": settings.ENV,
                }
            ),
            200,
        )
    except Exception as exc:
        return jsonify({"status": "erro", "detalhes": str(exc)}), 500


def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": settings.APP_VERSION,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


def reset_database():
    db = get_db()
    db.execute("DELETE FROM itens_pedido")
    db.execute("DELETE FROM pedidos")
    db.execute("DELETE FROM produtos")
    db.execute("DELETE FROM usuarios")
    db.commit()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


def executar_query():
    dados = request.get_json(silent=True) or {}
    if not dados.get("sql"):
        return jsonify({"erro": "Query não informada"}), 400
    return (
        jsonify(
            {
                "erro": "Execução de SQL arbitrário foi desativada por segurança",
                "sucesso": False,
            }
        ),
        403,
    )
