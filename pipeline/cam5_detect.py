# pipeline/cam5_detect.py

from datetime import datetime
import uuid
import requests
import cv2
from ultralytics import YOLO

MODEL = YOLO("yolov8n.pt")

VIDEO = "../Store 1/CAM 5 - billing.mp4"

API_URL = "http://127.0.0.1:8000/events/ingest"

# =====================================
# ZONES
# =====================================

BILLING_ZONE = (
    350,
    250,
    950,
    1080
)

QUEUE_ZONE = (
    0,
    100,
    350,
    1080
)

# =====================================
# TRACKING
# =====================================

customer_state = {}
queue_join_time = {}
queue_frames = {}

# =====================================
# SEND EVENT
# =====================================

def send_event(event):

    payload = {
        "events": [event]
    }

    try:

        response = requests.post(
            API_URL,
            json=payload,
            timeout=5
        )

        print(
            f"API Status: {response.status_code}"
        )

        print(
            response.text
        )

    except Exception as e:

        print(
            "API ERROR:",
            str(e)
        )

# =====================================
# VIDEO
# =====================================

cap = cv2.VideoCapture(VIDEO)

frame_count = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame_count += 1

    if frame_count % 100 == 0:

        print(
            f"Processed {frame_count} frames"
        )

    results = MODEL.track(
        frame,
        persist=True,
        classes=[0],
        verbose=False
    )

    if results and results[0].boxes is not None:

        for box in results[0].boxes:

            if box.id is None:
                continue

            track_id = int(
                box.id.item()
            )

            x1, y1, x2, y2 = box.xyxy[0]

            center_x = int(
                (x1 + x2) / 2
            )

            center_y = int(
                (y1 + y2) / 2
            )

            cv2.circle(
                frame,
                (center_x, center_y),
                5,
                (0, 255, 0),
                -1
            )

            cv2.putText(
                frame,
                str(track_id),
                (center_x, center_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0,255,255),
                1
            )

            # ======================
            # Zone Membership
            # ======================

            in_queue = (
                QUEUE_ZONE[0]
                <= center_x
                <= QUEUE_ZONE[2]
                and
                QUEUE_ZONE[1]
                <= center_y
                <= QUEUE_ZONE[3]
            )

            in_billing = (
                BILLING_ZONE[0]
                <= center_x
                <= BILLING_ZONE[2]
                and
                BILLING_ZONE[1]
                <= center_y
                <= BILLING_ZONE[3]
            )

            current_state = customer_state.get(
                track_id,
                "NONE"
            )

            # ======================
            # Queue Stability
            # ======================

            if in_queue:

                queue_frames[track_id] = (
                    queue_frames.get(
                        track_id,
                        0
                    ) + 1
                )

            else:

                queue_frames[track_id] = 0

            # ======================
            # QUEUE JOIN
            # ======================

            if (
                queue_frames[track_id] >= 15
                and
                current_state == "NONE"
            ):

                customer_state[
                    track_id
                ] = "QUEUE"

                queue_join_time[
                    track_id
                ] = datetime.utcnow()

                print(
                    f"QUEUE_JOIN: {track_id}"
                )

                queue_depth = sum(
                    1
                    for s in customer_state.values()
                    if s == "QUEUE"
                )

                event = {
                    "event_type":
                        "billing_queue_join",

                    "track_id":
                        track_id,

                    "store_id":
                        "ST1008",

                    "camera_id":
                        "CAM5",

                    "queue_depth":
                        queue_depth,

                    "event_time":
                        str(
                            datetime.utcnow()
                        )
                }

                send_event(event)

            # ======================
            # QUEUE COMPLETED
            # ======================

            elif (
                current_state == "QUEUE"
                and
                in_billing
            ):

                customer_state[
                    track_id
                ] = "BILLING"

                wait_seconds = (
                    datetime.utcnow()
                    -
                    queue_join_time[
                        track_id
                    ]
                ).total_seconds()

                print(
                    f"QUEUE_COMPLETED: {track_id}"
                )

                event = {

                    "queue_event_id":
                        str(
                            uuid.uuid4()
                        ),

                    "event_type":
                        "queue_completed",

                    "track_id":
                        track_id,

                    "store_id":
                        "ST1008",

                    "camera_id":
                        "CAM5",

                    "wait_seconds":
                        round(
                            wait_seconds,
                            2
                        ),

                    "abandoned":
                        False,

                    "event_time":
                        str(
                            datetime.utcnow()
                        )
                }

                send_event(event)

            # ======================
            # QUEUE ABANDONED
            # ======================

            elif (
                current_state == "QUEUE"
                and
                not in_queue
                and
                not in_billing
            ):

                customer_state[
                    track_id
                ] = "LEFT"

                wait_seconds = (
                    datetime.utcnow()
                    -
                    queue_join_time[
                        track_id
                    ]
                ).total_seconds()

                print(
                    f"QUEUE_ABANDONED: {track_id}"
                )

                event = {

                    "queue_event_id":
                        str(
                            uuid.uuid4()
                        ),

                    "event_type":
                        "queue_abandoned",

                    "track_id":
                        track_id,

                    "store_id":
                        "ST1008",

                    "camera_id":
                        "CAM5",

                    "wait_seconds":
                        round(
                            wait_seconds,
                            2
                        ),

                    "abandoned":
                        True,

                    "event_time":
                        str(
                            datetime.utcnow()
                        )
                }

                send_event(event)

    # =====================================
    # Draw Zones
    # =====================================

    cv2.rectangle(
        frame,
        (QUEUE_ZONE[0], QUEUE_ZONE[1]),
        (QUEUE_ZONE[2], QUEUE_ZONE[3]),
        (0,0,255),
        2
    )

    cv2.rectangle(
        frame,
        (BILLING_ZONE[0], BILLING_ZONE[1]),
        (BILLING_ZONE[2], BILLING_ZONE[3]),
        (0,255,0),
        2
    )

    cv2.putText(
        frame,
        "QUEUE",
        (20,80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,0,255),
        2
    )

    cv2.putText(
        frame,
        "BILLING",
        (370,220),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    queue_depth = sum(
        1
        for s in customer_state.values()
        if s == "QUEUE"
    )

    cv2.putText(
        frame,
        f"Queue Depth: {queue_depth}",
        (50,50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255,255,0),
        2
    )

    cv2.imshow(
        "CAM5 Billing",
        frame
    )

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()