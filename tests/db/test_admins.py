import os
import pytest
import farmsure.db as db


class TestInitAdminDb:
    def test_seeds_default_admin(self, seeded_admin):
        admin, err = db.login_admin(seeded_admin["email"], seeded_admin["password"])
        assert err is None
        assert admin is not None

    def test_idempotent_does_not_duplicate(self, seeded_admin):
        db.init_admin_db()
        db.init_admin_db()
        from farmsure.db.connection import get_connection, _cur
        conn = get_connection()
        c = _cur(conn)
        c.execute("SELECT COUNT(*) AS cnt FROM admins")
        count = c.fetchone()["cnt"]
        conn.close()
        assert count == 1

    def test_default_admin_name_from_env(self, seeded_admin):
        admin, _ = db.login_admin(seeded_admin["email"], seeded_admin["password"])
        assert admin["full_name"] == os.environ["DEFAULT_ADMIN_NAME"]


class TestLoginAdmin:
    def test_correct_credentials(self, seeded_admin):
        admin, err = db.login_admin(seeded_admin["email"], seeded_admin["password"])
        assert err is None
        assert admin["email"] == seeded_admin["email"]

    def test_wrong_password(self, seeded_admin):
        admin, err = db.login_admin(seeded_admin["email"], "wrongpassword")
        assert admin is None
        assert err is not None

    def test_unknown_email(self):
        admin, err = db.login_admin("nobody@nowhere.com", "anything")
        assert admin is None
        assert err is not None

    def test_returns_all_fields(self, seeded_admin):
        admin, _ = db.login_admin(seeded_admin["email"], seeded_admin["password"])
        assert "id" in admin
        assert "full_name" in admin
        assert "email" in admin
        assert "created_at" in admin

    def test_password_hash_not_exposed(self, seeded_admin):
        admin, _ = db.login_admin(seeded_admin["email"], seeded_admin["password"])
        assert admin.get("password_hash") != seeded_admin["password"]

    def test_created_at_is_string(self, seeded_admin):
        admin, _ = db.login_admin(seeded_admin["email"], seeded_admin["password"])
        assert isinstance(admin["created_at"], str)
