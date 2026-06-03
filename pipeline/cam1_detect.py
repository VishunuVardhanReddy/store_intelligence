from datetime import datetime
import cv2
from ultralytics import YOLO

from emit import EventEmitter

MODEL = YOLO("yolov8n.pt")

VIDEO = "../Store 1/CAM 1 - zone.mp4"

emitter = EventEmitter("events.jsonl")

visitor_zone = {}
candidate_zone = {}
candidate_count = {}

ZONES = {

    "LEFT_SHELF": [
        (0, 0),
        (600, 0),
        (600, 1080),
        (0, 1080)
    ],

    "CENTER_SHELF": [
        (600, 0),
        (1350, 0),
        (1350, 1080),
        (600, 1080)
    ],

    "RIGHT_SHELF": [
        (1350, 0),
        (1920, 0),
        (1920, 1080),
        (1350, 1080)
    ]
}


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


cap = cv2.VideoCapture(VIDEO)

frame_count = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame_count += 1

    if frame_count % 100 == 0:
        print(f"Processed {frame_count} frames")

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

            track_id = int(box.id.item())

            x1, y1, x2, y2 = box.xyxy[0]

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

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
                (center_x, center_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                1
            )

            if track_id not in visitor_zone:

                visitor_zone[track_id] = current_zone

            else:

                previous_zone = visitor_zone[track_id]

                if current_zone is not None:

                    if track_id not in candidate_zone:

                        candidate_zone[track_id] = current_zone
                        candidate_count[track_id] = 1

                    elif candidate_zone[track_id] == current_zone:

                        candidate_count[track_id] += 1

                    else:

                        candidate_zone[track_id] = current_zone
                        candidate_count[track_id] = 1

                    if (
                        candidate_count[track_id] >= 15
                        and previous_zone != current_zone
                    ):

                        print(
                            f"{track_id}: "
                            f"{previous_zone}"
                            f" -> "
                            f"{current_zone}"
                        )

                        exit_event = {
                            "event_type": "zone_exited",
                            "track_id": track_id,
                            "store_id": "ST1008",
                            "camera_id": "CAM1",
                            "zone_id": previous_zone,
                            "zone_name": previous_zone,
                            "zone_type": "SHELF",
                            "is_revenue_zone": True,
                            "event_time": str(datetime.utcnow()),
                            "zone_hotspot_x": center_x,
                            "zone_hotspot_y": center_y
                        }

                        enter_event = {
                            "event_type": "zone_entered",
                            "track_id": track_id,
                            "store_id": "ST1008",
                            "camera_id": "CAM1",
                            "zone_id": current_zone,
                            "zone_name": current_zone,
                            "zone_type": "SHELF",
                            "is_revenue_zone": True,
                            "event_time": str(datetime.utcnow()),
                            "zone_hotspot_x": center_x,
                            "zone_hotspot_y": center_y
                        }

                        print("ZONE EXIT")
                        emitter.emit(exit_event)

                        print("ZONE ENTER")
                        emitter.emit(enter_event)

                        visitor_zone[track_id] = current_zone
                        candidate_count[track_id] = 0

    # Draw LEFT zone
    cv2.rectangle(
        frame,
        (0, 0),
        (600, 1080),
        (255, 0, 0),
        2
    )

    cv2.putText(
        frame,
        "LEFT_SHELF",
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 0),
        2
    )

    # Draw CENTER zone
    cv2.rectangle(
        frame,
        (600, 0),
        (1350, 1080),
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        "CENTER_SHELF",
        (650, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Draw RIGHT zone
    cv2.rectangle(
        frame,
        (1350, 0),
        (1920, 1080),
        (0, 0, 255),
        2
    )

    cv2.putText(
        frame,
        "RIGHT_SHELF",
        (1450, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2
    )

    cv2.imshow(
        "CAM1 Zone Analytics",
        frame
    )

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()