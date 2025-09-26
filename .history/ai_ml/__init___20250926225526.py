"""
AI/ML module for Smart Tourist Safety & Incident Response System
Hybrid pipeline combining Rule-based + ML + Deep Learning approaches
"""

__version__ = "1.0.0"

# Import core components (lazy loading to avoid circular imports)
def get_pipeline():
    """Get the main AI/ML pipeline"""
    from .pipeline import TouristSafetyPipeline
    return TouristSafetyPipeline()

def get_feature_extractor():
    """Get the feature extractor"""
    from .preprocessors.feature_extractor import FeatureExtractor
    return FeatureExtractor()

def get_safety_scorer():
    """Get the safety scorer"""
    from .utils.safety_scorer import SafetyScorer
    return SafetyScorer()

__all__ = [
    "get_pipeline",
    "get_feature_extractor", 
    "get_safety_scorer"
]