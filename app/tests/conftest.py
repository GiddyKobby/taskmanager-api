# tests/conftest.py
import pytest
from app import create_app
from app.config import TestingConfig
from app.extensions import db


@pytest.fixture
def app():
    """Create a Flask app instance for testing with a fresh DB."""
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client to simulate API requests."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Register + login a test user, then return auth headers with JWT."""
    # Register test user
    client.post("/auth/register", json={
        "username": "tester",
        "password": "testpass"
    })

    # Login and grab token
    response = client.post("/auth/login", json={
        "username": "tester",
        "password": "testpass"
    })
    token = response.get_json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
