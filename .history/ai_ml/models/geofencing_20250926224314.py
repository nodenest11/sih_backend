"""
Rule-based geo-fencing model for immediate threat detection
"""
import math
from typing import List, Dict, Tuple, Optional, Any
from shapely.geometry import Point, Polygon
from geopy.distance import geodesic
from ..config.ai_config import CONFIG
from ..schemas.ai_schemas import TouristMovementData, ModelPrediction

class GeoFencingModel:
    """
    Rule-based geo-fencing for instant alerts
    Provides deterministic, zero-delay response for critical situations
    """
    
    def __init__(self):
        self.config = CONFIG.geofencing
        self.restricted_zones = []
        self.risky_zones = []
        self.safe_zones = []
        self._load_zones()
        
    def _load_zones(self):
        """
        Load geo-fence zones from configuration or database
        For now, we'll define some sample zones
        """
        # Sample restricted zones (these would typically come from database)
        self.restricted_zones = [
            {
                'name': 'Restricted Military Area - Delhi',
                'type': 'polygon',
                'coordinates': [
                    [77.1876, 28.5906], [77.1900, 28.5906], 
                    [77.1900, 28.5926], [77.1876, 28.5926], [77.1876, 28.5906]
                ],
                'severity': 'critical'
            },
            {
                'name': 'Restricted Border Area - LOC',
                'type': 'polygon', 
                'coordinates': [
                    [74.8723, 34.0837], [74.8743, 34.0837],
                    [74.8743, 34.0857], [74.8723, 34.0857], [74.8723, 34.0837]
                ],
                'severity': 'critical'
            }
        ]
        
        # Sample risky zones
        self.risky_zones = [
            {
                'name': 'Dense Forest Area - Goa',
                'type': 'polygon',
                'coordinates': [
                    [73.7821, 15.2993], [73.7851, 15.2993],
                    [73.7851, 15.3023], [73.7821, 15.3023], [73.7821, 15.2993]
                ],
                'severity': 'warning'
            },
            {
                'name': 'Remote Mountain Area - Himachal',
                'type': 'polygon',
                'coordinates': [
                    [77.1734, 31.1048], [77.1754, 31.1048],
                    [77.1754, 31.1068], [77.1734, 31.1068], [77.1734, 31.1048]
                ],
                'severity': 'warning'
            }
        ]
        
        # Sample safe zones (tourist attractions, hotels, etc.)
        self.safe_zones = [
            {
                'name': 'India Gate Tourist Area - Delhi',
                'type': 'circle',
                'center': [77.2295, 28.6129],
                'radius': 1000,  # meters
                'severity': 'safe'
            },
            {
                'name': 'Taj Mahal Complex - Agra', 
                'type': 'circle',
                'center': [78.0421, 27.1751],
                'radius': 800,
                'severity': 'safe'
            }
        ]
    
    def predict(self, data: TouristMovementData) -> ModelPrediction:
        """
        Perform geo-fence analysis on tourist location
        
        Args:
            data: Tourist movement data
            
        Returns:
            ModelPrediction with geo-fence analysis results
        """
        current_point = Point(data.longitude, data.latitude)
        
        # Check restricted zones first (highest priority)
        restricted_result = self._check_restricted_zones(current_point, data)
        if restricted_result['in_restricted']:
            return self._create_prediction(
                score=0.0,  # Critical threat
                confidence=1.0,
                details=restricted_result
            )
        
        # Check risky zones
        risky_result = self._check_risky_zones(current_point, data)
        if risky_result['in_risky']:
            return self._create_prediction(
                score=0.3,  # Warning level
                confidence=0.8,
                details=risky_result
            )
        
        # Check safe zones
        safe_result = self._check_safe_zones(current_point, data)
        if safe_result['in_safe']:
            return self._create_prediction(
                score=1.0,  # Safe
                confidence=0.9,
                details=safe_result
            )
        
        # Unknown area - neutral score
        return self._create_prediction(
            score=0.7,  # Neutral
            confidence=0.5,
            details={
                'zone_type': 'unknown',
                'in_restricted': False,
                'in_risky': False,
                'in_safe': False,
                'message': 'Location not classified'
            }
        )
    
    def _check_restricted_zones(self, point: Point, data: TouristMovementData) -> Dict[str, Any]:
        """Check if point is in any restricted zone"""
        for zone in self.restricted_zones:
            if self._point_in_zone(point, zone):
                return {
                    'zone_type': 'restricted',
                    'in_restricted': True,
                    'in_risky': False,
                    'in_safe': False,
                    'zone_name': zone['name'],
                    'severity': zone['severity'],
                    'message': f"CRITICAL: Tourist entered restricted area: {zone['name']}",
                    'requires_immediate_action': True
                }
                
        return {
            'zone_type': 'unknown',
            'in_restricted': False,
            'in_risky': False,
            'in_safe': False
        }
    
    def _check_risky_zones(self, point: Point, data: TouristMovementData) -> Dict[str, Any]:
        """Check if point is in any risky zone"""
        for zone in self.risky_zones:
            if self._point_in_zone(point, zone):
                return {
                    'zone_type': 'risky',
                    'in_restricted': False,
                    'in_risky': True,
                    'in_safe': False,
                    'zone_name': zone['name'],
                    'severity': zone['severity'],
                    'message': f"WARNING: Tourist in risky area: {zone['name']}",
                    'requires_monitoring': True
                }
                
        return {
            'zone_type': 'unknown',
            'in_restricted': False,
            'in_risky': False,
            'in_safe': False
        }
    
    def _check_safe_zones(self, point: Point, data: TouristMovementData) -> Dict[str, Any]:
        """Check if point is in any safe zone"""
        for zone in self.safe_zones:
            if self._point_in_zone(point, zone):
                return {
                    'zone_type': 'safe',
                    'in_restricted': False,
                    'in_risky': False,
                    'in_safe': True,
                    'zone_name': zone['name'],
                    'severity': zone['severity'],
                    'message': f"Tourist in safe area: {zone['name']}"
                }
                
        return {
            'zone_type': 'unknown',
            'in_restricted': False,
            'in_risky': False,
            'in_safe': False
        }
    
    def _point_in_zone(self, point: Point, zone: Dict[str, Any]) -> bool:
        """Check if a point is within a zone"""
        if zone['type'] == 'polygon':
            polygon = Polygon([(coord[0], coord[1]) for coord in zone['coordinates']])
            return polygon.contains(point)
            
        elif zone['type'] == 'circle':
            center_lat, center_lon = zone['center'][1], zone['center'][0]
            point_lat, point_lon = point.y, point.x
            
            # Use geodesic distance for accuracy
            distance = geodesic((center_lat, center_lon), (point_lat, point_lon)).meters
            return distance <= zone['radius']
            
        return False
    
    def _create_prediction(self, score: float, confidence: float, details: Dict[str, Any]) -> ModelPrediction:
        """Create a ModelPrediction object"""
        from datetime import datetime
        
        return ModelPrediction(
            model_name="geofencing",
            score=score,
            confidence=confidence,
            details=details,
            timestamp=datetime.now()
        )
    
    def check_sos_signal(self, data: TouristMovementData) -> Optional[ModelPrediction]:
        """
        Check for SOS signals (panic button press)
        This would be called separately when an SOS signal is received
        """
        # In a real implementation, this would check for SOS signals
        # For now, we'll assume SOS is indicated by a special field or separate API call
        
        return ModelPrediction(
            model_name="geofencing_sos",
            score=0.0,  # Maximum alert
            confidence=1.0,
            details={
                'sos_activated': True,
                'message': 'EMERGENCY: Tourist activated SOS signal',
                'requires_immediate_action': True,
                'location': {
                    'latitude': data.latitude,
                    'longitude': data.longitude
                }
            },
            timestamp=data.timestamp
        )
    
    def add_restricted_zone(self, zone: Dict[str, Any]):
        """Add a new restricted zone"""
        self.restricted_zones.append(zone)
        
    def add_risky_zone(self, zone: Dict[str, Any]):
        """Add a new risky zone"""
        self.risky_zones.append(zone)
        
    def add_safe_zone(self, zone: Dict[str, Any]):
        """Add a new safe zone"""
        self.safe_zones.append(zone)
        
    def get_zone_info(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get detailed information about zones at a specific location"""
        point = Point(longitude, latitude)
        
        zone_info = {
            'location': {'latitude': latitude, 'longitude': longitude},
            'zones': []
        }
        
        # Check all zone types
        all_zones = (
            [(zone, 'restricted') for zone in self.restricted_zones] +
            [(zone, 'risky') for zone in self.risky_zones] +
            [(zone, 'safe') for zone in self.safe_zones]
        )
        
        for zone, zone_type in all_zones:
            if self._point_in_zone(point, zone):
                zone_info['zones'].append({
                    'name': zone['name'],
                    'type': zone_type,
                    'severity': zone['severity']
                })
                
        return zone_info