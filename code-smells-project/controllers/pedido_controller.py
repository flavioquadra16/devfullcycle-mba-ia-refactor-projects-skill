from functools import wraps

from flask import jsonify, request

import models.pedido_model as pedido_model
from services.notification_service import notifications


def _erro(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            return jsonify({"erro": str(exc)}), 500

    return wrapper


@_erro
def criar_pedido():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        return jsonify({"erro": "Usuario ID é obrigatório"}), 400
    if not itens or len(itens) == 0:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    resultado = pedido_model.criar(usuario_id, itens)
    if "erro" in resultado:
        return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

    notifications.pedido_criado(resultado["pedido_id"], usuario_id)
    return (
        jsonify(
            {
                "dados": resultado,
                "sucesso": True,
                "mensagem": "Pedido criado com sucesso",
            }
        ),
        201,
    )


@_erro
def listar_pedidos_usuario(usuario_id):
    return jsonify({"dados": pedido_model.listar_por_usuario(usuario_id), "sucesso": True}), 200


@_erro
def listar_todos_pedidos():
    return jsonify({"dados": pedido_model.listar(), "sucesso": True}), 200


@_erro
def atualizar_status_pedido(pedido_id):
    dados = request.get_json(silent=True) or {}
    novo_status = dados.get("status", "")
    if novo_status not in pedido_model.STATUS_VALIDOS:
        return jsonify({"erro": "Status inválido"}), 400
    pedido_model.atualizar_status(pedido_id, novo_status)
    notifications.status_alterado(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


@_erro
def relatorio_vendas():
    return jsonify({"dados": pedido_model.relatorio_vendas(), "sucesso": True}), 200
