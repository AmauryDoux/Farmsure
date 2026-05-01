from datetime import datetime
from .connection import get_connection, _cur, _row


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
