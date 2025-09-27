"""
🚀 Smart Tourist Safety System - Proper Application Startup
This file ensures the correct FastAPI app with router structure is started
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting Smart Tourist Safety System with proper router structure...")
    print("📊 Swagger UI will be available at: http://localhost:8000/docs")
    print("🏥 Health check available at: http://localhost:8000/health")
    print("📍 API endpoints available at: /api/v1/* and direct endpoints")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )