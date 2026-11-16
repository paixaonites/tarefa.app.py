import pytest
from app import app, tarefas


@pytest.fixture
def client():
    app.config["TESTING"] = True
    tarefas.clear()
    tarefas.extend([
        {"id": 1, "titulo": "Configurar ambiente Python", "status": "concluida"},
        {"id": 2, "titulo": "Implementar rotas da API", "status": "pendente"}
    ])
    with app.test_client() as client:
        yield client


def obter_token(client):
    resposta = client.post("/login", json={"usuario": "admin", "senha": "123456"})
    return resposta.get_json()["access_token"]


def test_login_sucesso(client):
    resposta = client.post("/login", json={"usuario": "admin", "senha": "123456"})
    dados = resposta.get_json()
    assert resposta.status_code == 200
    assert "access_token" in dados


def test_login_senha_incorreta(client):
    resposta = client.post("/login", json={"usuario": "admin", "senha": "errada"})
    dados = resposta.get_json()
    assert resposta.status_code == 401
    assert "access_token" not in dados


def test_consulta_tarefas(client):
    resposta = client.get("/tarefas")
    dados = resposta.get_json()
    assert resposta.status_code == 200
    assert isinstance(dados, list)
    assert len(dados) == 2


def test_cadastro_sem_token(client):
    resposta = client.post("/tarefas", json={"titulo": "Tarefa não autorizada"})
    assert resposta.status_code == 401
    assert len(tarefas) == 2


def test_cadastro_com_token_valido(client):
    token = obter_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resposta = client.post("/tarefas", json={"titulo": "Revisar os testes da API"}, headers=headers)
    dados = resposta.get_json()

    assert resposta.status_code == 201
    assert dados["titulo"] == "Revisar os testes da API"
    assert dados["status"] == "pendente"
    assert "id" in dados


def test_cadastro_titulo_vazio(client):
    token = obter_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resposta = client.post("/tarefas", json={"titulo": "   "}, headers=headers)

    assert resposta.status_code == 400
    assert len(tarefas) == 2