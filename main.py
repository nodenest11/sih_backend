from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import tourists, locations, alerts, admin
import uvicorn

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Tourist Safety & Incident Response System",
    description="Backend API for tourist safety monitoring and emergency response",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tourists.router, prefix="/tourists", tags=["tourists"])
app.include_router(locations.router, prefix="/locations", tags=["locations"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/heatmap")
def get_heatmap_redirect():
    """Redirect to the heatmap endpoint (for backward compatibility)"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/locations/heatmap")

@app.get("/restrictedZones")
def get_restricted_zones_redirect():
    """Redirect to the restricted zones endpoint"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/locations/restrictedZones")

@app.get("/")
def read_root():
    return {"message": "Smart Tourist Safety & Incident Response System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)