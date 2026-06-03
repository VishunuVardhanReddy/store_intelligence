# pipeline/emit.py

import json
import requests

from datetime import datetime

print("LOADED EMIT.PY")
class EventEmitter:

    def __init__(self, output_file):

        self.output_file = output_file

    def emit(self, event):

        payload = {
            "events": [event]
        }

        print("\nSENDING PAYLOAD:")
        print(payload)

        try:
            response = requests.post(
                "http://127.0.0.1:8000/events/ingest",
                json=payload
            )

            print("API Status:", response.status_code)
            print("API Response:", response.text)

        except Exception as e:
            print("API Error:", str(e))

def now():

    return datetime.utcnow().isoformat()