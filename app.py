from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "chave-secreta-super-segura-atividade"

jwt = JWTManager(app)

usuarios = {
    "admin": generate_password_hash("123456")
}

tarefas = [
    {"id": 1, "titulo": "Configurar ambiente Python", "status": "concluida"},
    {"id": 2, "titulo": "Implementar rotas da API", "status": "pendente"}
]


@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json(silent=True) or {}
    usuario = dados.get("usuario")
    senha = dados.get("senha")

    if not usuario or not senha:
        return jsonify({"erro": "Usuário e senha são obrigatórios"}), 401

    senha_hash = usuarios.get(usuario)
    if not senha_hash or not check_password_hash(senha_hash, senha):
        return jsonify({"erro": "Credenciais inválidas"}), 401

    token = create_access_token(identity=usuario)
    return jsonify({"access_token": token}), 200


@app.route("/tarefas", methods=["GET"])
def listar_tarefas():
    return jsonify(tarefas), 200


@app.route("/tarefas", methods=["POST"])
@jwt_required()
def criar_tarefa():
    dados = request.get_json(silent=True) or {}
    titulo = dados.get("titulo")

    if not titulo or not isinstance(titulo, str) or not titulo.strip():
        return jsonify({"erro": "O título da tarefa é obrigatório"}), 400

    novo_id = max([t["id"] for t in tarefas], default=0) + 1
    nova_tarefa = {
        "id": novo_id,
        "titulo": titulo.strip(),
        "status": "pendente"
    }
    tarefas.append(nova_tarefa)

    return jsonify(nova_tarefa), 201


if __name__ == "__main__":
    app.run(debug=True)