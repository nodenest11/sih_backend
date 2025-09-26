"""
Configuration settings for AI/ML models
"""
from dataclasses import dataclass
from typing import List, Dict, Any
import os

@dataclass
class GeoFencingConfig:
    """Configuration for geo-fencing model"""
    restricted_zones: List[Dict[str, Any]] = None  # Will be loaded from database
    buffer_distance: float = 50.0  # meters
    
@dataclass
class IsolationForestConfig:
    """Configuration for Isolation Forest anomaly detection"""
    contamination: float = 0.1  # Expected proportion of outliers
    n_estimators: int = 100
    max_samples: str = "auto"
    random_state: int = 42
    
@dataclass
class LSTMConfig:
    """Configuration for LSTM Autoencoder"""
    sequence_length: int = 10  # Number of time steps to look back
    input_features: int = 4  # [distance_per_min, inactivity_duration, deviation_from_route, speed]
    hidden_size: int = 64
    num_layers: int = 2
    dropout: float = 0.2
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    
@dataclass
class SafetyScoringConfig:
    """Configuration for safety scoring system"""
    # Safety score thresholds
    critical_threshold: float = 50.0
    warning_threshold: float = 80.0
    
    # Model weights for fusion
    geofence_weight: float = 0.4
    isolation_forest_weight: float = 0.3
    lstm_weight: float = 0.3
    
    # Score adjustments
    panic_penalty: float = -40.0
    restricted_zone_penalty: float = -30.0
    risky_zone_penalty: float = -20.0
    safe_hour_bonus: float = +10.0
    
@dataclass
class AIConfig:
    """Main configuration class"""
    # Model paths
    model_save_dir: str = "./ai_ml/saved_models"
    
    # Feature engineering
    inactivity_threshold_minutes: float = 30.0  # Minutes without movement
    deviation_threshold_meters: float = 500.0  # Meters from planned route
    
    # Data processing
    location_update_interval_minutes: float = 5.0
    
    # Component configs
    geofencing: GeoFencingConfig = GeoFencingConfig()
    isolation_forest: IsolationForestConfig = IsolationForestConfig()
    lstm: LSTMConfig = LSTMConfig()
    safety_scoring: SafetyScoringConfig = SafetyScoringConfig()
    
    def __post_init__(self):
        """Create model directory if it doesn't exist"""
        os.makedirs(self.model_save_dir, exist_ok=True)

# Global configuration instance
CONFIG = AIConfig()