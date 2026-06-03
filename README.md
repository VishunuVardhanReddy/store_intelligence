# Store Intelligence System

## Overview

AI-powered retail analytics system using YOLOv8, FastAPI, and SQLite.

## Features

- Entry/Exit Analytics (CAM3)
- Shelf Zone Analytics (CAM1)
- Brand Zone Analytics (CAM2)
- Billing Queue Analytics (CAM5)
- Metrics API
- Funnel API
- Anomaly Detection API

## Setup

pip install -r requirements.txt

## Run API

uvicorn app.main:app --reload

## Run Cameras

python pipeline/detect.py
python pipeline/cam1_detect.py
python pipeline/cam2_detect.py
python pipeline/cam5_detect.py

## APIs

POST /events/ingest
GET /stores/{store_id}/metrics
GET /stores/{store_id}/funnel
GET /stores/{store_id}/anomalies
GET /health