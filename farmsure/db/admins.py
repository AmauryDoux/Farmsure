from .connection import get_connection, _cur, _row
from .users import _hash


def init_admin_db():
    conn = get_connection()
    c = _cur(conn)
    c.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id            SERIAL PRIMARY KEY,
            full_name     TEXT        NOT NULL,
            email         TEXT        UNIQUE NOT NULL,
            password_hash TEXT        NOT NULL,
            created_at    TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.commit()
    c.execute("SELECT COUNT(*) AS cnt FROM admins")
    if c.fetchone()["cnt"] == 0:
        c.execute(
            "INSERT INTO admins (full_name, email, password_hash) VALUES (%s, %s, %s)",
            ("Sarah Mitchell", "admin@farmsure.com", _hash("admin123")),
        )
        conn.commit()
    c.close()
    conn.close()


def login_admin(email, password):
    conn = get_connection()
    c = _cur(conn)
    c.execute(
        "SELECT * FROM admins WHERE email=%s AND password_hash=%s",
        (email, _hash(password)),
    )
    row = c.fetchone()
    conn.close()
    if row:
        return _row(row), None
    return None, "Incorrect email or password."
