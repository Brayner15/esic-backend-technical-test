from tests.conftest import client
import pytest


@pytest.mark.asyncio
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
def test_create_request(client):
    payload = {
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "information",
        "description": "This is a test request for institutional information",
    }

    response = client.post("/api/v1/requests/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["requester_name"] == "John Doe"
    assert data["requester_email"] == "john@example.com"
    assert data["status"] == "pending"
    assert "request_number" in data
    assert "id" in data


@pytest.mark.asyncio
def test_create_request_invalid_email(client):
    payload = {
        "requester_name": "John Doe",
        "requester_email": "invalid-email",
        "institution_name": "Test Institution",
        "request_type": "information",
        "description": "This is a test request for institutional information",
    }

    response = client.post("/api/v1/requests/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
def test_create_request_short_description(client):
    payload = {
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "information",
        "description": "Short",
    }

    response = client.post("/api/v1/requests/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
def test_get_request(client):
    payload = {
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "information",
        "description": "This is a test request for institutional information",
    }

    create_response = client.post("/api/v1/requests/", json=payload)
    request_id = create_response.json()["id"]

    get_response = client.get(f"/api/v1/requests/{request_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == request_id
    assert data["requester_name"] == "John Doe"


@pytest.mark.asyncio
def test_get_request_not_found(client):
    response = client.get("/api/v1/requests/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
def test_list_requests(client):
    for i in range(3):
        payload = {
            "requester_name": f"User {i}",
            "requester_email": f"user{i}@example.com",
            "institution_name": "Test Institution",
            "request_type": "information",
            "description": "This is a test request for institutional information",
        }
        client.post("/api/v1/requests/", json=payload)

    response = client.get("/api/v1/requests/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
def test_update_request(client):
    payload = {
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "information",
        "description": "This is a test request for institutional information",
    }

    create_response = client.post("/api/v1/requests/", json=payload)
    request_id = create_response.json()["id"]

    update_payload = {"status": "processing", "description": "Updated description with more content"}

    update_response = client.put(f"/api/v1/requests/{request_id}", json=update_payload)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["status"] == "processing"
    assert data["description"] == "Updated description with more content"


@pytest.mark.asyncio
def test_delete_request(client):
    payload = {
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "information",
        "description": "This is a test request for institutional information",
    }

    create_response = client.post("/api/v1/requests/", json=payload)
    request_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/requests/{request_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/requests/{request_id}")
    assert get_response.status_code == 404
