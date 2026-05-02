# tests/conftest.py
import os
import pytest
import psycopg2
from dotenv import load_dotenv
from unittest.mock import Mock, patch, MagicMock

load_dotenv()


@pytest.fixture(scope="session")
def test_db_url():
    """Get test database URL from environment variable."""
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set")
    return url


@pytest.fixture
def test_connection(test_db_url):
    """Create a test database connection."""
    conn = psycopg2.connect(test_db_url)
    yield conn
    conn.close()


@pytest.fixture
def clean_db(test_connection):
    """Clean up database before and after test."""
    cursor = test_connection.cursor()
    
    # Drop tables if they exist
    cursor.execute("DROP TABLE IF EXISTS claims CASCADE")
    cursor.execute("DROP TABLE IF EXISTS users CASCADE")
    cursor.execute("DROP TABLE IF EXISTS admins CASCADE")
    test_connection.commit()
    
    yield test_connection
    
    # Cleanup after test
    cursor.execute("DROP TABLE IF EXISTS claims CASCADE")
    cursor.execute("DROP TABLE IF EXISTS users CASCADE")
    cursor.execute("DROP TABLE IF EXISTS admins CASCADE")
    test_connection.commit()
    cursor.close()


@pytest.fixture
def mock_connection():
    """Mock database connection."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


# tests/test_users.py
import pytest
import hashlib
import psycopg2.errors
from unittest.mock import patch, MagicMock
from farmsure.db.users import (
    _hash, init_db, register_user, login_user, get_user, update_user
)
from farmsure.db.connection import _cur


class TestHashFunction:
    def test_hash_consistency(self):
        """Test that hashing produces consistent results."""
        password = "test_password_123"
        hash1 = _hash(password)
        hash2 = _hash(password)
        assert hash1 == hash2

    def test_hash_format(self):
        """Test that hash is SHA256 hexdigest."""
        password = "test"
        result = _hash(password)
        expected = hashlib.sha256(password.encode()).hexdigest()
        assert result == expected

    def test_hash_different_passwords(self):
        """Test that different passwords produce different hashes."""
        hash1 = _hash("password1")
        hash2 = _hash("password2")
        assert hash1 != hash2

    def test_hash_empty_string(self):
        """Test hashing empty string."""
        result = _hash("")
        expected = hashlib.sha256("".encode()).hexdigest()
        assert result == expected


class TestInitDb:
    @patch("farmsure.db.users.get_connection")
    def test_init_db_creates_tables(self, mock_get_conn):
        """Test that init_db creates necessary tables."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        init_db()

        assert mock_cursor.execute.call_count >= 2
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("farmsure.db.users.get_connection")
    def test_init_db_creates_users_table(self, mock_get_conn):
        """Test that users table is created with correct schema."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        init_db()

        calls = mock_cursor.execute.call_args_list
        users_table_sql = calls[0][0][0]
        assert "CREATE TABLE IF NOT EXISTS users" in users_table_sql
        assert "full_name" in users_table_sql
        assert "email" in users_table_sql
        assert "password_hash" in users_table_sql

    @patch("farmsure.db.users.get_connection")
    def test_init_db_creates_claims_table(self, mock_get_conn):
        """Test that claims table is created with correct schema."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        init_db()

        calls = mock_cursor.execute.call_args_list
        claims_table_sql = calls[1][0][0]
        assert "CREATE TABLE IF NOT EXISTS claims" in claims_table_sql
        assert "user_id" in claims_table_sql
        assert "claim_number" in claims_table_sql


