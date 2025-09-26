"""
AI/ML module for Smart Tourist Safety & Incident Response System
Hybrid pipeline combining Rule-based + ML + Deep Learning approaches
"""

from .models.geofencing import GeoFencingModel
from .models.isolation_forest_detector import IsolationForestDetector
from .models.lstm_autoencoder import LSTMAutoencoder
from .preprocessors.feature_extractor import FeatureExtractor
from .utils.safety_scorer import SafetyScorer
from .pipeline import TouristSafetyPipeline

__version__ = "1.0.0"
__all__ = [
    "GeoFencingModel",
    "IsolationForestDetector", 
    "LSTMAutoencoder",
    "FeatureExtractor",
    "SafetyScorer",
    "TouristSafetyPipeline"
]