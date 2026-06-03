from app.database import get_connection

def detect_anomalies(events):

    anomalies = []

    queue_events = 0

    for e in events:

        if e["event_type"] == "queue_join":
            queue_events += 1

    if queue_events > 10:

        anomalies.append({

            "type":
            "QUEUE_SPIKE",

            "severity":
            "WARN",

            "suggested_action":
            "Open additional billing counter"

        })

    return anomalies

def get_anomalies(store_id):

    conn = get_connection()
    cur = conn.cursor()

    anomalies = []

    avg_wait = cur.execute("""
        SELECT AVG(wait_seconds)
        FROM queue_events
        WHERE store_id=?
    """, (store_id,)).fetchone()[0]

    if avg_wait and avg_wait > 60:

        anomalies.append({
            "severity": "WARN",
            "type": "QUEUE_SPIKE",
            "suggested_action":
            "Increase billing capacity."
        })

    abandoned = cur.execute("""
        SELECT COUNT(*)
        FROM queue_events
        WHERE store_id=?
        AND abandoned=1
    """, (store_id,)).fetchone()[0]

    if abandoned > 5:

        anomalies.append({
            "severity": "CRITICAL",
            "type": "HIGH_ABANDONMENT",
            "suggested_action":
            "Investigate long billing delays."
        })

    conn.close()

    return anomalies