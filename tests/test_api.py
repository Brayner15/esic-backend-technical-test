from tests.conftest import client
import pytest


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


def test_health_ready(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data


def test_create_request(client):
    payload = {
        "external_id": "EXT-001",
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "soporte_tecnico",
        "description": "This is a test request for technical support with sufficient length",
        "priority": "media",
    }

    response = client.post("/solicitudes/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["requester_name"] == "John Doe"
    assert data["requester_email"] == "john@example.com"
    assert data["status"] == "recibida"
    assert data["priority"] == "media"
    assert "request_number" in data
    assert "id" in data


def test_create_duplicate_external_id(client):
    """Test that duplicate external_id returns 409 Conflict."""
    payload = {
        "external_id": "EXT-DUP",
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "academica",
        "description": "This is a test request with sufficient description length",
    }

    response1 = client.post("/solicitudes/", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/solicitudes/", json=payload)
    assert response2.status_code == 409


def test_create_request_invalid_email(client):
    payload = {
        "external_id": "EXT-002",
        "requester_name": "John Doe",
        "requester_email": "invalid-email",
        "institution_name": "Test Institution",
        "request_type": "administrativa",
        "description": "This is a test request with sufficient description length",
    }

    response = client.post("/solicitudes/", json=payload)
    assert response.status_code == 422


def test_create_request_short_description(client):
    payload = {
        "external_id": "EXT-003",
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "acceso_plataforma",
        "description": "Short",
    }

    response = client.post("/solicitudes/", json=payload)
    assert response.status_code == 422


def test_create_request_invalid_type(client):
    payload = {
        "external_id": "EXT-004",
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "invalid_type",
        "description": "This is a test request with sufficient description length",
    }

    response = client.post("/solicitudes/", json=payload)
    assert response.status_code == 422


def test_get_request(client):
    payload = {
        "external_id": "EXT-005",
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "soporte_tecnico",
        "description": "This is a test request for technical support with sufficient length",
    }

    create_response = client.post("/solicitudes/", json=payload)
    request_id = create_response.json()["id"]

    get_response = client.get(f"/solicitudes/{request_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == request_id
    assert data["requester_name"] == "John Doe"


def test_get_request_not_found(client):
    response = client.get("/solicitudes/9999")
    assert response.status_code == 404


def test_list_requests(client):
    for i in range(3):
        payload = {
            "external_id": f"EXT-LIST-{i}",
            "requester_name": f"User {i}",
            "requester_email": f"user{i}@example.com",
            "institution_name": "Test Institution",
            "request_type": "academica",
            "description": "This is a test request with sufficient description length",
        }
        client.post("/solicitudes/", json=payload)

    response = client.get("/solicitudes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


def test_list_requests_filter_by_priority(client):
    for priority in ["baja", "media", "alta"]:
        payload = {
            "external_id": f"EXT-PRIO-{priority}",
            "requester_name": "Test User",
            "requester_email": "test@example.com",
            "institution_name": "Test Institution",
            "request_type": "administrativa",
            "description": "This is a test request with sufficient description length",
            "priority": priority,
        }
        client.post("/solicitudes/", json=payload)

    response = client.get("/solicitudes/?priority=alta")
    assert response.status_code == 200
    data = response.json()
    assert all(item["priority"] == "alta" for item in data)


def test_list_requests_filter_by_type(client):
    payload = {
        "external_id": "EXT-TYPE-TEST",
        "requester_name": "Test User",
        "requester_email": "test@example.com",
        "institution_name": "Test Institution",
        "request_type": "soporte_tecnico",
        "description": "This is a test request with sufficient description length",
    }
    client.post("/solicitudes/", json=payload)

    response = client.get("/solicitudes/?request_type=soporte_tecnico")
    assert response.status_code == 200
    data = response.json()
    assert all(item["request_type"] == "soporte_tecnico" for item in data)


def test_update_request_status(client):
    payload = {
        "external_id": "EXT-UPD-STATUS",
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "academica",
        "description": "This is a test request with sufficient description length",
    }

    create_response = client.post("/solicitudes/", json=payload)
    request_id = create_response.json()["id"]

    update_payload = {"status": "en_proceso"}
    update_response = client.patch(f"/solicitudes/{request_id}/estado", json=update_payload)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["status"] == "en_proceso"


def test_update_request(client):
    payload = {
        "external_id": "EXT-UPD",
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "administrativa",
        "description": "This is a test request with sufficient description length",
    }

    create_response = client.post("/solicitudes/", json=payload)
    request_id = create_response.json()["id"]

    update_payload = {
        "priority": "alta",
        "description": "Updated description with more content and sufficient length",
    }

    update_response = client.put(f"/solicitudes/{request_id}", json=update_payload)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["priority"] == "alta"
    assert data["description"] == "Updated description with more content and sufficient length"


def test_delete_request(client):
    payload = {
        "external_id": "EXT-DEL",
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "acceso_plataforma",
        "description": "This is a test request with sufficient description length",
    }

    create_response = client.post("/solicitudes/", json=payload)
    request_id = create_response.json()["id"]

    delete_response = client.delete(f"/solicitudes/{request_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/solicitudes/{request_id}")
    assert get_response.status_code == 404
