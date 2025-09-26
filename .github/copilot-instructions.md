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
