# Smart Tourist Safety & Incident Response System - Backend

A FastAPI backend system for monitoring tourist safety, tracking locations, and managing emergency responses using Supabase as the database.

## Features

- **Tourist Registration**: Register tourists with safety scoring system
- **Location Tracking**: Real-time GPS coordinate tracking
- **Emergency Alerts**: Panic button and geofence violation alerts
- **Safety Scoring**: Automatic safety score calculation (0-100)
- **Restricted Zones**: Geofenced areas with automatic alerts

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: Supabase (PostgreSQL)
- **Validation**: Pydantic 2.11.9
- **Server**: Uvicorn

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   # Create .env file with:
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   SECRET_KEY=your_secret_key
   DEBUG=True
   ```

3. **Database Setup**
   - Execute `supabase_schema.sql` in your Supabase SQL editor
   - Initialize restricted zones: `POST /admin/initialize-database`

4. **Run Server**
   ```bash
   uvicorn main:app --reload --host localhost --port 8000
   ```

## API Endpoints

### Tourist Management
- `POST /tourists/register` - Register new tourist
- `GET /tourists/{id}` - Get tourist details

### Location Tracking
- `POST /locations/update` - Update tourist location
- `GET /locations/all` - Get all latest locations

### Alerts
- `POST /alerts/panic` - Create panic alert
- `POST /alerts/geofence` - Create geofence alert
- `GET /alerts` - Get all alerts
- `PUT /alerts/{id}/resolve` - Resolve alert

### Admin
- `GET /admin/health` - Health check
- `POST /admin/initialize-database` - Initialize database

## Safety Scoring

- **Default Score**: 100
- **Panic Alert**: -40 points
- **Geofence Violation**: -20 points
- **Score Range**: 0-100

## Documentation

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Production Deployment

- Update environment variables for production
- Disable debug mode (`DEBUG=False`)
- Configure proper CORS origins
- Set up proper authentication if needed