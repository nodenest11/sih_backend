from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import tourists, locations, alerts, admin

app = FastAPI(
    title="Smart Tourist Safety & Incident Response System",
    description="Backend API for tourist safety monitoring and emergency response",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tourists.router, prefix="/tourists", tags=["tourists"])
app.include_router(locations.router, prefix="/locations", tags=["locations"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {
        "message": "Smart Tourist Safety & Incident Response System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}