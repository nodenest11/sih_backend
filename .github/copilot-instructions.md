You are building the backend for a Smart Tourist Safety & Incident Response System using FastAPI + PostgreSQL.
Your job is to:

1. Setup

Use FastAPI framework with PostgreSQL database.

ORM: SQLAlchemy.

Run with Uvicorn.

Provide requirements.txt.

2. Database Models

Tourist: id, name, contact, trip_info, emergency_contact, safety_score (0–100).

Location: id, tourist_id, latitude, longitude, timestamp.

Alert: id, tourist_id, type (panic | geofence), message, timestamp, status (active | resolved).

3. APIs

Tourist Management

POST /tourists/register → Register a tourist (store in DB).

GET /tourists/{id} → Get tourist details (safety score, trip info, emergency contact).

Location Management

POST /locations/update → Tourist sends current location (lat/lon).

Example request:

{ "tourist_id": 1, "latitude": 28.61, "longitude": 77.23 }


GET /locations/all → Return latest location of all tourists.

Alerts Management

POST /alerts/panic → Create panic alert.

{ "tourist_id": 1, "latitude": 28.61, "longitude": 77.23 }


POST /alerts/geofence → Create geofence alert.

GET /alerts → Get all active alerts.

PUT /alerts/{id}/resolve → Mark alert as resolved.

Safety Score Calculation

Start simple:

Panic = -40

Enter risky zone = -20

Staying safe for 1 hr = +10

Update safety score in DB.

4. Dataset

Create sample dataset with 100 dummy tourists, random locations (Delhi, Goa, Shillong, etc.).

Mark 5–10 restricted zones (geo-fence polygons).

Store them in DB for testing.

5. Communication

Mobile App → uses REST APIs (JSON).

Web Dashboard → uses REST APIs (JSON).

Support CORS enabled.

6. Extra

Add Swagger docs (/docs).

Seed database with demo data on startup.