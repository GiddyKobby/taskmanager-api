import json

def test_register_and_login(client):
    # Register
    response = client.post("/auth/register", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 201

    # Login
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
