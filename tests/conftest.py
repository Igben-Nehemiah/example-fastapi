from typing import Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from app.main import app
from app import schemas, models
from app.config import settings
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
from app.oauth2 import create_access_token


SQLALCHEMY_DATABASE_URL = \
    f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "test@email.com", "password": "password"}

    res = client.post("/users/", json=user_data)
    new_user = res.json()

    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "test123@email.com", "password": "password"}

    res = client.post("/users/", json=user_data)
    new_user = res.json()

    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, session, test_user2):
    post_data = [
        {
            "title": "The first post",
            "content": "This is an intersting post",
            "owner_id": test_user["id"]
        },
        {
            "title": "The second post",
            "content": "This is an intersting post, I guess",
            "owner_id": test_user["id"]
        },
        {
            "title": "The third post",
            "content": "This is a fairly decent post",
            "owner_id": test_user["id"]
        },
        {
            "title": "The fourth post",
            "content": "This is a fairly decent post",
            "owner_id": test_user2["id"]
        },
    ]

    

    posts = list(map(lambda post: models.Post(**post), post_data))

    session.add_all(posts)
    session.commit()
    return session.query(models.Post).all()