import azure.functions as func
import logging
import json
import os
import pyodbc
from typing import Dict, Any

SQL_CONN_STR = os.getenv("SQL_CONNECTION_STRING")

def get_conn():
    return pyodbc.connect(SQL_CONN_STR)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

USUARIOS: Dict[int, Dict[str, Any]] = {}
PROX_ID = 1


def imprimir_titulo(titulo: str):
    logging.info("\n" + "=" * 60)
    logging.info(titulo)
    logging.info("=" * 60)


def listar_usuarios():
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, idade, email, cidade FROM Usuarios")
        rows = cursor.fetchall()

        usuarios = []
        for r in rows:
            usuarios.append({
                "id": r.id,
                "nome": r.nome,
                "idade": r.idade,
                "email": r.email,
                "cidade": r.cidade,
            })

    return {
        "status_code": 200,
        "corpo": usuarios,
    }


def obter_usuario(usuario_id: int):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome, idade, email, cidade FROM Usuarios WHERE id = ?",
            (usuario_id,)
        )
        row = cursor.fetchone()

    if not row:
        return {
            "status_code": 404,
            "corpo": f"Usuário {usuario_id} não encontrado",
        }

    usuario = {
        "id": row.id,
        "nome": row.nome,
        "idade": row.idade,
        "email": row.email,
        "cidade": row.cidade,
    }

    return {
        "status_code": 200,
        "corpo": usuario,
    }



def criar_usuario(nome: str, idade: int, email: str, cidade: str | None = None):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Usuarios (nome, idade, email, cidade)
            OUTPUT INSERTED.id, INSERTED.nome, INSERTED.idade, INSERTED.email, INSERTED.cidade
            VALUES (?, ?, ?, ?)
            """,
            (nome, idade, email, cidade)
        )
        row = cursor.fetchone()
        conn.commit()

    usuario = {
        "id": row.id,
        "nome": row.nome,
        "idade": row.idade,
        "email": row.email,
        "cidade": row.cidade,
    }

    return {
        "status_code": 201,
        "corpo": usuario,
    }


def atualizar_usuario(
    usuario_id: int,
    nome: str | None = None,
    idade: int | None = None,
    email: str | None = None,
    cidade: str | None = None,
):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nome, idade, email, cidade FROM Usuarios WHERE id = ?",
            (usuario_id,)
        )
        row = cursor.fetchone()

        if not row:
            return {
                "status_code": 404,
                "corpo": f"Usuário {usuario_id} não encontrado",
            }

        novo_nome = nome if nome is not None else row.nome
        nova_idade = idade if idade is not None else row.idade
        novo_email = email if email is not None else row.email
        nova_cidade = cidade if cidade is not None else row.cidade

        cursor.execute(
            """
            UPDATE Usuarios
            SET nome = ?, idade = ?, email = ?, cidade = ?
            WHERE id = ?
            """,
            (novo_nome, nova_idade, novo_email, nova_cidade, usuario_id)
        )
        conn.commit()

    return {
        "status_code": 200,
        "corpo": {
            "id": usuario_id,
            "nome": novo_nome,
            "idade": nova_idade,
            "email": novo_email,
            "cidade": nova_cidade,
        },
    }


def remover_usuario(usuario_id: int):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Usuarios WHERE id = ?",
            (usuario_id,)
        )
        linhas = cursor.rowcount
        conn.commit()

    if linhas == 0:
        return {
            "status_code": 404,
            "corpo": f"Usuário {usuario_id} não encontrado",
        }

    return {
        "status_code": 200,
        "corpo": f"Usuário {usuario_id} removido com sucesso",
    }


def _http_from_result(resultado: dict) -> func.HttpResponse:
    status_code = resultado.get("status_code", 200)
    corpo = resultado.get("corpo")

    if isinstance(corpo, (dict, list)):
        body = json.dumps(corpo, ensure_ascii=False)
        mimetype = "application/json"
    else:
        body = str(corpo)
        mimetype = "text/plain; charset=utf-8"

    return func.HttpResponse(
        body=body,
        status_code=status_code,
        mimetype=mimetype,
    )


@app.route(route="usuarios", methods=["GET", "POST"])
def http_usuarios(req: func.HttpRequest) -> func.HttpResponse:

    if req.method == "GET":
        imprimir_titulo("Listando usuários via Azure Function")
        try:
            resultado = listar_usuarios()
            return _http_from_result(resultado)
        except Exception as e:
            logging.exception("Erro ao listar usuários")
            return func.HttpResponse(
                f"Erro ao listar usuários: {e}",
                status_code=500,
                mimetype="text/plain; charset=utf-8",
            )

    if req.method == "POST":
        try:
            body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                "JSON inválido na requisição",
                status_code=400
            )

        nome = body.get("nome")
        idade = body.get("idade")
        email = body.get("email")
        cidade = body.get("cidade")

        if not (nome and idade and email):
            return func.HttpResponse(
                "Campos obrigatórios: nome, idade, email",
                status_code=400
            )

        imprimir_titulo("Criando usuário via Azure Function")
        try:
            resultado = criar_usuario(nome, idade, email, cidade)
            return _http_from_result(resultado)
        except Exception as e:
            logging.exception("Erro ao criar usuário")
            return func.HttpResponse(
                f"Erro ao criar usuário: {e}",
                status_code=500,
                mimetype="text/plain; charset=utf-8",
            )


@app.route(route="usuarios/{usuario_id}", methods=["GET", "PUT", "DELETE"])
def http_usuario_por_id(req: func.HttpRequest) -> func.HttpResponse:
    usuario_id_str = req.route_params.get("usuario_id")

    try:
        usuario_id = int(usuario_id_str)
    except (TypeError, ValueError):
        return func.HttpResponse(
            "ID do usuário inválido.",
            status_code=400
        )

    if req.method == "GET":
        imprimir_titulo(f"Obtendo usuário ID {usuario_id} via Azure Function")
        resultado = obter_usuario(usuario_id)
        return _http_from_result(resultado)

    if req.method == "PUT":
        try:
            body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                "JSON inválido na requisição",
                status_code=400
            )

        nome = body.get("nome")
        idade = body.get("idade")
        email = body.get("email")
        cidade = body.get("cidade")

        imprimir_titulo(f"Atualizando usuário ID {usuario_id} via Azure Function")
        resultado = atualizar_usuario(
            usuario_id,
            nome=nome,
            idade=idade,
            email=email,
            cidade=cidade,
        )
        return _http_from_result(resultado)

    if req.method == "DELETE":
        imprimir_titulo(f"Removendo usuário ID {usuario_id} via Azure Function")
        resultado = remover_usuario(usuario_id)
        return _http_from_result(resultado)