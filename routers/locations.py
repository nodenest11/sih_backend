from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from database import get_db
from models import Location, Tourist, Alert, AlertStatus
from schemas import LocationUpdate, LocationResponse, HeatmapResponse, HeatmapPoint
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/update", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def update_location(location: LocationUpdate, db: Session = Depends(get_db)):
    """Update tourist location"""
    # Check if tourist exists
    tourist = db.query(Tourist).filter(Tourist.id == location.tourist_id).first()
    if not tourist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tourist not found"
        )
    
    # Create new location entry
    db_location = Location(
        tourist_id=location.tourist_id,
        latitude=location.latitude,
        longitude=location.longitude
    )
    
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    
    # Add tourist name to response
    response = LocationResponse.from_orm(db_location)
    response.tourist_name = tourist.name
    
    return response

@router.get("/all", response_model=List[LocationResponse])
def get_all_latest_locations(db: Session = Depends(get_db)):
    """Get latest location of all tourists"""
    # Subquery to get the latest location for each tourist
    subquery = (
        db.query(Location.tourist_id, db.func.max(Location.timestamp).label('latest_timestamp'))
        .group_by(Location.tourist_id)
        .subquery()
    )
    
    # Join with locations and tourists to get complete information
    latest_locations = (
        db.query(Location, Tourist.name)
        .join(subquery, 
              (Location.tourist_id == subquery.c.tourist_id) & 
              (Location.timestamp == subquery.c.latest_timestamp))
        .join(Tourist, Location.tourist_id == Tourist.id)
        .all()
    )
    
    # Format response
    result = []
    for location, tourist_name in latest_locations:
        location_response = LocationResponse.from_orm(location)
        location_response.tourist_name = tourist_name
        result.append(location_response)
    
    return result

@router.get("/tourist/{tourist_id}", response_model=List[LocationResponse])
def get_tourist_locations(
    tourist_id: int, 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    """Get location history for a specific tourist"""
    # Check if tourist exists
    tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
    if not tourist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tourist not found"
        )
    
    # Get locations for the tourist, ordered by timestamp (newest first)
    locations = (
        db.query(Location)
        .filter(Location.tourist_id == tourist_id)
        .order_by(desc(Location.timestamp))
        .limit(limit)
        .all()
    )
    
    # Add tourist name to each response
    result = []
    for location in locations:
        location_response = LocationResponse.from_orm(location)
        location_response.tourist_name = tourist.name
        result.append(location_response)
    
    return result

@router.get("/latest/{tourist_id}", response_model=LocationResponse)
def get_latest_location(tourist_id: int, db: Session = Depends(get_db)):
    """Get the latest location for a specific tourist"""
    # Check if tourist exists
    tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
    if not tourist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tourist not found"
        )
    
    # Get the latest location
    latest_location = (
        db.query(Location)
        .filter(Location.tourist_id == tourist_id)
        .order_by(desc(Location.timestamp))
        .first()
    )
    
    if not latest_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No location data found for this tourist"
        )
    
    # Add tourist name to response
    response = LocationResponse.from_orm(latest_location)
    response.tourist_name = tourist.name
    
    return response

