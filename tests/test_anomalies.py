from app.anomalies import get_anomalies

def test_anomalies():
    result = get_anomalies("ST1008")

    assert isinstance(result, list)