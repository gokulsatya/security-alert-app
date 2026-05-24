# ---- Unit tests for the Security Alert Management API ----
# Run with:  pytest -v
#
# These tests run against a SEPARATE throwaway SQLite database (test.db),
# NOT your real alerts.db — so your seeded data is never touched.

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from main import app, get_db
import models  # noqa: F401  (import registers the Alert table on Base)

# ---- Set up a dedicated test database ----
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


# This replacement get_db hands tests a session on the TEST database.
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Tell the app: during tests, use override_get_db instead of the real get_db.
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ---- Fixture: fresh, empty tables before each test; cleaned up after ----
@pytest.fixture(autouse=True)
def fresh_database():
    Base.metadata.create_all(bind=test_engine)   # build empty tables
    yield                                         # the test runs here
    Base.metadata.drop_all(bind=test_engine)     # wipe them afterward


# A reusable valid alert payload the tests can start from.
def valid_alert():
    return {
        "title": "Suspicious login attempt",
        "description": "Multiple failed logins from an unknown IP",
        "severity": "High",
        "status": "Open",
        "source": "SIEM",
    }


# ---- Tests ----

def test_list_alerts_empty():
    # A fresh test DB has no alerts, so the list should be empty.
    response = client.get("/alerts")
    assert response.status_code == 200
    assert response.json() == []


def test_create_alert_succeeds():
    response = client.post("/alerts", json=valid_alert())
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Suspicious login attempt"
    assert body["id"] == 1                 # first alert gets id 1
    assert "created_at" in body            # server set a timestamp


def test_get_one_alert():
    created = client.post("/alerts", json=valid_alert()).json()
    response = client.get(f"/alerts/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_missing_alert_returns_404():
    response = client.get("/alerts/999999")
    assert response.status_code == 404


def test_create_rejects_short_description():
    bad = valid_alert()
    bad["description"] = "too short"       # under 10 characters
    response = client.post("/alerts", json=bad)
    assert response.status_code == 422     # validation error


def test_create_rejects_invalid_severity():
    bad = valid_alert()
    bad["severity"] = "Spicy"              # not a real severity
    response = client.post("/alerts", json=bad)
    assert response.status_code == 422


def test_update_alert():
    created = client.post("/alerts", json=valid_alert()).json()
    changed = valid_alert()
    changed["status"] = "Closed"
    response = client.put(f"/alerts/{created['id']}", json=changed)
    assert response.status_code == 200
    assert response.json()["status"] == "Closed"


def test_delete_alert():
    created = client.post("/alerts", json=valid_alert()).json()
    response = client.delete(f"/alerts/{created['id']}")
    assert response.status_code == 200
    # Confirm it's really gone.
    follow_up = client.get(f"/alerts/{created['id']}")
    assert follow_up.status_code == 404