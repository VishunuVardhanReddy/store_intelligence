from app.database import get_connection

def calculate_metrics(events, store_id):

    entries = set()
    purchases = set()

    zone_visits = 0

    for e in events:

        if e["store_id"] != store_id:
            continue

        if e["event_type"] == "entry":
            entries.add(e["id_token"])

        elif e["event_type"] == "zone_entered":
            zone_visits += 1

        elif e["event_type"] == "queue_completed":

            if "track_id" in e:
                purchases.add(
                    str(e["track_id"])
                )

    visitors = len(entries)

    conversion_rate = 0

    if visitors > 0:
        conversion_rate = (
            len(purchases)
            /
            visitors
        ) * 100

    return {
        "unique_visitors": visitors,
        "conversion_rate": round(
            conversion_rate,
            2
        ),
        "zone_visits": zone_visits
    }

def get_store_metrics(store_id):

    conn = get_connection()
    cur = conn.cursor()

    visitors = cur.execute("""
        SELECT COUNT(*)
        FROM sessions
        WHERE store_id=?
        AND is_staff=0
    """, (store_id,)).fetchone()[0]

    converted = cur.execute("""
        SELECT COUNT(*)
        FROM sessions
        WHERE store_id=?
        AND converted=1
        AND is_staff=0
    """, (store_id,)).fetchone()[0]

    conversion_rate = 0

    if visitors:
        conversion_rate = round(
            (converted / visitors) * 100,
            2
        )

    avg_wait = cur.execute("""
        SELECT AVG(wait_seconds)
        FROM queue_events
        WHERE store_id=?
        AND abandoned=0
    """, (store_id,)).fetchone()[0]

    conn.close()

    return {
        "store_id": store_id,
        "unique_visitors": visitors,
        "converted_visitors": converted,
        "conversion_rate": conversion_rate,
        "avg_queue_wait_seconds": avg_wait or 0
    }