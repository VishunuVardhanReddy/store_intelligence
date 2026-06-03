from app.database import get_connection
from datetime import datetime

def health(events):

    last_event = None

    if events:
        last_event = events[-1]

    return {

        "status": "healthy",

        "last_event":
        last_event

    }

def health_status():

    conn = get_connection()
    cur = conn.cursor()

    count = cur.execute("""
        SELECT COUNT(*)
        FROM events
    """).fetchone()[0]

    conn.close()

    return {
        "status": "healthy",
        "event_count": count
    }