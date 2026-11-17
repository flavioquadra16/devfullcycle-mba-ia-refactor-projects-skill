from database import get_db
from utils.passwords import hash_password, verify_password


def _publico(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def listar():
    rows = get_db().execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios"
    ).fetchall()
    return [_publico(row) for row in rows]


def buscar_por_id(usuario_id):
    row = get_db().execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?",
        (usuario_id,),
    ).fetchone()
    if row is None:
        return None
    return _publico(row)


def criar(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, hash_password(senha), tipo),
    )
    db.commit()
    return cursor.lastrowid


def autenticar(email, senha):
    row = get_db().execute(
        "SELECT id, nome, email, senha, tipo FROM usuarios WHERE email = ?",
        (email,),
    ).fetchone()
    if row is None or not verify_password(senha, row["senha"]):
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }
