from asyncio import events

from fastapi import FastAPI, Request
from fastapi import HTTPException
from app.metrics import get_store_metrics
from app.funnel import get_funnel
from app.anomalies import get_anomalies
from app.health import health_status
from app.database import initialize_database
from app.ingestion import store_event
from typing import Any, List, Dict
from pydantic import BaseModel
from app.models import Event
from app.models import EventIngestRequest

app = FastAPI(
    title="Store Intelligence API",
    version="1.0.0"
)

@app.on_event("startup")
def startup():

    initialize_database()


@app.get("/")
def root():

    return {
        "service": "Store Intelligence API",
        "status": "running"
    }

class EventBatch(BaseModel):
    events: List[Dict[str, Any]]
@app.post("/events/ingest")
def ingest_events(batch: EventBatch):

    print("INGEST ENDPOINT HIT")
    print(events)
    accepted = 0
    rejected = 0
    duplicates = 0
    errors = []

    for idx, event in enumerate(batch.events):

        try:
            status = store_event(event)

            if status == "accepted":
                accepted += 1

            elif status == "duplicate":
                duplicates += 1

        except Exception as e:

            rejected += 1

            errors.append({
                "index": idx,
                "error": str(e)
            })

    return {
        "accepted": accepted,
        "rejected": rejected,
        "duplicates": duplicates,
        "errors": errors
    }
@app.get("/stores/{store_id}/metrics")
def metrics(store_id: str):

    return get_store_metrics(store_id)


@app.get("/stores/{store_id}/funnel")
def funnel(store_id: str):

    return get_funnel(store_id)


@app.get("/stores/{store_id}/anomalies")
def anomalies(store_id: str):

    return get_anomalies(store_id)


@app.get("/health")
def health():
    return health_status()