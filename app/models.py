from typing import Optional, List, Union, Dict
from pydantic import BaseModel
from datetime import datetime
from typing import Any

class EventIngestRequest(BaseModel):
    events: List[Dict[str, Any]]


class EntryExitEvent(BaseModel):
    event_type: str
    id_token: str
    store_code: str
    camera_id: str
    event_timestamp: datetime

    is_staff: bool = False

    gender_pred: Optional[str] = "UNKNOWN"
    age_pred: Optional[int] = None
    age_bucket: Optional[str] = "UNKNOWN"

    is_face_hidden: bool = True

    group_id: Optional[str] = None
    group_size: Optional[int] = None


class ZoneEvent(BaseModel):
    event_type: str

    track_id: int

    store_id: str
    camera_id: str

    zone_id: str
    zone_name: str
    zone_type: str

    is_revenue_zone: str

    event_time: datetime

    zone_hotspot_x: float
    zone_hotspot_y: float

    gender: Optional[str] = "UNKNOWN"
    age: Optional[int] = None
    age_bucket: Optional[str] = "UNKNOWN"


class QueueEvent(BaseModel):
    queue_event_id: str

    event_type: str

    track_id: int

    store_id: str
    camera_id: str

    zone_id: str
    zone_name: str
    zone_type: str

    is_revenue_zone: str

    queue_join_ts: datetime

    queue_served_ts: Optional[datetime] = None
    queue_exit_ts: datetime

    wait_seconds: int

    queue_position_at_join: int

    abandoned: bool

    zone_hotspot_x: float
    zone_hotspot_y: float

    gender: Optional[str] = "UNKNOWN"
    age: Optional[int] = None
    age_bucket: Optional[str] = "UNKNOWN"


EventUnion = Union[
    EntryExitEvent,
    ZoneEvent,
    QueueEvent
]


class IngestResponse(BaseModel):
    accepted: int
    rejected: int
    duplicates: int
    errors: List[dict]


class Event(BaseModel):
    event_type: str
    store_id: str
    camera_id: str

    id_token: Optional[str] = None
    track_id: Optional[int] = None

    zone_id: Optional[str] = None
    zone_name: Optional[str] = None

    event_time: str

    zone_hotspot_x: Optional[int] = None
    zone_hotspot_y: Optional[int] = None

    metadata: Optional[Dict] = {}