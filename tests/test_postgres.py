import os
import pytest
from app.core import Clinic
from app.db import Base


@pytest.mark.skipif(
    not os.getenv("POSTGRES_TEST_URL"), reason="Set POSTGRES_TEST_URL to a dedicated test database"
)
def test_postgresql_transactional_scenario():
    s = Clinic(os.environ["POSTGRES_TEST_URL"])
    try:
        a = s.book("slot-1", "PG Demo", "pg-request", True)
        assert s.book("slot-1", "PG Demo", "pg-request", True) == a
        with pytest.raises(ValueError):
            s.book("slot-1", "Other", "other-key", True)
        s.cancel(a["id"], True)
        assert s.slots()[0]["available"]
    finally:
        Base.metadata.drop_all(s.engine)
        s.engine.dispose()
