import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
from tests.conftest import client


def test_duplicate_external_id_sequential(client):
    """Test that duplicate external_id is rejected."""
    payload = {
        "external_id": "EXT-CONC-001",
        "requester_name": "John Doe",
        "requester_email": "john@example.com",
        "institution_name": "Test Institution",
        "request_type": "soporte_tecnico",
        "description": "This is a test request with sufficient description length",
    }

    response1 = client.post("/solicitudes/", json=payload)
    assert response1.status_code == 201
    request_id_1 = response1.json()["id"]

    response2 = client.post("/solicitudes/", json=payload)
    assert response2.status_code == 409
    detail = response2.json()["detail"]
    assert "external_id" in detail.lower()
    assert "EXT-CONC-001" in detail


def test_concurrent_duplicate_attempts(client):
    """Test handling of concurrent attempts to create duplicate requests."""
    external_id = "EXT-CONC-PARALLEL"
    payload = {
        "external_id": external_id,
        "requester_name": "Jane Doe",
        "requester_email": "jane@example.com",
        "institution_name": "Test Institution",
        "request_type": "academica",
        "description": "This is a test request with sufficient description length",
    }

    successful = 0
    conflicts = 0

    def create_request():
        response = client.post("/solicitudes/", json=payload)
        return response.status_code

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(create_request) for _ in range(5)]
        for future in as_completed(futures):
            status_code = future.result()
            if status_code == 201:
                successful += 1
            elif status_code == 409:
                conflicts += 1

    assert successful == 1
    assert conflicts == 4


def test_concurrent_different_requests(client):
    """Test that concurrent requests with different external_ids all succeed."""
    successful = 0

    def create_request(index: int):
        payload = {
            "external_id": f"EXT-DIFF-{index}",
            "requester_name": f"User {index}",
            "requester_email": f"user{index}@example.com",
            "institution_name": "Test Institution",
            "request_type": "administrativa",
            "description": "This is a test request with sufficient description length",
        }
        response = client.post("/solicitudes/", json=payload)
        return response.status_code

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(create_request, i) for i in range(10)]
        for future in as_completed(futures):
            status_code = future.result()
            if status_code == 201:
                successful += 1

    assert successful == 10


def test_idempotent_request_creation_detection(client):
    """Test that the system detects duplicate attempts even with slight delays."""
    external_id = "EXT-IDEM-001"
    payload = {
        "external_id": external_id,
        "requester_name": "Alice Smith",
        "requester_email": "alice@example.com",
        "institution_name": "Test Institution",
        "request_type": "soporte_tecnico",
        "description": "This is a test request with sufficient description length",
    }

    response1 = client.post("/solicitudes/", json=payload)
    assert response1.status_code == 201
    request_1 = response1.json()

    import time
    time.sleep(0.1)

    response2 = client.post("/solicitudes/", json=payload)
    assert response2.status_code == 409
    assert request_1["id"] in response2.json()["detail"]


def test_update_nonexistent_request(client):
    """Test that updating a non-existent request returns 404."""
    payload = {"priority": "alta"}

    response = client.put("/solicitudes/99999", json=payload)
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert "no encontrada" in detail.lower()


def test_update_status_nonexistent_request(client):
    """Test that updating status of non-existent request returns 404."""
    payload = {"status": "completada"}

    response = client.patch("/solicitudes/99999/estado", json=payload)
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert "no encontrada" in detail.lower()


def test_delete_nonexistent_request(client):
    """Test that deleting a non-existent request returns 404."""
    response = client.delete("/solicitudes/99999")
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert "no encontrada" in detail.lower()


def test_create_and_verify_request_uniqueness(client):
    """Test that each created request has unique request_number."""
    request_numbers = set()

    for i in range(5):
        payload = {
            "external_id": f"EXT-UNIQUE-{i}",
            "requester_name": f"User {i}",
            "requester_email": f"user{i}@example.com",
            "institution_name": "Test Institution",
            "request_type": "academica",
            "description": "This is a test request with sufficient description length",
        }
        response = client.post("/solicitudes/", json=payload)
        assert response.status_code == 201
        request_number = response.json()["request_number"]
        request_numbers.add(request_number)

    assert len(request_numbers) == 5


def test_list_requests_after_duplicates(client):
    """Test that duplicate attempts don't create multiple entries."""
    external_id = "EXT-LIST-CONC"
    payload = {
        "external_id": external_id,
        "requester_name": "Bob Johnson",
        "requester_email": "bob@example.com",
        "institution_name": "Test Institution",
        "request_type": "administrativa",
        "description": "This is a test request with sufficient description length",
    }

    response1 = client.post("/solicitudes/", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/solicitudes/", json=payload)
    assert response2.status_code == 409

    list_response = client.get("/solicitudes/")
    requests = list_response.json()
    matching_requests = [r for r in requests if r["external_id"] == external_id]

    assert len(matching_requests) == 1
