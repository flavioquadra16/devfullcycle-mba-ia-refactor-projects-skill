from database import get_db

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
DISCOUNT_TIERS = (
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
)

_PEDIDOS_SQL = """
SELECT
    p.id AS pedido_id,
    p.usuario_id AS usuario_id,
    p.status AS status,
    p.total AS total,
    p.criado_em AS criado_em,
    i.id AS item_id,
    i.produto_id AS produto_id,
    i.quantidade AS quantidade,
    i.preco_unitario AS preco_unitario,
    pr.nome AS produto_nome
FROM pedidos p
LEFT JOIN itens_pedido i ON i.pedido_id = p.id
LEFT JOIN produtos pr ON pr.id = i.produto_id
"""


def _agrupar(rows):
    pedidos = {}
    ordem = []
    for row in rows:
        pedido_id = row["pedido_id"]
        if pedido_id not in pedidos:
            pedidos[pedido_id] = {
                "id": pedido_id,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            ordem.append(pedido_id)
        if row["item_id"] is not None:
            nome = row["produto_nome"] if row["produto_nome"] else "Desconhecido"
            pedidos[pedido_id]["itens"].append(
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": nome,
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                }
            )
    return [pedidos[pedido_id] for pedido_id in ordem]


def criar(usuario_id, itens):
    db = get_db()
    produtos = []
    total = 0
    for item in itens:
        produto = db.execute(
            "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?",
            (item["produto_id"],),
        ).fetchone()
        if produto is None:
            return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": "Estoque insuficiente para " + produto["nome"]}
        total = total + (produto["preco"] * item["quantidade"])
        produtos.append(produto)

    try:
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid
        for item, produto in zip(itens, produtos):
            db.execute(
                """
                INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                VALUES (?, ?, ?, ?)
                """,
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"pedido_id": pedido_id, "total": total}


def listar_por_usuario(usuario_id):
    rows = get_db().execute(
        _PEDIDOS_SQL + " WHERE p.usuario_id = ? ORDER BY p.id, i.id",
        (usuario_id,),
    ).fetchall()
    return _agrupar(rows)


def listar():
    rows = get_db().execute(_PEDIDOS_SQL + " ORDER BY p.id, i.id").fetchall()
    return _agrupar(rows)


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()
    return True


def _desconto(faturamento):
    for limite, taxa in DISCOUNT_TIERS:
        if faturamento > limite:
            return faturamento * taxa
    return 0


def relatorio_vendas():
    db = get_db()
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT SUM(total) FROM pedidos").fetchone()[0]
    if faturamento is None:
        faturamento = 0
    pendentes = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'"
    ).fetchone()[0]
    aprovados = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'"
    ).fetchone()[0]
    cancelados = db.execute(
        "SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'"
    ).fetchone()[0]
    desconto = _desconto(faturamento)
    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
