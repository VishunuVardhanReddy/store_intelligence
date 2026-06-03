from app.database import get_connection


def get_funnel(store_id):

    conn = get_connection()
    cur = conn.cursor()

    # Unique visitors entered store
    entries = cur.execute("""
        SELECT COUNT(DISTINCT id_token)
        FROM sessions
        WHERE store_id=?
        AND is_staff=0
    """, (store_id,)).fetchone()[0]

    # Unique visitors who visited zones
    zone_visitors = min(
        entries,
        cur.execute("""
            SELECT COUNT(DISTINCT track_id)
            FROM zone_visits
            WHERE store_id=?
        """, (store_id,)).fetchone()[0]
    )

    # Unique customers reaching billing
    billing = cur.execute("""
        SELECT COUNT(DISTINCT track_id)
        FROM queue_events
        WHERE store_id=?
    """, (store_id,)).fetchone()[0]

    # Converted visitors
    purchases = cur.execute("""
        SELECT COUNT(DISTINCT id_token)
        FROM sessions
        WHERE store_id=?
        AND converted=1
    """, (store_id,)).fetchone()[0]

    conn.close()

    return {
        "entry": entries,
        "zone_visit": zone_visitors,
        "billing": billing,
        "purchase": purchases
    }


def build_funnel(events, store_id):

    entries = set()
    zones = set()
    billing = set()
    purchases = set()

    for e in events:

        if e.get("store_id") != store_id:
            continue

        if e.get("event_type") == "entry":

            if e.get("id_token"):
                entries.add(
                    e["id_token"]
                )

        elif e.get("event_type") == "zone_entered":

            if e.get("track_id") is not None:
                zones.add(
                    str(e["track_id"])
                )

        elif e.get("event_type") == "queue_completed":

            if e.get("track_id") is not None:
                billing.add(
                    str(e["track_id"])
                )

                if e.get("id_token"):
                    purchases.add(
                        e["id_token"]
                    )

    return {
        "entry": len(entries),
        "zone_visit": len(zones),
        "billing": len(billing),
        "purchase": len(purchases)
    }