class TestRegisterUser:
    @patch("farmsure.db.users.get_connection")
    def test_register_user_success(self, mock_get_conn):
        """Test successful user registration."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"id": 1}

        uid, error = register_user(
            "John Doe", "john@example.com", "password123",
            "Doe Farm", "Iowa", "555-1234"
        )

        assert uid == 1
        assert error is None
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("farmsure.db.users.get_connection")
    def test_register_user_duplicate_email(self, mock_get_conn):
        """Test registration with duplicate email."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.errors.UniqueViolation("duplicate email")

        uid, error = register_user(
            "Jane Doe", "jane@example.com", "password123",
            "Doe Farm", "Iowa", "555-5678"
        )

        assert uid is None
        assert "already exists" in error
        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("farmsure.db.users.get_connection")
    def test_register_user_returns_id(self, mock_get_conn):
        """Test that register_user returns the correct user ID."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"id": 42}

        uid, _ = register_user(
            "Test User", "test@example.com", "pass",
            "Test Farm", "Location", "123-4567"
        )

        assert uid == 42

    @patch("farmsure.db.users.get_connection")
    def test_register_user_closes_connection(self, mock_get_conn):
        """Test that connection is closed after registration."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"id": 1}

        register_user("User", "email@test.com", "pass", "Farm", "Location", "Phone")

        mock_conn.close.assert_called_once()

    @patch("farmsure.db.users.get_connection")
    def test_register_user_hashes_password(self, mock_get_conn):
        """Test that password is hashed before storage."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"id": 1}

        password = "plaintext_password"
        register_user("User", "email@test.com", password, "Farm", "Location", "Phone")

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1][2] == _hash(password)


class TestLoginUser:
    @patch("farmsure.db.users.get_connection")
    def test_login_user_success(self, mock_get_conn):
        """Test successful user login."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        user_data = {
            "id": 1, "full_name": "John Doe", "email": "john@example.com",
            "password_hash": _hash("password123"), "farm_name": "Doe Farm",
            "location": "Iowa", "phone": "555-1234", "created_at": "2023-01-01T00:00:00"
        }
        mock_cursor.fetchone.return_value = user_data

        user, error = login_user("john@example.com", "password123")

        assert user is not None
        assert error is None
        assert user["id"] == 1
        mock_conn.close.assert_called_once()

    @patch("farmsure.db.users.get_connection")
    def test_login_user_wrong_password(self, mock_get_conn):
        """Test login with wrong password."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        user, error = login_user("john@example.com", "wrongpassword")

        assert user is None
        assert "Incorrect" in error

    @patch("farmsure.db.users.get_connection")
    def test_login_user_nonexistent_email(self, mock_get_conn):
        """Test login with non-existent email."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        user, error = login_user("nonexistent@example.com", "password")

        assert user is None
        assert "Incorrect" in error

    @patch("farmsure.db.users.get_connection")
    def test_login_user_closes_connection(self, mock_get_conn):
        """Test that connection is closed after login."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        login_user("email@test.com", "password")

        mock_conn.close.assert_called_once()

    @patch("farmsure.db.users.get_connection")
    def test_login_user_returns_user_dict(self, mock_get_conn):
        """Test that login returns user data as dictionary."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        user_data = {"id": 1, "full_name": "User", "email": "user@test.com"}
        mock_cursor.fetchone.return_value = user_data

        user, _ = login_user("user@test.com", "password")

        assert isinstance(user, dict)
        assert user["id"] == 1


class TestGetUser:
    @patch("farmsure.db.users.get_connection")
    def test_get_user_success(self, mock_get_conn):
        """Test retrieving user by ID."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        user_data = {
            "id": 1, "full_name": "John Doe", "email": "john@example.com",
            "farm_name": "Doe Farm", "location": "Iowa", "phone": "555-1234"
        }
        mock_cursor.fetchone.return_value = user_data

        user = get_user(1)

        assert user["id"] == 1
        assert user["full_name"] == "John Doe"
        mock_conn.close.assert_called_once()

    @patch("farmsure.db.users.get_connection")
    def test_get_user_not_found(self, mock_get_conn):
        """Test retrieving non-existent user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        user = get_user(999)

        assert user is None

    @patch("farmsure.db.users.get_connection")
    def test_get_user_closes_connection(self, mock_get_conn):
        """Test that connection is closed after get_user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        get_user(1)

        mock_conn.close.assert_called_once()


class TestUpdateUser:
    @patch("farmsure.db.users.get_connection")
    def test_update_user_success(self, mock_get_conn):
        """Test successful user update."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        update_user(1, "Jane Doe", "New Farm", "New Location", "555-9999")

        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("farmsure.db.users.get_connection")
    def test_update_user_all_fields(self, mock_get_conn):
        """Test that all fields are updated."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        update_user(1, "Full Name", "Farm Name", "Location", "Phone")

        call_args = mock_cursor.execute.call_args
        assert call_args[0][1] == ("Full Name", "Farm Name", "Location", "Phone", 1)

    @patch("farmsure.db.users.get_connection")
    def test_update_user_closes_connection(self, mock_get_conn):
        """Test that connection is closed after update."""
        mock_conn   = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        with patch("farmsure.db.users._cur", return_value=mock_cursor):
            update_user(1, "Name", "Farm", "Location", "555")

        mock_conn.close.assert_called_once()
