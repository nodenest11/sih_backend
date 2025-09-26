from fastapi import APIRouter, HTTPException, status
from schemas import TouristCreate, TouristResponse
from services import TouristService
from typing import List

router = APIRouter()

@router.post("/register", response_model=TouristResponse, status_code=status.HTTP_201_CREATED)
def register_tourist(tourist: TouristCreate):
    """Register a new tourist"""
    try:
        tourist_data = tourist.dict()
        result = TouristService.create_tourist(tourist_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create tourist"
            )
        
        return TouristResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating tourist: {str(e)}"
        )

@router.get("/{tourist_id}", response_model=TouristResponse)
def get_tourist(tourist_id: int):
    """Get tourist details by ID"""
    try:
        tourist = TouristService.get_tourist(tourist_id)
        
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        return TouristResponse(**tourist)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tourist: {str(e)}"
        )