from fastapi import APIRouter, HTTPException, status
from schemas import DatabaseInitResponse, HealthCheckResponse
from services import AdminService

router = APIRouter()

@router.post("/initialize-database", response_model=DatabaseInitResponse)
def initialize_database():
    """Initialize database with essential data"""
    try:
        result = AdminService.initialize_database()
        return DatabaseInitResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing database: {str(e)}"
        )

@router.get("/health", response_model=HealthCheckResponse)
def health_check():
    """Health check endpoint"""
    try:
        result = AdminService.health_check()
        return HealthCheckResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )