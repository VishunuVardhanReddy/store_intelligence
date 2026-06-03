import requests

payload = {
    "events": [
        {
            "event_type": "entry",
            "store_id": "ST1008",
            "camera_id": "CAM3",
            "event_time": "2026-06-03T16:30:00"
        }
    ]
}

r = requests.post(
    "http://127.0.0.1:8000/events/ingest",
    json=payload
)

print(r.status_code)
print(r.text)