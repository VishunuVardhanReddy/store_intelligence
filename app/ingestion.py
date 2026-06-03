import json
import hashlib
import uuid

from app.database import get_connection

EVENT_DB = []

def ingest_events(events):

    inserted = 0

    for event in events:

        if "event_id" not in event:
            event["event_id"] = str(uuid.uuid4())

        duplicate = any(
            e["event_id"] == event["event_id"]
            for e in EVENT_DB
        )

        if duplicate:
            continue

        EVENT_DB.append(event)
        inserted += 1

    return inserted

def generate_hash(event):

    payload = json.dumps(
        event,
        sort_keys=True,
        default=str
    )

    return hashlib.sha256(
        payload.encode()
    ).hexdigest()

def store_event(event):
    
    print("\nRECEIVED EVENT:")
    print(event)
    event_hash = generate_hash(event)

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO events
            (
                event_hash,
                event_type,
                store_id,
                payload
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                event_hash,
                event["event_type"],
                event.get("store_id"),
                json.dumps(event)
            )
        )

        # ENTRY EVENT
        if event["event_type"] == "entry":

            cursor.execute(
                """
                INSERT OR IGNORE INTO sessions
                (
                    id_token,
                    store_id,
                    entry_time,
                    is_staff
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    event["id_token"],
                    event["store_id"],
                    event["event_time"],
                    int(event.get("is_staff", False))
                )
            )

        # EXIT EVENT
        elif event["event_type"] == "exit":

            cursor.execute(
                """
                UPDATE sessions
                SET exit_time=?
                WHERE id_token=?
                """,
                (
                    event["event_time"],
                    event["id_token"]
                )
            )

        # ZONE EVENT
        elif event["event_type"] == "zone_entered":

            cursor.execute(
                """
                INSERT INTO zone_visits
                (
                    track_id,
                    store_id,
                    zone_id,
                    zone_name,
                    enter_time
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event["track_id"],
                    event["store_id"],
                    event["zone_id"],
                    event["zone_name"],
                    event["event_time"]
                )
            )

        # QUEUE COMPLETE
        elif event["event_type"] == "queue_completed":

            cursor.execute(
                """
                INSERT INTO queue_events
                (
                    queue_event_id,
                    track_id,
                    store_id,
                    wait_seconds,
                    abandoned
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event["queue_event_id"],
                    event["track_id"],
                    event["store_id"],
                    event["wait_seconds"],
                    int(event["abandoned"])
                )
            )

            cursor.execute(
                """
                UPDATE sessions
                SET converted=1
                WHERE rowid = (
                SELECT rowid
                FROM sessions
                WHERE store_id=?
                AND converted=0
                LIMIT 1
                )
                """,
                (
                    event["store_id"],
                )
            )
            print("Marked one visitor as converted")

        conn.commit()

        return "accepted"

    except Exception as e:

        print("DB ERROR:", e)
        print("FAILING EVENT:", event)
        return "duplicate"

    finally:

        conn.close()