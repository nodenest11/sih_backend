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


anonpublic : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxZW5xd2Z1eXdpZ2hhaW5udWpoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyMDg5NTgsImV4cCI6MjA3Mzc4NDk1OH0.qztg3ZGxTCGZwDjIKlnvHtdGODdMxPxy2ntQg6GkHAs

service_rolesecret : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxZW5xd2Z1eXdpZ2hhaW5udWpoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODIwODk1OCwiZXhwIjoyMDczNzg0OTU4fQ._Z6Fk7qOP1D72rZrJwYt6_A3oMZPf5GZEF8xJ_BTKhg

supabase url : https://tqenqwfuywighainnujh.supabase.co


# 🧑‍💻 AI/ML Developer Prompt for Hybrid Tourist Safety System

You are tasked with implementing the **AI/ML layer** for the **Smart Tourist Safety Monitoring & Incident Response System**.  
Your focus: build a **hybrid pipeline** combining Rule-based + ML + Deep Learning.

---

## 📂 Data You Will Work With
You will receive **tourist movement data** from the backend in the following format:

| Field         | Type     | Description |
|---------------|----------|-------------|
| tourist_id    | UUID     | Unique ID (linked to blockchain-based digital ID) |
| latitude      | float    | Tourist current GPS latitude |
| longitude     | float    | Tourist current GPS longitude |
| altitude      | float    | GPS altitude (optional) |
| timestamp     | datetime | Time of location capture |
| speed         | float    | Speed (m/s or km/h) |
| planned_route | JSON     | Tourist’s planned itinerary (list of waypoints) |
| zone_type     | string   | Zone label (safe, risky, restricted) |

👉 Additional derived features (to be computed during preprocessing):  
- Distance travelled per minute  
- Inactivity duration  
- Deviation from planned route  

---

## ⚙️ Components of the Hybrid AI/ML Model

### 1. **Rule-Based Geo-fencing**
- Input: latitude, longitude, zone_type.  
- If `zone_type == restricted` → **instant alert**.  
- If tourist presses **SOS** → **instant alert**.  
- ✅ Works without ML, deterministic.  
- 🔑 Purpose: Immediate, zero-delay response.  

---

### 2. **Unsupervised Anomaly Detection (Isolation Forest)**
- Input features: `[distance_per_min, inactivity_duration, deviation_from_route, speed]`.  
- Algorithm: **Isolation Forest (scikit-learn)**.  
- Output: **Anomaly Score (0 = normal, 1 = anomaly)**.  
- ✅ Detects rare/unusual patterns like sudden inactivity or unusual speed.  
- 🔑 Purpose: Early warning system when no labels exist.  

---

### 3. **Sequence Modeling (LSTM/GRU Autoencoder)**
- Input: Sequential tourist movement data (last N minutes as sliding window).  
- Algorithm: **LSTM/GRU Autoencoder (PyTorch)**.  
- Process:  
  - Model learns “normal sequence” of movement.  
  - If reconstruction error is high → anomaly.  
- Output: **Temporal Risk Score (0–1)**.  
- ✅ Detects gradual risks (e.g., drifting off itinerary, long inactivity in unsafe areas).  
- 🔑 Purpose: Adds **time-series context** → reduces false positives.  

---

### 4. **Supervised Classification (LightGBM/XGBoost – Future Stage)**
- Input features: `[distance_per_min, inactivity_duration, deviation_from_route, speed, anomaly_scores]`.  
- Training Data: Labeled incidents (Safe, Warning, Critical) collected after deployment.  
- Algorithm: **LightGBM or XGBoost**.  
- Output: **Severity Classification (Safe, Warning, Critical)**.  
- ✅ Learns from history, reduces false alerts.  
- 🔑 Purpose: Long-term improvement once real incident data is available.  

---

### 5. **Safety Scoring & Alert Fusion**
- Combine results from all models:  
  - Geo-fence → Binary (Safe / Restricted)  
  - Isolation Forest → Anomaly Score  
  - LSTM/GRU → Temporal Risk Score  
  - LightGBM → Severity Classification (future)  
- Compute **Safety Score (0–100):**  
  - > 80 → Safe  
  - 50–80 → Warning (notify tourist)  
  - < 50 → Critical (notify police + family, auto E-FIR)  
- 🔑 Purpose: Unified decision engine for alerts.  

---

## ✅ Expected Workflow
1. Tourist sends location → Backend forwards to AI pipeline.  
2. Data is **preprocessed** into features.  
3. Models run in sequence:  
   - Geo-fence → instant checks.  
   - Isolation Forest → anomaly score.  
   - LSTM/GRU → sequence anomaly score.  
   - LightGBM (future) → severity classification.  
4. Scores fused → Safety Score calculated.  
5. System decides: **No action / Tourist Warning / Police Alert**.  

---

## 🔑 Key Takeaway
- **Geo-fencing** = deterministic, fast.  
- **Isolation Forest** = unsupervised anomaly detection.  
- **LSTM/GRU** = sequential anomaly detection.  
- **LightGBM** = supervised severity classification (future).  
- Together, these make the system **smart, reliable, and adaptive**.  

---

⚡ Use this guide to **understand how the AI works** and **implement each algorithm** step by step.




📘 Smart Tourist Safety & Incident Response System

Database Schema Documentation

1. Tourists (public.tourists)

Stores personal and safety information of tourists.

