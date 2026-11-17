from functools import wraps

from flask import jsonify, request

import models.produto_model as produto_model

def _erro(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            return jsonify({"erro": str(exc)}), 500

    return wrapper


def _validar_criacao(dados):
    if not dados:
        return None, (jsonify({"erro": "Dados inválidos"}), 400)
    if "nome" not in dados:
        return None, (jsonify({"erro": "Nome é obrigatório"}), 400)
    if "preco" not in dados:
        return None, (jsonify({"erro": "Preço é obrigatório"}), 400)
    if "estoque" not in dados:
        return None, (jsonify({"erro": "Estoque é obrigatório"}), 400)

    nome = dados["nome"]
    preco = dados["preco"]
    estoque = dados["estoque"]
    if preco < 0:
        return None, (jsonify({"erro": "Preço não pode ser negativo"}), 400)
    if estoque < 0:
        return None, (jsonify({"erro": "Estoque não pode ser negativo"}), 400)
    if len(nome) < 2:
        return None, (jsonify({"erro": "Nome muito curto"}), 400)
    if len(nome) > 200:
        return None, (jsonify({"erro": "Nome muito longo"}), 400)

    categoria = dados.get("categoria", "geral")
    if categoria not in produto_model.CATEGORIAS_VALIDAS:
        return None, (
            jsonify(
                {
                    "erro": "Categoria inválida. Válidas: "
                    + str(produto_model.CATEGORIAS_VALIDAS)
                }
            ),
            400,
        )
    return (nome, dados.get("descricao", ""), preco, estoque, categoria), None


@_erro
def listar_produtos():
    produtos = produto_model.listar()
    return jsonify({"dados": produtos, "sucesso": True}), 200


@_erro
def buscar_produto(id):
    produto = produto_model.buscar_por_id(id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


@_erro
def criar_produto():
    campos, erro = _validar_criacao(request.get_json(silent=True))
    if erro:
        return erro
    nome, descricao, preco, estoque, categoria = campos
    produto_id = produto_model.criar(nome, descricao, preco, estoque, categoria)
    return (
        jsonify(
            {
                "dados": {"id": produto_id},
                "sucesso": True,
                "mensagem": "Produto criado",
            }
        ),
        201,
    )


@_erro
def atualizar_produto(id):
    dados = request.get_json(silent=True)
    existente = produto_model.buscar_por_id(id)
    if not existente:
        return jsonify({"erro": "Produto não encontrado"}), 404
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400
    if "nome" not in dados:
        return jsonify({"erro": "Nome é obrigatório"}), 400
    if "preco" not in dados:
        return jsonify({"erro": "Preço é obrigatório"}), 400
    if "estoque" not in dados:
        return jsonify({"erro": "Estoque é obrigatório"}), 400
    if dados["preco"] < 0:
        return jsonify({"erro": "Preço não pode ser negativo"}), 400
    if dados["estoque"] < 0:
        return jsonify({"erro": "Estoque não pode ser negativo"}), 400

    produto_model.atualizar(
        id,
        dados["nome"],
        dados.get("descricao", ""),
        dados["preco"],
        dados["estoque"],
        dados.get("categoria", "geral"),
    )
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


@_erro
def deletar_produto(id):
    produto = produto_model.buscar_por_id(id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    produto_model.deletar(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


@_erro
def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = request.args.get("preco_min", None)
    preco_max = request.args.get("preco_max", None)
    if preco_min:
        preco_min = float(preco_min)
    if preco_max:
        preco_max = float(preco_max)
    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
