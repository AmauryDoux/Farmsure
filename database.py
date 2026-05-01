import psycopg2
import psycopg2.extras
import psycopg2.errors
import hashlib
import os
from datetime import datetime, date

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://farmsure:farmsure@localhost:5432/farmsure",
)


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def _cur(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def _row(row):
    if row is None:
        return None
    d = dict(row)
    for k, v in d.items():
        if hasattr(v, "isoformat"):
            d[k] = v.isoformat()
    return d


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


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── Admin auth ────────────────────────────────────────────────────────────────

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


# ── Back-office claim queries ─────────────────────────────────────────────────

def get_all_claims(status_filter=None):
    conn = get_connection()
    c = _cur(conn)
    base = """
        SELECT
            cl.id, cl.user_id, cl.claim_number, cl.crop_type, cl.issue_type,
            cl.description, cl.incident_date, cl.affected_acres, cl.estimated_loss,
            cl.status, cl.created_at,
            u.full_name, u.email AS user_email, u.farm_name, u.location, u.phone
        FROM claims cl
        JOIN users u ON cl.user_id = u.id
    """
    if status_filter and status_filter != "All":
        c.execute(base + " WHERE cl.status=%s ORDER BY cl.created_at DESC", (status_filter,))
    else:
        c.execute(base + " ORDER BY cl.created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [_row(r) for r in rows]


def update_claim_status(claim_id, new_status):
    conn = get_connection()
    c = _cur(conn)
    c.execute("UPDATE claims SET status=%s WHERE id=%s", (new_status, claim_id))
    conn.commit()
    conn.close()


def get_all_claim_stats():
    conn = get_connection()
    c = _cur(conn)
    c.execute("""
        SELECT
            COUNT(*)                                                AS total,
            SUM(CASE WHEN status='Pending'      THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN status='Under Review' THEN 1 ELSE 0 END) AS under_review,
            SUM(CASE WHEN status='Approved'     THEN 1 ELSE 0 END) AS approved,
            SUM(CASE WHEN status='Rejected'     THEN 1 ELSE 0 END) AS rejected,
            COALESCE(SUM(estimated_loss), 0)                       AS total_claimed
        FROM claims
    """)
    row = c.fetchone()
    conn.close()
    return _row(row)


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


def create_claim(user_id, crop_type, issue_type, description, incident_date, affected_acres, estimated_loss):
    conn = get_connection()
    c = _cur(conn)
    c.execute("SELECT COUNT(*) AS cnt FROM claims")
    count = c.fetchone()["cnt"]
    claim_number = f"CLM-{datetime.now().year}-{str(count + 1).zfill(5)}"
    c.execute(
        """INSERT INTO claims
           (user_id, claim_number, crop_type, issue_type, description,
            incident_date, affected_acres, estimated_loss)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (user_id, claim_number, crop_type, issue_type, description,
         incident_date, affected_acres, estimated_loss),
    )
    conn.commit()
    conn.close()
    return claim_number


def get_user_claims(user_id):
    conn = get_connection()
    c = _cur(conn)
    c.execute(
        "SELECT * FROM claims WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,),
    )
    rows = c.fetchall()
    conn.close()
    return [_row(r) for r in rows]


def get_claim_stats(user_id):
    conn = get_connection()
    c = _cur(conn)
    c.execute(
        """SELECT
               COUNT(*)                                                  AS total,
               SUM(CASE WHEN status='Pending'      THEN 1 ELSE 0 END)   AS pending,
               SUM(CASE WHEN status='Under Review' THEN 1 ELSE 0 END)   AS under_review,
               SUM(CASE WHEN status='Approved'     THEN 1 ELSE 0 END)   AS approved,
               SUM(CASE WHEN status='Rejected'     THEN 1 ELSE 0 END)   AS rejected,
               COALESCE(SUM(estimated_loss), 0)                         AS total_claimed
           FROM claims WHERE user_id=%s""",
        (user_id,),
    )
    row = c.fetchone()
    conn.close()
    return _row(row)
