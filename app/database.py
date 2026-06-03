import sqlite3

DB_PATH = "store_intelligence.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


def initialize_database():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_hash TEXT UNIQUE,
        event_type TEXT,
        store_id TEXT,
        payload TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions(
        id_token TEXT PRIMARY KEY,
        store_id TEXT,
        entry_time TEXT,
        exit_time TEXT,
        is_staff INTEGER DEFAULT 0,
        converted INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS zone_visits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id INTEGER,
        store_id TEXT,
        zone_id TEXT,
        zone_name TEXT,
        enter_time TEXT,
        exit_time TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS queue_events(
        queue_event_id TEXT PRIMARY KEY,
        track_id INTEGER,
        store_id TEXT,
        wait_seconds INTEGER,
        abandoned INTEGER
    )
    """)

    conn.commit()
    conn.close()