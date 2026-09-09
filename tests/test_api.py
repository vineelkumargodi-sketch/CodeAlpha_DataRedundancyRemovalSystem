import pytest

from app import create_app, db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    database_path = tmp_path / "test.db"

    monkeypatch.setenv(
        "DATABASE_URL",
        f"sqlite:///{database_path}"
    )

    app = create_app()
    app.config.update(TESTING=True)

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.drop_all()


def test_create_unique_record(client):

    response = client.post(
        "/api/records",
        json={
            "name": "John Smith",
            "email": "john@example.com",
            "phone": "+91 98765 43210",
        },
    )

    assert response.status_code == 201
    assert response.json["status"] == "UNIQUE"


def test_reject_exact_duplicate(client):

    payload = {
        "name": "John Smith",
        "email": "john@example.com",
        "phone": "+91 98765 43210",
    }

    first = client.post(
        "/api/records",
        json=payload
    )

    second = client.post(
        "/api/records",
        json=payload
    )

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json["status"] == "REDUNDANT"


def test_detect_possible_duplicate(client):

    first = client.post(
        "/api/records",
        json={
            "name": "John Smith",
            "email": "john@example.com",
            "phone": "+91 98765 43210",
        },
    )

    assert first.status_code == 201

    second = client.post(
        "/api/records",
        json={
            "name": "John Smit",
            "email": "john@example.com",
            "phone": "+91 11111 11111",
        },
    )

    assert second.status_code == 409
    assert second.json["status"] == "POSSIBLE_DUPLICATE"


def test_invalid_email(client):

    response = client.post(
        "/api/records",
        json={
            "name": "Test User",
            "email": "invalid-email",
            "phone": "+91 98765 43210",
        },
    )

    assert response.status_code == 400
    assert response.json["status"] == "INVALID"