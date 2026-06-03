from pipeline.tracker import SessionTracker

def test_tracker():

    tracker = SessionTracker()

    token = tracker.get_token(1)

    assert token is not None