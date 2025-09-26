import pytest
from app import create_app
from app.config import TestingConfig
from app.extensions import db  # adjust if db is initialized elsewhere

@pytest.fixture
def app():
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()  # setup schema before each test
        yield app
        db.session.remove()
        db.drop_all()  # clean after each test

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Register and login a test user, then return auth headers
    client.post("/auth/register", json={
        "username": "tester",
        "password": "testpass"
    })
    response = client.post("/auth/login", json={
        "username": "tester",
        "password": "testpass"
    })
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
