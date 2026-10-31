import pytest
from fastapi.testclient import TestClient
from app.core import Clinic, evaluate
from app.api import app, service


@pytest.fixture
def clinic(tmp_path):
    return Clinic("sqlite:///" + str(tmp_path / "clinic.sqlite"))


def test_concurrent_booking():
    assert evaluate()["confirmed_bookings"] == 1


def test_confirmation_replay_and_cancel(clinic):
    with pytest.raises(PermissionError):
        clinic.book("slot-1", "Alex", "a")
    b = clinic.book("slot-1", "Alex", "a", True)
    assert clinic.book("slot-1", "Alex", "a", True) == b
    with pytest.raises(ValueError):
        clinic.book("slot-2", "Alex", "a", True)
    clinic.cancel(b["id"], True)
    assert clinic.slots()[0]["available"]
    clinic.book("slot-1", "Sam", "b", True)
    clinic.cancel(b["id"], True)
    assert not clinic.slots()[0]["available"]


def test_restart_preserves_booking(clinic):
    clinic.book("slot-2", "Demo", "persist", True)
    assert not Clinic(str(clinic.engine.url)).slots()[1]["available"]


def test_api_rejects_unconfirmed(clinic):
    app.dependency_overrides.clear()
    service.cache_clear()
    import app.api as api

    old = api.service
    api.service = lambda: clinic
    try:
        with TestClient(app) as client:
            assert (
                client.post(
                    "/api/bookings", json={"slot_id": "slot-1", "patient": "Alex", "request_key": "a"}
                ).status_code
                == 403
            )
            assert len(client.get("/api/slots").json()) == 4
    finally:
        api.service = old
