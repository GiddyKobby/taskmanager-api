def test_create_task(client, auth_headers):
    response = client.post("/tasks/", json={
        "title": "My first task"
    }, headers=auth_headers)

    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "My first task"
    assert data["done"] == False
