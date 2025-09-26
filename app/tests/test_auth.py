# tests/test_auth.py
import json

def test_register_and_login(client):
    # Register user
    res = client.post("/auth/register", json={
        "username": "john",
        "password": "password123"
    })
    assert res.status_code == 201

    # Login user
    res = client.post("/auth/login", json={
        "username": "john",   # 👈 use username, not email
        "password": "password123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
