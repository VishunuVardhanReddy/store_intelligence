# pipeline/cam2_detect.py

from datetime import datetime
import json
import cv2
from ultralytics import YOLO

from emit import EventEmitter

MODEL = YOLO("yolov8n.pt")

VIDEO = "../Store 1/CAM 2 - zone.mp4"

emitter = EventEmitter(
    "events.jsonl"
)

# ==========================================
# BRAND ZONES
# ==========================================

ZONES = {

    "ALPS": [
        (250, 0),
        (450, 0),
        (450, 1080),
        (250, 1080)
    ],

    "LOREAL": [
        (450, 0),
        (600, 0),
        (600, 1080),
        (450, 1080)
    ],

    "MARS": [
        (600, 0),
        (750, 0),
        (750, 1080),
        (600, 1080)
    ],

    "SWISS_BEAUTY": [
        (750, 0),
        (950, 0),
        (950, 1080),
        (750, 1080)
    ],

    "LAKME": [
        (950, 0),
        (1150, 0),
        (1150, 1080),
        (950, 1080)
    ],

    "FACES_CANADA": [
        (1150, 0),
        (1450, 0),
        (1450, 1080),
        (1150, 1080)
    ],

    "MAYBELLINE": [
        (1450, 0),
        (1920, 0),
        (1920, 1080),
        (1450, 1080)
    ]
}

# ==========================================
# HELPERS
# ==========================================

visitor_zone = {}
zone_enter_time = {}


def point_in_zone(x, y, zone):

    x_min = min(p[0] for p in zone)
    x_max = max(p[0] for p in zone)

    y_min = min(p[1] for p in zone)
    y_max = max(p[1] for p in zone)

    return (
        x_min <= x <= x_max
        and
        y_min <= y <= y_max
    )


# ==========================================
# VIDEO
# ==========================================

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

            current_zone = None

            for zone_name, polygon in ZONES.items():

                if point_in_zone(
                    center_x,
                    center_y,
                    polygon
                ):
                    current_zone = zone_name
                    break

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
                (
                    center_x,
                    center_y - 10
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                1
            )

            # ==================================
            # FIRST TIME
            # ==================================

            if track_id not in visitor_zone:

                visitor_zone[track_id] = current_zone

                zone_enter_time[track_id] = (
                    datetime.utcnow()
                )

                continue

            previous_zone = visitor_zone[track_id]

            # ==================================
            # ZONE CHANGE
            # ==================================

            if (
                previous_zone != current_zone
                and
                current_zone is not None
            ):

                dwell_seconds = (
                    datetime.utcnow()
                    -
                    zone_enter_time[track_id]
                ).total_seconds()

                print(
                    f"{track_id}: "
                    f"{previous_zone}"
                    f" -> "
                    f"{current_zone}"
                )

                # ==============================
                # EXIT EVENT
                # ==============================

                exit_event = {

                    "event_type":
                    "zone_exited",

                    "track_id":
                    track_id,

                    "store_id":
                    "ST1008",

                    "camera_id":
                    "CAM2",

                    "zone_id":
                    previous_zone,

                    "zone_name":
                    previous_zone,

                    "event_time":
                    str(datetime.utcnow()),

                    "dwell_seconds":
                    round(
                        dwell_seconds,
                        2
                    )
                }

                # ==============================
                # ENTER EVENT
                # ==============================

                enter_event = {

                    "event_type":
                    "zone_entered",

                    "track_id":
                    track_id,

                    "store_id":
                    "ST1008",

                    "camera_id":
                    "CAM2",

                    "zone_id":
                    current_zone,

                    "zone_name":
                    current_zone,

                    "event_time":
                    str(datetime.utcnow())
                }

                # ==================================
                # SAVE + SEND TO API
                # ==================================

                emitter.emit(
                    exit_event
                )

                emitter.emit(
                    enter_event
                )

                visitor_zone[track_id] = (
                    current_zone
                )

                zone_enter_time[track_id] = (
                    datetime.utcnow()
                )

    # ==================================
    # DRAW ZONES
    # ==================================

    colors = [

        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),

        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),

        (200, 200, 200)
    ]

    for idx, (
        zone_name,
        polygon
    ) in enumerate(
        ZONES.items()
    ):

        x1 = polygon[0][0]
        x2 = polygon[1][0]

        cv2.rectangle(
            frame,
            (x1, 0),
            (x2, 1080),
            colors[idx],
            2
        )

        cv2.putText(
            frame,
            zone_name,
            (x1 + 20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            colors[idx],
            2
        )

    cv2.imshow(
        "CAM2 Zone Analytics",
        frame
    )

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()

cv2.destroyAllWindows()