@router.get("/heatmap", response_model=HeatmapResponse)
def get_location_heatmap(
    hours: int = Query(24, description="Hours back to include in heatmap", ge=1, le=168),
    include_alerts: bool = Query(True, description="Include alert data in heatmap"),
    grid_size: float = Query(0.01, description="Grid size for clustering nearby points", ge=0.001, le=0.1),
    db: Session = Depends(get_db)
):
    """
    Generate heatmap data for tourist locations
    
    - **hours**: Number of hours back to include (1-168 hours, default 24)
    - **include_alerts**: Whether to include alert information in intensity
    - **grid_size**: Grid size for clustering nearby points (0.001-0.1, default 0.01)
    """
    try:
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        # Get locations within time range
        locations_query = (
            db.query(Location, Tourist.safety_score)
            .join(Tourist, Location.tourist_id == Tourist.id)
            .filter(Location.timestamp >= time_threshold)
        )
        
        locations_data = locations_query.all()
        
        if not locations_data:
            return HeatmapResponse(
                points=[],
                total_points=0,
                bounds={"north": 0, "south": 0, "east": 0, "west": 0},
                generated_at=datetime.utcnow()
            )
        
        # Group locations into grid cells for clustering
        grid_clusters = {}
        
        for location, safety_score in locations_data:
            # Create grid key based on grid_size
            grid_lat = round(location.latitude / grid_size) * grid_size
            grid_lng = round(location.longitude / grid_size) * grid_size
            grid_key = (grid_lat, grid_lng)
            
            if grid_key not in grid_clusters:
                grid_clusters[grid_key] = {
                    'latitude': grid_lat,
                    'longitude': grid_lng,
                    'tourist_count': 0,
                    'total_safety_score': 0,
                    'locations': []
                }
            
            grid_clusters[grid_key]['tourist_count'] += 1
            grid_clusters[grid_key]['total_safety_score'] += safety_score
            grid_clusters[grid_key]['locations'].append(location)
        
        # Get alert data if requested
        alerts_data = {}
        if include_alerts:
            alerts_query = (
                db.query(Alert)
                .filter(
                    and_(
                        Alert.timestamp >= time_threshold,
                        Alert.latitude.isnot(None),
                        Alert.longitude.isnot(None)
                    )
                )
            )
            
            for alert in alerts_query.all():
                alert_grid_lat = round(alert.latitude / grid_size) * grid_size
                alert_grid_lng = round(alert.longitude / grid_size) * grid_size
                alert_grid_key = (alert_grid_lat, alert_grid_lng)
                
                if alert_grid_key not in alerts_data:
                    alerts_data[alert_grid_key] = 0
                alerts_data[alert_grid_key] += 1
        
        # Create heatmap points
        heatmap_points = []
        all_lats = []
        all_lngs = []
        
        for grid_key, cluster_data in grid_clusters.items():
            tourist_count = cluster_data['tourist_count']
            avg_safety_score = cluster_data['total_safety_score'] / tourist_count
            alert_count = alerts_data.get(grid_key, 0)
            
            # Calculate intensity based on tourist count, safety score, and alerts
            base_intensity = min(tourist_count * 10, 100)  # 10 points per tourist, max 100
            
            # Adjust intensity based on safety score (lower score = higher intensity)
            safety_factor = (100 - avg_safety_score) / 100  # 0 to 1
            safety_intensity = safety_factor * 50  # 0 to 50 points
            
            # Add alert intensity
            alert_intensity = min(alert_count * 20, 50)  # 20 points per alert, max 50
            
            total_intensity = int(base_intensity + safety_intensity + alert_intensity)
            
            # Determine risk level
            if avg_safety_score < 30 or alert_count > 2:
                risk_level = "critical"
            elif avg_safety_score < 50 or alert_count > 1:
                risk_level = "high"
            elif avg_safety_score < 70 or alert_count > 0:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            heatmap_point = HeatmapPoint(
                latitude=cluster_data['latitude'],
                longitude=cluster_data['longitude'],
                intensity=max(1, total_intensity),  # Minimum intensity of 1
                tourist_count=tourist_count,
                alert_count=alert_count if include_alerts else None,
                risk_level=risk_level
            )
            
            heatmap_points.append(heatmap_point)
            all_lats.append(cluster_data['latitude'])
            all_lngs.append(cluster_data['longitude'])
        
        # Calculate bounds
        if all_lats and all_lngs:
            bounds = {
                "north": max(all_lats),
                "south": min(all_lats),
                "east": max(all_lngs),
                "west": min(all_lngs)
            }
        else:
            bounds = {"north": 0, "south": 0, "east": 0, "west": 0}
        
        return HeatmapResponse(
            points=heatmap_points,
            total_points=len(heatmap_points),
            bounds=bounds,
            generated_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating heatmap: {str(e)}"
        )