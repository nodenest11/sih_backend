# Smart Tourist Safety & Incident Response System - Backend

A FastAPI-based backend system for monitoring tourist safety and handling emergency incidents.

## Features

- **Tourist Management**: Register tourists with contact details and emergency contacts
- **Real-time Location Tracking**: Track tourist locations with GPS coordinates
- **Alert System**: Handle panic alerts and geofence violations
- **Safety Score Calculation**: Dynamic scoring system based on tourist behavior
- **Risk Assessment**: Comprehensive risk analysis for each tourist
- **Restricted Zones**: Geofence monitoring for dangerous areas

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (with SQLite fallback for development)
- **ORM**: SQLAlchemy
- **Server**: Uvicorn
- **Documentation**: Automatic OpenAPI/Swagger docs

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the example environment file and configure your database:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```
DATABASE_URL=postgresql://username:password@localhost:5432/tourist_safety_db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

For development without PostgreSQL, the system will automatically use SQLite.

### 3. Run the Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Initialize Sample Data

After starting the server, visit: `http://localhost:8000/admin/seed-database` to populate the database with 100 sample tourists and test data.

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Tourist Management
- `POST /tourists/register` - Register a new tourist
- `GET /tourists/{id}` - Get tourist details
- `GET /tourists/` - List all tourists
- `PUT /tourists/{id}/safety-score` - Update safety score

### Location Management
- `POST /locations/update` - Update tourist location
- `GET /locations/all` - Get latest locations of all tourists
- `GET /locations/tourist/{id}` - Get location history for a tourist
- `GET /locations/latest/{id}` - Get latest location for a tourist

### Alert Management
- `POST /alerts/panic` - Create panic alert
- `POST /alerts/geofence` - Create geofence violation alert
- `GET /alerts/` - Get all alerts (with status filter)
- `PUT /alerts/{id}/resolve` - Resolve an alert
- `GET /alerts/tourist/{id}` - Get alerts for specific tourist

### Admin & Analytics
- `GET /admin/{id}/risk-assessment` - Get risk assessment for tourist
- `POST /admin/{id}/safe-checkin` - Record safe check-in
- `POST /admin/{id}/check-safe-duration` - Check safe duration bonus
- `POST /admin/seed-database` - Initialize sample data

## Safety Score System

The safety score ranges from 0-100:

- **Panic Alert**: -40 points
- **Geofence Violation**: -20 points
- **Safe Duration (1 hour)**: +10 points
- **Regular Check-in**: +5 points

## Sample Data

The system includes:
- 100 dummy tourists with realistic names and details
- Location data across Indian cities (Delhi, Mumbai, Goa, Shillong, etc.)
- 5 restricted zones with geofence polygons
- Sample alerts for testing

## Example API Usage

### Register a Tourist
```bash
curl -X POST "http://localhost:8000/tourists/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "contact": "9876543210",
    "trip_info": "Visiting Delhi for business",
    "emergency_contact": "9876543211"
  }'
```

### Update Location
```bash
curl -X POST "http://localhost:8000/locations/update" \
  -H "Content-Type: application/json" \
  -d '{
    "tourist_id": 1,
    "latitude": 28.61,
    "longitude": 77.23
  }'
```

### Create Panic Alert
```bash
curl -X POST "http://localhost:8000/alerts/panic" \
  -H "Content-Type: application/json" \
  -d '{
    "tourist_id": 1,
    "latitude": 28.61,
    "longitude": 77.23
  }'
```

## Database Schema

### Tourist
- id, name, contact, trip_info, emergency_contact, safety_score

### Location
- id, tourist_id, latitude, longitude, timestamp

### Alert
- id, tourist_id, type, message, latitude, longitude, timestamp, status

### RestrictedZone
- id, name, description, polygon_coordinates, risk_level

### GeofenceAlert
- id, tourist_id, zone_id, zone_name, latitude, longitude, entry_type, safety_score_impact, timestamp

## Development

### Project Structure
```
backend/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── services.py          # Business logic services
├── seed_data.py         # Sample data generation
├── requirements.txt     # Python dependencies
├── routers/
│   ├── tourists.py      # Tourist management endpoints
│   ├── locations.py     # Location tracking endpoints
│   ├── alerts.py        # Alert management endpoints
│   └── admin.py         # Admin and analytics endpoints
└── .env.example         # Environment configuration template
```

### Running Tests
The system includes comprehensive sample data for testing all endpoints. Use the Swagger UI at `/docs` for interactive testing.

## Deployment

For production deployment:

1. Set up PostgreSQL database
2. Configure environment variables
3. Use a production WSGI server like Gunicorn
4. Set up proper CORS origins
5. Enable HTTPS

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request