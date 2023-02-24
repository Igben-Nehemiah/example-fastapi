import pytest
from fastapi.testclient import TestClient
from app import schemas
from jose import jwt
from app.config import settings


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running!!!"}


def test_create_user(client: TestClient):
    res = client.post('/users/', json={"email": "test@email.com", "password": "password"})

    new_user = schemas.UserResponseDto(**res.json())

    assert new_user.email == "test@email.com"
    assert res.status_code == 201


def test_login_user(client, test_user):

    res = client.post('/auth/login', 
                      data={"username": test_user["email"], "password": test_user["password"]})

    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id: str = payload.get("user_id")

    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'password', 403),
    ('test@email.com', 'wrongpassword', 403),
    ('wrongemail@gmail.com', 'wrongpassword', 403),
    (None, 'password', 422),
    ('test@email.com', None, 422)
])
def test_incorrect_login(email, password, status_code, test_user, client):
    res = client.post("/auth/login", 
                      data={"username": email, "password": password})
    
    assert res.status_code == status_code