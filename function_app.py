import azure.functions as func
import logging
import json
from typing import Dict, Any

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

USUARIOS: Dict[int, Dict[str, Any]] = {}
PROX_ID = 1


def imprimir_titulo(titulo: str):
    logging.info("\n" + "=" * 60)
    logging.info(titulo)
    logging.info("=" * 60)


def listar_usuarios():
    return {
        "status_code": 200,
        "corpo": list(USUARIOS.values()),
    }


def obter_usuario(usuario_id: int):
    usuario = USUARIOS.get(usuario_id)
    if usuario is None:
        return {
            "status_code": 404,
            "corpo": f"Usuário {usuario_id} não encontrado",
        }
    return {
        "status_code": 200,
        "corpo": usuario,
    }


def criar_usuario(nome: str, idade: int, email: str, cidade: str | None = None):
    global PROX_ID

    usuario = {
        "id": PROX_ID,
        "nome": nome,
        "idade": idade,
        "email": email,
        "cidade": cidade,
    }
    USUARIOS[PROX_ID] = usuario
    PROX_ID += 1

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
    usuario = USUARIOS.get(usuario_id)
    if usuario is None:
        return {
            "status_code": 404,
            "corpo": f"Usuário {usuario_id} não encontrado",
        }

    if nome is not None:
        usuario["nome"] = nome
    if idade is not None:
        usuario["idade"] = idade
    if email is not None:
        usuario["email"] = email
    if cidade is not None:
        usuario["cidade"] = cidade

    return {
        "status_code": 200,
        "corpo": usuario,
    }


def remover_usuario(usuario_id: int):
    if usuario_id not in USUARIOS:
        return {
            "status_code": 404,
            "corpo": f"Usuário {usuario_id} não encontrado",
        }

    del USUARIOS[usuario_id]
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
        resultado = listar_usuarios()
        return _http_from_result(resultado)

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
        resultado = criar_usuario(nome, idade, email, cidade)
        return _http_from_result(resultado)


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