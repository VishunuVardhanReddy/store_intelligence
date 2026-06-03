from app.metrics import get_store_metrics

def test_metrics():
    result = get_store_metrics("ST1008")

    assert "unique_visitors" in result
    assert "conversion_rate" in result