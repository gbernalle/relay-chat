from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "auth_service"))
)

from main import app, get_db, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

Base.metadata.create_all(bind=engine)

def test_register_user():
    """Testa se é possível registrar um usuário novo."""
    response = client.post(
        "/register",
        json={"username": "teste_unitario", "password": "123"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Usuário criado com sucesso"}

def test_register_duplicate_user():
    """Testa se o sistema barra usuários duplicados."""
    response = client.post(
        "/register",
        json={"username": "teste_unitario", "password": "123"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuário já existe"

def test_login_success():
    """Testa login com senha correta."""
    response = client.post(
        "/login",
        json={"username": "teste_unitario", "password": "123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "teste_unitario"
    assert "user_id" in data

def test_login_wrong_password():
    """Testa login com senha errada."""
    response = client.post(
        "/login",
        json={"username": "teste_unitario", "password": "ERRADA"},
    )
    assert response.status_code == 400