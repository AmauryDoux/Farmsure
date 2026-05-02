"""
Top-level pytest configuration.

Requires a `farmsure_test` database to exist in the same Docker Postgres
instance. Create it once with:

    docker exec farmers_insurance-db-1 psql -U farmsure -d farmsure -c "CREATE DATABASE farmsure_test;"

The schema is initialised once per session; every individual test gets a
clean slate via TRUNCATE so tests never bleed into each other.
"""

import os

import psycopg2
import pytest
from dotenv import load_dotenv

load_dotenv()

# ── Point the whole test process at the test database ────────────────────────

_prod_url  = os.environ["DATABASE_URL"]
TEST_URL   = _prod_url.rsplit("/", 1)[0] + "/farmsure_test"

os.environ["DATABASE_URL"] = TEST_URL
os.environ.setdefault("DEFAULT_ADMIN_NAME",     "Test Admin")
os.environ.setdefault("DEFAULT_ADMIN_EMAIL",    "testadmin@farmsure.com")
os.environ.setdefault("DEFAULT_ADMIN_PASSWORD", "testpass123")

# Patch the already-imported connection module so all DB calls hit the test DB
import farmsure.db.connection as _conn
_conn.DATABASE_URL  = TEST_URL
_conn.get_connection = lambda: psycopg2.connect(TEST_URL)


# ── Session fixture: verify the test DB exists and initialise the schema ─────

@pytest.fixture(scope="session", autouse=True)
def init_test_database():
    try:
        conn = psycopg2.connect(TEST_URL)
        conn.close()
    except psycopg2.OperationalError:
        pytest.exit(
            "\n\nTest database 'farmsure_test' does not exist. Create it with:\n"
            "  docker exec farmers_insurance-db-1 psql -U farmsure -d farmsure "
            "-c \"CREATE DATABASE farmsure_test;\"\n",
            returncode=1,
        )

    import farmsure.db as db
    db.init_db()
    db.init_admin_db()


# ── Function fixture: wipe all rows before every test ────────────────────────

@pytest.fixture(autouse=True)
def clean_tables():
    import farmsure.db as db
    # Recreate tables in case a generated test dropped them
    db.init_db()
    db.init_admin_db()
    conn = psycopg2.connect(TEST_URL)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("TRUNCATE claims, admins, users RESTART IDENTITY CASCADE")
    conn.close()


# ── Shared helpers available to all tests ────────────────────────────────────

@pytest.fixture
def make_user():
    import farmsure.db as db

    def _make(full_name="Jane Doe", email="jane@farm.com", password="password123",
               farm_name="Green Acres", location="County, State", phone="+1 555 0100"):
        uid, err = db.register_user(full_name, email, password, farm_name, location, phone)
        assert err is None, f"make_user failed: {err}"
        return uid

    return _make


@pytest.fixture
def make_claim(make_user):
    import farmsure.db as db

    def _make(user_id=None, crop_type="Wheat", issue_type="Drought / Lack of Water",
               description="Severe drought this season.", incident_date="2025-07-01",
               affected_acres=50.0, estimated_loss=10000.0):
        if user_id is None:
            user_id = make_user()
        return db.create_claim(
            user_id, crop_type, issue_type, description,
            incident_date, affected_acres, estimated_loss,
        )

    return _make


@pytest.fixture
def seeded_admin():
    import farmsure.db as db
    db.init_admin_db()
    return {
        "email":    os.environ["DEFAULT_ADMIN_EMAIL"],
        "password": os.environ["DEFAULT_ADMIN_PASSWORD"],
        "name":     os.environ["DEFAULT_ADMIN_NAME"],
    }
