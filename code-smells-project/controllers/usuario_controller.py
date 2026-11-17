from functools import wraps

from flask import jsonify, request

import models.usuario_model as usuario_model


def _erro(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            return jsonify({"erro": str(exc)}), 500

    return wrapper


@_erro
def listar_usuarios():
    return jsonify({"dados": usuario_model.listar(), "sucesso": True}), 200


@_erro
def buscar_usuario(id):
    usuario = usuario_model.buscar_por_id(id)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True}), 200
    return jsonify({"erro": "Usuário não encontrado"}), 404


@_erro
def criar_usuario():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400
    usuario_id = usuario_model.criar(nome, email, senha)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


@_erro
def login():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400
    usuario = usuario_model.autenticar(email, senha)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
    return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
