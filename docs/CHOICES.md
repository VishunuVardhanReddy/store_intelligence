# Design Choices

## Why YOLOv8

YOLOv8 provides:
- Fast inference
- Person detection
- Built-in tracking support

## Why SQLite

Chosen because:
- Lightweight
- No server setup
- Easy local testing

## Why FastAPI

Chosen because:
- Automatic Swagger docs
- Type validation
- Fast development

## Tracking Strategy

Used YOLO tracking IDs to:
- Detect entries/exits
- Track zone movement
- Measure queue wait time

## Event Driven Design

All cameras emit events to a common ingestion API.

Benefits:
- Decoupled architecture
- Easy analytics generation
- Scalable design