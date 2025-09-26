"""
Data preprocessor utilities
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from ..schemas.ai_schemas import ProcessedFeatures

class DataPreprocessor:
    """Handles data preprocessing for ML models"""
    
    def __init__(self):
        self.feature_scaler = StandardScaler()
        self.target_scaler = MinMaxScaler()
        self.is_fitted = False
        
    def prepare_isolation_forest_data(self, features_list: List[ProcessedFeatures]) -> np.ndarray:
        """
        Prepare data for Isolation Forest anomaly detection
        
        Returns:
            numpy array with features: [distance_per_min, inactivity_duration, deviation_from_route, speed]
        """
        if not features_list:
            return np.array([]).reshape(0, 4)
            
        data = []
        for features in features_list:
            row = [
                features.distance_per_min,
                features.inactivity_duration, 
                features.deviation_from_route,
                features.speed
            ]
            data.append(row)
            
        return np.array(data)
    
    def normalize_features(self, data: np.ndarray, fit: bool = False) -> np.ndarray:
        """
        Normalize features using StandardScaler
        
        Args:
            data: Input data array
            fit: Whether to fit the scaler (True for training data)
            
        Returns:
            Normalized data array
        """
        if data.size == 0:
            return data
            
        if fit:
            self.feature_scaler.fit(data)
            self.is_fitted = True
            
        if self.is_fitted:
            return self.feature_scaler.transform(data)
        else:
            # If not fitted, return original data (shouldn't happen in production)
            return data
    
    def create_sliding_windows(self, 
                             data: np.ndarray, 
                             window_size: int,
                             step_size: int = 1) -> np.ndarray:
        """
        Create sliding windows for sequence modeling
        
        Args:
            data: Input time series data (samples, features)
            window_size: Size of each window
            step_size: Step size between windows
            
        Returns:
            Array of shape (num_windows, window_size, features)
        """
        if len(data) < window_size:
            # Pad with zeros if not enough data
            padding_needed = window_size - len(data)
            padding = np.zeros((padding_needed, data.shape[1]))
            data = np.vstack([padding, data])
            
        windows = []
        for i in range(0, len(data) - window_size + 1, step_size):
            window = data[i:i + window_size]
            windows.append(window)
            
        return np.array(windows)
    
    def handle_missing_values(self, data: np.ndarray) -> np.ndarray:
        """
        Handle missing values in the data
        """
        # Replace NaN with 0 (simple strategy)
        data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
        return data
    
    def create_feature_dataframe(self, features_list: List[ProcessedFeatures]) -> pd.DataFrame:
        """
        Convert list of ProcessedFeatures to pandas DataFrame
        """
        data = []
        for features in features_list:
            row = {
                'tourist_id': features.tourist_id,
                'timestamp': features.timestamp,
                'latitude': features.latitude,
                'longitude': features.longitude,
                'speed': features.speed,
                'zone_type': features.zone_type,
                'distance_per_min': features.distance_per_min,
                'inactivity_duration': features.inactivity_duration,
                'deviation_from_route': features.deviation_from_route
            }
            data.append(row)
            
        return pd.DataFrame(data)
    
    def filter_by_time_window(self, 
                            features_list: List[ProcessedFeatures],
                            window_hours: int = 24) -> List[ProcessedFeatures]:
        """
        Filter features to only include data within a time window
        """
        if not features_list:
            return []
            
        current_time = max(f.timestamp for f in features_list)
        cutoff_time = current_time - timedelta(hours=window_hours)
        
        return [f for f in features_list if f.timestamp >= cutoff_time]
        
    def group_by_tourist(self, features_list: List[ProcessedFeatures]) -> Dict[int, List[ProcessedFeatures]]:
        """
        Group features by tourist_id
        """
        grouped = {}
        for features in features_list:
            tourist_id = features.tourist_id
            if tourist_id not in grouped:
                grouped[tourist_id] = []
            grouped[tourist_id].append(features)
            
        # Sort each group by timestamp
        for tourist_id in grouped:
            grouped[tourist_id].sort(key=lambda x: x.timestamp)
            
        return grouped