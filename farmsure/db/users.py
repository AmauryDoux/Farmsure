import hashlib
import psycopg2.errors
from .connection import get_connection, _cur, _row


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    conn = get_connection()
    c = _cur(conn)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            SERIAL PRIMARY KEY,
            full_name     TEXT        NOT NULL,
            email         TEXT        UNIQUE NOT NULL,
            password_hash TEXT        NOT NULL,
            farm_name     TEXT,
            location      TEXT,
            phone         TEXT,
            created_at    TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id             SERIAL PRIMARY KEY,
            user_id        INTEGER     NOT NULL REFERENCES users(id),
            claim_number   TEXT        UNIQUE NOT NULL,
            crop_type      TEXT        NOT NULL,
            issue_type     TEXT        NOT NULL,
            description    TEXT        NOT NULL,
            incident_date  TEXT        NOT NULL,
            affected_acres REAL,
            estimated_loss REAL,
            status         TEXT        DEFAULT 'Pending',
            created_at     TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.commit()
    c.close()
    conn.close()


def register_user(full_name, email, password, farm_name, location, phone):
    conn = get_connection()
    try:
        c = _cur(conn)
        c.execute(
            """INSERT INTO users (full_name, email, password_hash, farm_name, location, phone)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (full_name, email, _hash(password), farm_name, location, phone),
        )
        uid = c.fetchone()["id"]
        conn.commit()
        return uid, None
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return None, "An account with this email already exists."
    finally:
        conn.close()


def login_user(email, password):
    conn = get_connection()
    c = _cur(conn)
    c.execute(
        "SELECT * FROM users WHERE email=%s AND password_hash=%s",
        (email, _hash(password)),
    )
    row = c.fetchone()
    conn.close()
    if row:
        return _row(row), None
    return None, "Incorrect email or password."


def get_user(user_id):
    conn = get_connection()
    c = _cur(conn)
    c.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    row = c.fetchone()
    conn.close()
    return _row(row)


def update_user(user_id, full_name, farm_name, location, phone):
    conn = get_connection()
    c = _cur(conn)
    c.execute(
        "UPDATE users SET full_name=%s, farm_name=%s, location=%s, phone=%s WHERE id=%s",
        (full_name, farm_name, location, phone, user_id),
    )
    conn.commit()
    conn.close()
