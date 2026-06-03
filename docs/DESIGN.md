# Store Intelligence System Design

## Architecture

Cameras:
- CAM1: Shelf Zone Analytics
- CAM2: Brand Zone Analytics
- CAM3: Entry/Exit Tracking
- CAM5: Billing Queue Analytics

Pipeline:
Camera → YOLOv8 Detection → EventEmitter → FastAPI → SQLite Database

## Components

### CAM3
Tracks store entries and exits.

### CAM1
Tracks movement between shelf zones:
- LEFT_SHELF
- CENTER_SHELF
- RIGHT_SHELF

### CAM2
Tracks movement between brand zones:
- ALPS
- LOREAL
- MARS
- SWISS_BEAUTY
- LAKME
- FACES_CANADA

### CAM5
Tracks:
- Queue Join
- Queue Completed
- Queue Abandoned

## Storage

SQLite database:
- events
- sessions
- zone_visits
- queue_events

## APIs

POST /events/ingest
GET /stores/{store_id}/metrics
GET /stores/{store_id}/funnel
GET /stores/{store_id}/anomalies
GET /health