Column	Type	Constraints
id	bigint (PK)	Auto-generated
name	varchar	Required
contact	varchar	Required, Unique
email	varchar	Optional
trip_info	jsonb	Default: {}
emergency_contact	varchar	Required
safety_score	integer	Default 100, Range 0–100
age	integer	Range 0–150
nationality	varchar	Default: Indian
passport_number	varchar	Optional
is_active	boolean	Default: true
last_location_update	timestamptz	Nullable
created_at	timestamptz	Default now()
updated_at	timestamptz	Default now()
2. Locations (public.locations)

Captures real-time GPS tracking data for tourists.

Column	Type	Constraints
id	bigint (PK)	Auto-generated
tourist_id	bigint (FK)	→ tourists.id
latitude	numeric	Range -90 to 90
longitude	numeric	Range -180 to 180
altitude	numeric	Optional
accuracy	numeric	Optional
speed	numeric	Optional
heading	numeric	0–360
timestamp	timestamptz	Default now()
created_at	timestamptz	Default now()
3. Location History (public.location_history)

Compressed travel history for analytics.

Column	Type	Constraints
id	bigint (PK)	Auto-generated
tourist_id	bigint (FK)	→ tourists.id
date	date	Required
location_data	jsonb	Required
total_distance	numeric	Optional
unique_locations	integer	Optional
created_at	timestamptz	Default now()
4. Alerts (public.alerts)

Stores safety alerts triggered manually or automatically.

Column	Type	Constraints
id	bigint (PK)	Auto-generated
tourist_id	bigint (FK)	→ tourists.id
type	varchar	Enum: panic, geofence, anomaly, temporal, low_safety_score, sos, manual
severity	varchar	Enum: LOW, MEDIUM, HIGH, CRITICAL (default: LOW)
message	text	Required
description	text	Optional
latitude	numeric	Optional
longitude	numeric	Optional
ai_confidence	numeric	0–1
auto_generated	boolean	Default: false
acknowledged	boolean	Default: false
acknowledged_by	varchar	Optional
acknowledged_at	timestamptz	Optional
resolved_by	varchar	Optional
resolved_at	timestamptz	Optional
resolution_notes	text	Optional
timestamp	timestamptz	Default now()
status	varchar	Enum: active, acknowledged, resolved, false_alarm (default: active)
5. Safe Zones (public.safe_zones)

Defines safe/tourist-friendly areas.

Column	Type	Constraints
id	bigint (PK)	Auto-generated
name	varchar	Required
description	text	Optional
zone_type	varchar	Enum: tourist_area, hotel, restaurant, transport_hub, hospital, police_station
coordinates	jsonb	Required (GeoJSON polygon)
city	varchar	Optional
state	varchar	Optional
country	varchar	Default: India
safety_rating	integer	1–5, Default: 5
is_active	boolean	Default: true
created_at	timestamptz	Default now()
updated_at	timestamptz	Default now()
6. Restricted Zones (public.restricted_zones)

Defines dangerous or restricted areas.

Column	Type	Constraints
id	bigint (PK)	Auto-generated
name	varchar	Required
description	text	Optional
zone_type	varchar	Enum: restricted, military, private, dangerous, construction, natural_hazard
coordinates	jsonb	Required (GeoJSON polygon)
city	varchar	Optional
state	varchar	Optional
country	varchar	Default: India
danger_level	integer	1–5, Default: 3
buffer_zone_meters	integer	Default: 100
is_active	boolean	Default: true
created_at	timestamptz	Default now()
updated_at	timestamptz	Default now()
7. AI Assessments (public.ai_assessments)

Aggregated AI/ML safety evaluations.

Column	Type	Constraints
id	bigint (PK)	Auto-generated
tourist_id	bigint (FK)	→ tourists.id
location_id	bigint (FK)	→ locations.id
safety_score	integer	0–100
severity	varchar	Enum: SAFE, WARNING, CRITICAL
geofence_alert	boolean	Default: false
anomaly_score	numeric	0–1
temporal_risk_score	numeric	0–1
supervised_prediction	numeric	0–1
confidence_level	numeric	0–1 (required)
recommended_action	varchar	Optional
alert_message	text	Optional
model_versions	jsonb	Default: {}
processing_time_ms	numeric	Optional
created_at	timestamptz	Default now()
8. AI Model Predictions (public.ai_model_predictions)

Detailed model-level AI predictions.

Column	Type	Constraints
id	bigint (PK)	Auto-generated
assessment_id	bigint (FK)	→ ai_assessments.id
model_name	varchar	Enum: geofence, isolation_forest, temporal_autoencoder, lightgbm_classifier
prediction_value	numeric	0–1
confidence	numeric	0–1
processing_time_ms	numeric	Optional
model_version	varchar	Optional
metadata	jsonb	Default: {}
created_at	timestamptz	Default now()
9. API Logs (public.api_logs)

Logs API usage and errors.

Column	Type	Constraints
id	bigint (PK)	Auto-generated
endpoint	varchar	Required
method	varchar	Required
status_code	integer	Required
response_time_ms	numeric	Optional
user_agent	text	Optional
ip_address	inet	Optional
request_data	jsonb	Optional
error_message	text	Optional
created_at	timestamptz	Default now()
10. System Metrics (public.system_metrics)

Stores system health and performance metrics.

Column	Type	Constraints
id	bigint (PK)	Auto-generated
metric_type	varchar	Enum: cpu_usage, memory_usage, active_tourists, requests_per_minute, error_rate
value	numeric	Required
unit	varchar	Optional
metadata	jsonb	Default: {}
created_at	timestamptz	Default now()
11. Spatial Reference System (public.spatial_ref_sys)

(Internal PostGIS table – not usually edited by users)

Column	Type	Constraints
srid	integer (PK)	>0, ≤998999
auth_name	varchar	Optional
auth_srid	integer	Optional
srtext	varchar	Optional
proj4text	varchar	Optional