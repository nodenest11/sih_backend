"""
Feature extractor for tourist movement data
Computes derived features for ML models
"""
import math
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from geopy.distance import geodesic
from ..config.ai_config import CONFIG
from ..schemas.ai_schemas import TouristMovementData, ProcessedFeatures

class FeatureExtractor:
    """Extracts features from tourist movement data"""
    
    def __init__(self):
        self.config = CONFIG
        
    def extract_features(self, 
                        current_data: TouristMovementData,
                        historical_data: List[TouristMovementData]) -> ProcessedFeatures:
        """
        Extract features from current and historical tourist data
        
        Args:
            current_data: Current tourist location data
            historical_data: List of historical location data (sorted by timestamp)
            
        Returns:
            ProcessedFeatures object with derived features
        """
        
        # Basic features
        features = {
            'tourist_id': current_data.tourist_id,
            'timestamp': current_data.timestamp,
            'latitude': current_data.latitude,
            'longitude': current_data.longitude,
            'speed': current_data.speed or 0.0,
            'zone_type': current_data.zone_type or 'unknown'
        }
        
        # Compute derived features
        features['distance_per_min'] = self._calculate_distance_per_minute(
            current_data, historical_data
        )
        
        features['inactivity_duration'] = self._calculate_inactivity_duration(
            current_data, historical_data
        )
        
        features['deviation_from_route'] = self._calculate_route_deviation(
            current_data, current_data.planned_route
        )
        
        # Store recent locations for sequence models
        features['recent_locations'] = self._prepare_recent_locations(
            current_data, historical_data
        )
        
        return ProcessedFeatures(**features)
    
    def _calculate_distance_per_minute(self, 
                                     current: TouristMovementData,
                                     historical: List[TouristMovementData]) -> float:
        """
        Calculate distance traveled per minute
        """
        if not historical:
            return 0.0
            
        # Get the most recent location
        last_location = historical[-1]
        
        # Calculate time difference in minutes
        time_diff = (current.timestamp - last_location.timestamp).total_seconds() / 60.0
        
        if time_diff <= 0:
            return 0.0
            
        # Calculate distance using geodesic distance
        current_pos = (current.latitude, current.longitude)
        last_pos = (last_location.latitude, last_location.longitude)
        
        distance_meters = geodesic(current_pos, last_pos).meters
        
        return distance_meters / time_diff
    
    def _calculate_inactivity_duration(self,
                                     current: TouristMovementData,
                                     historical: List[TouristMovementData]) -> float:
        """
        Calculate how long the tourist has been inactive (stationary)
        """
        if not historical:
            return 0.0
            
        inactivity_minutes = 0.0
        current_pos = (current.latitude, current.longitude)
        
        # Look backwards through historical data
        for i in range(len(historical) - 1, -1, -1):
            hist_data = historical[i]
            hist_pos = (hist_data.latitude, hist_data.longitude)
            
            # Calculate distance from current position
            distance = geodesic(current_pos, hist_pos).meters
            
            # If distance is small, consider it as stationary
            if distance < 50:  # 50 meters threshold
                time_diff = (current.timestamp - hist_data.timestamp).total_seconds() / 60.0
                inactivity_minutes = max(inactivity_minutes, time_diff)
            else:
                break  # Tourist has moved, stop looking back
                
        return inactivity_minutes
    
    def _calculate_route_deviation(self,
                                  current: TouristMovementData,
                                  planned_route: Optional[List[Dict]]) -> float:
        """
        Calculate deviation from planned route in meters
        """
        if not planned_route:
            return 0.0
            
        current_pos = (current.latitude, current.longitude)
        min_distance = float('inf')
        
        # Find minimum distance to any point in the planned route
        for waypoint in planned_route:
            if 'latitude' in waypoint and 'longitude' in waypoint:
                waypoint_pos = (waypoint['latitude'], waypoint['longitude'])
                distance = geodesic(current_pos, waypoint_pos).meters
                min_distance = min(min_distance, distance)
                
        # Also check distances between consecutive waypoints (path segments)
        for i in range(len(planned_route) - 1):
            wp1 = planned_route[i]
            wp2 = planned_route[i + 1]
            
            if ('latitude' in wp1 and 'longitude' in wp1 and 
                'latitude' in wp2 and 'longitude' in wp2):
                
                distance_to_segment = self._distance_to_line_segment(
                    current_pos,
                    (wp1['latitude'], wp1['longitude']),
                    (wp2['latitude'], wp2['longitude'])
                )
                min_distance = min(min_distance, distance_to_segment)
                
        return min_distance if min_distance != float('inf') else 0.0
    
    def _distance_to_line_segment(self, point: Tuple[float, float], 
                                 line_start: Tuple[float, float],
                                 line_end: Tuple[float, float]) -> float:
        """
        Calculate minimum distance from a point to a line segment
        """
        # Convert to meters using approximate conversion
        # This is a simplified calculation for short distances
        
        x, y = point
        x1, y1 = line_start  
        x2, y2 = line_end
        
        # Calculate the perpendicular distance from point to line
        A = x - x1
        B = y - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            # Line segment is actually a point
            return geodesic(point, line_start).meters
            
        param = dot / len_sq
        
        if param < 0:
            closest_point = line_start
        elif param > 1:
            closest_point = line_end
        else:
            closest_point = (x1 + param * C, y1 + param * D)
            
        return geodesic(point, closest_point).meters
    
    def _prepare_recent_locations(self,
                                current: TouristMovementData,
                                historical: List[TouristMovementData]) -> List[Dict]:
        """
        Prepare recent location data for sequence models
        """
        # Get last N locations including current
        sequence_length = self.config.lstm.sequence_length
        all_locations = historical + [current]
        
        # Take the most recent locations
        recent = all_locations[-sequence_length:] if len(all_locations) >= sequence_length else all_locations
        
        # Convert to format suitable for LSTM
        location_sequence = []
        for loc in recent:
            location_dict = {
                'latitude': loc.latitude,
                'longitude': loc.longitude, 
                'timestamp': loc.timestamp.isoformat(),
                'speed': loc.speed or 0.0
            }
            location_sequence.append(location_dict)
            
        return location_sequence
    
    def extract_sequence_features(self, features_list: List[ProcessedFeatures]) -> np.ndarray:
        """
        Extract features for sequence modeling (LSTM)
        
        Returns:
            numpy array of shape (sequence_length, num_features)
        """
        if not features_list:
            return np.zeros((self.config.lstm.sequence_length, self.config.lstm.input_features))
            
        # Features to use: [distance_per_min, inactivity_duration, deviation_from_route, speed]
        sequence_data = []
        
        for features in features_list:
            feature_vector = [
                features.distance_per_min,
                features.inactivity_duration,
                features.deviation_from_route,
                features.speed
            ]
            sequence_data.append(feature_vector)
            
        # Convert to numpy array and pad if necessary
        sequence_array = np.array(sequence_data)
        
        # Pad or truncate to match expected sequence length
        target_length = self.config.lstm.sequence_length
        current_length = len(sequence_array)
        
        if current_length < target_length:
            # Pad with zeros
            padding = np.zeros((target_length - current_length, self.config.lstm.input_features))
            sequence_array = np.vstack([padding, sequence_array])
        elif current_length > target_length:
            # Take the most recent data
            sequence_array = sequence_array[-target_length:]
            
        return sequence_array