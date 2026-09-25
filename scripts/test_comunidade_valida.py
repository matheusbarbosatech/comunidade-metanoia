import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Testar Rota Web /comunidade
res_web = client.get("/comunidade")
print("Status /comunidade:", res_web.status_code)
assert res_web.status_code == 200, "Falha ao carregar /comunidade"
assert "Comunidade Metanoia" in res_web.text
assert "Acolhimento & Boas-Vindas" in res_web.text

# 2. Testar API de Espaços
res_espacos = client.get("/api/v1/comunidade/espacos")
print("Status /api/v1/comunidade/espacos:", res_espacos.status_code)
assert res_espacos.status_code == 200
espacos = res_espacos.json()
print("Total de Espaços Cadastrados:", len(espacos))
assert len(espacos) >= 6

# 3. Testar API de Posts
res_posts = client.get("/api/v1/comunidade/posts")
print("Status /api/v1/comunidade/posts:", res_posts.status_code)
assert res_posts.status_code == 200
posts = res_posts.json()
print("Total de Posts Iniciais:", len(posts))
assert len(posts) >= 3

# 4. Testar Criação de Novo Post
novo_post = {
    "espaco_id": espacos[0]["id"],
    "autor_nome": "Discípulo Teste",
    "titulo": "Post de Teste Automatizado",
    "conteudo": "Deus é bom em todo o tempo!",
    "anonimo": False
}
res_criar = client.post("/api/v1/comunidade/posts", json=novo_post)
print("Status Criar Post:", res_criar.status_code)
assert res_criar.status_code == 200
post_id = res_criar.json()["post_id"]

# 5. Testar Reação
res_reagir = client.post(f"/api/v1/comunidade/posts/{post_id}/reagir", json={"tipo": "orando"})
print("Status Reagir:", res_reagir.status_code, "Likes:", res_reagir.json()["likes_count"])
assert res_reagir.status_code == 200

# 6. Testar Comentário
res_com = client.post(f"/api/v1/comunidade/posts/{post_id}/comentarios", json={
    "autor_nome": "Irmão Teste",
    "conteudo": "Amém e glória a Deus!"
})
print("Status Comentar:", res_com.status_code)
assert res_com.status_code == 200

# 7. Testar Flet App com a Comunidade ativa
from unittest.mock import MagicMock
from app import flet_app

page_mock = MagicMock()
page_mock.controls = []
page_mock.overlay = []
page_mock._dialogs = MagicMock()
page_mock._dialogs.controls = []
flet_app.main(page_mock)
print("Flet App Main com Aba Comunidade executou com Sucesso!")

print(">>> TODOS OS 7 TESTES DA COMUNIDADE PASSARAM COM 100% DE SUCESSO! <<<")
