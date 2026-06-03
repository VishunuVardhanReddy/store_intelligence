# pipeline/tracker.py

from collections import defaultdict

class SessionTracker:

    def __init__(self):

        self.track_to_token = {}
        self.next_id = 60000

    def get_token(self, track_id):

        if track_id not in self.track_to_token:

            self.next_id += 1

            self.track_to_token[track_id] = (
                f"ID_{self.next_id}"
            )

        return self.track_to_token[track_id]