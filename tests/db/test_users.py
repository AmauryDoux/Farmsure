import pytest
import farmsure.db as db
from farmsure.db.users import _hash


class TestHash:
    def test_deterministic(self):
        assert _hash("secret") == _hash("secret")

    def test_different_inputs_differ(self):
        assert _hash("abc") != _hash("xyz")

    def test_returns_hex_string(self):
        result = _hash("password")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex digest


class TestRegisterUser:
    def test_success_returns_id(self, make_user):
        uid = make_user()
        assert isinstance(uid, int)
        assert uid > 0

    def test_duplicate_email_returns_error(self, make_user):
        make_user(email="dup@farm.com")
        uid, err = db.register_user(
            "Other Person", "dup@farm.com", "password123", "", "", "")
        assert uid is None
        assert "already exists" in err

    def test_different_emails_both_succeed(self, make_user):
        uid1 = make_user(email="a@farm.com")
        uid2 = make_user(email="b@farm.com")
        assert uid1 != uid2

    def test_stored_password_is_hashed(self, make_user):
        make_user(email="test@farm.com", password="plaintext")
        user, _ = db.login_user("test@farm.com", "plaintext")
        assert user["password_hash"] == _hash("plaintext")
        assert user["password_hash"] != "plaintext"


class TestLoginUser:
    def test_correct_credentials(self, make_user):
        make_user(email="login@farm.com", password="mypassword")
        user, err = db.login_user("login@farm.com", "mypassword")
        assert err is None
        assert user["email"] == "login@farm.com"

    def test_wrong_password(self, make_user):
        make_user(email="wp@farm.com", password="correct")
        user, err = db.login_user("wp@farm.com", "wrong")
        assert user is None
        assert err is not None

    def test_unknown_email(self):
        user, err = db.login_user("nobody@farm.com", "any")
        assert user is None
        assert err is not None

    def test_returns_all_profile_fields(self, make_user):
        make_user(
            full_name="John Smith",
            email="john@farm.com",
            farm_name="Smith Farm",
            location="Iowa",
            phone="+1 555 9999",
        )
        user, _ = db.login_user("john@farm.com", "password123")
        assert user["full_name"] == "John Smith"
        assert user["farm_name"] == "Smith Farm"
        assert user["location"] == "Iowa"
        assert user["phone"] == "+1 555 9999"

    def test_timestamps_serialised_as_strings(self, make_user):
        make_user(email="ts@farm.com")
        user, _ = db.login_user("ts@farm.com", "password123")
        assert isinstance(user["created_at"], str)


class TestGetUser:
    def test_returns_correct_user(self, make_user):
        uid = make_user(email="get@farm.com", full_name="Get Me")
        user = db.get_user(uid)
        assert user["id"] == uid
        assert user["full_name"] == "Get Me"

    def test_unknown_id_returns_none(self):
        assert db.get_user(999999) is None


class TestUpdateUser:
    def test_updates_fields(self, make_user):
        uid = make_user(email="upd@farm.com", full_name="Old Name")
        db.update_user(uid, "New Name", "New Farm", "New Location", "+1 999 0000")
        user = db.get_user(uid)
        assert user["full_name"] == "New Name"
        assert user["farm_name"] == "New Farm"
        assert user["location"] == "New Location"
        assert user["phone"] == "+1 999 0000"

    def test_email_unchanged_after_update(self, make_user):
        uid = make_user(email="unchanged@farm.com")
        db.update_user(uid, "New Name", "", "", "")
        user = db.get_user(uid)
        assert user["email"] == "unchanged@farm.com"
