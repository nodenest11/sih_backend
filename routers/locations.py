from fastapi import APIRouter, HTTPException, status
from schemas import LocationUpdate, LocationResponse
from services import LocationService
from typing import List

router = APIRouter()

@router.post("/update", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def update_location(location: LocationUpdate):
    """Update tourist location"""
    try:
        result = LocationService.update_location(
            location.tourist_id,
            location.latitude,
            location.longitude
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update location"
            )
        
        return LocationResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating location: {str(e)}"
        )

@router.get("/all", response_model=List[LocationResponse])
def get_all_locations():
    """Get latest location of all tourists"""
    try:
        locations = LocationService.get_all_locations()
        return [LocationResponse(**location) for location in locations]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving locations: {str(e)}"
        )