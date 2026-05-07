# db.py
import psycopg2
import psycopg2.extras
from config import DB_HOST, DB_PORT, DB_NAME

def get_connection(username, password):
    """Get a DB connection using the actual DB user credentials."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=username,
        password=password,
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def query(conn, sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()

def execute(conn, sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
    conn.commit()

def query_one(conn, sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchone()