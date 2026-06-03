# pipeline/detect.py
from datetime import datetime
import time
import cv2
from ultralytics import YOLO
from tracker import SessionTracker
from emit import EventEmitter
inside_zone={}
last_event_time = {}
visitor_state = {}
MODEL = YOLO("yolov8n.pt")
tracker = SessionTracker()
emitter = EventEmitter(
    "events.jsonl"
)
ENTRANCE_ZONE = (
    1450,  # x1
    150,   # y1
    1910,  # x2
    900    # y2
)
def process_video(
    video_path,
    store_id="ST1008"
):
    cap = cv2.VideoCapture(video_path)
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
        if not results:
            continue
        boxes = results[0].boxes
        if boxes is None:
            continue
        for box in boxes:
            if box.id is None:
                continue
            track_id = int(box.id.item())
            x1, y1, x2, y2 = box.xyxy[0]
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            x1z, y1z, x2z, y2z = ENTRANCE_ZONE
            current_inside = (
                x1z <= center_x <= x2z
                and
                y1z <= center_y <= y2z
            )
            cv2.circle(
                frame,
                (center_x, center_y),
                5,
                (0,255,0),
                -1
            )
            cv2.imshow("Entry Camera", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            token = tracker.get_token(track_id)
            if track_id not in inside_zone:
                inside_zone[track_id] = current_inside
            else:
                previous_inside = inside_zone[track_id]
                if not previous_inside and current_inside:
                    if visitor_state.get(track_id) != "INSIDE":
                        visitor_state[track_id] = "INSIDE"
                    print(f"ENTRY: {token}")
                    emitter.emit({
                        "event_type": "entry",
                        "id_token": token,
                        "store_id": store_id,
                        "camera_id": "CAM3",
                        "event_time": str(datetime.utcnow()),
                        "is_staff": False,
                        "gender_pred": "UNKNOWN",
                        "age_pred": None,
                        "age_bucket": "UNKNOWN",
                        "is_face_hidden": True,
                        "group_id": None,
                        "group_size": None
                    })
                elif previous_inside and not current_inside:
                    if visitor_state.get(track_id) != "OUTSIDE":
                        visitor_state[track_id] = "OUTSIDE"
                    print(f"EXIT: {token}")
                    emitter.emit({
                        "event_type": "exit",
                        "id_token": token,
                        "store_id": store_id,
                        "camera_id": "CAM3",
                        "event_time": str(datetime.utcnow()),
                        "is_staff": False,
                        "gender_pred": "UNKNOWN",
                        "age_pred": None,
                        "age_bucket": "UNKNOWN",
                        "is_face_hidden": True,
                        "group_id": None,
                        "group_size": None
                })
                inside_zone[track_id] = current_inside        
    cap.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    process_video(
        "../Store 1/CAM 3 - entry.mp4",
        "ST1008"
    )