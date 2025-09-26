"""
Main AI/ML pipeline that orchestrates all models for tourist safety assessment
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from ..models.geofencing import GeoFencingModel
from ..models.isolation_forest_detector import IsolationForestDetector
from ..models.lstm_autoencoder import LSTMAutoencoderDetector
from ..preprocessors.feature_extractor import FeatureExtractor
from ..utils.safety_scorer import SafetyScorer
from ..schemas.ai_schemas import TouristMovementData, ProcessedFeatures, SafetyAssessment, ModelPrediction
from ..config.ai_config import CONFIG

class TouristSafetyPipeline:
    """
    Main pipeline that coordinates all AI/ML models for real-time safety assessment
    """
    
    def __init__(self):
        # Initialize all components
        self.geofence_model = GeoFencingModel()
        self.anomaly_detector = IsolationForestDetector()
        self.temporal_detector = LSTMAutoencoderDetector()
        self.feature_extractor = FeatureExtractor()
        self.safety_scorer = SafetyScorer()
        
        # Cache for storing recent features per tourist
        self.tourist_feature_cache: Dict[int, List[ProcessedFeatures]] = {}
        self.cache_max_size = 50  # Keep last 50 features per tourist
        
    def assess_tourist_safety(self,
                             current_data: TouristMovementData,
                             historical_data: Optional[List[TouristMovementData]] = None,
                             additional_context: Optional[Dict[str, Any]] = None) -> SafetyAssessment:
        """
        Perform comprehensive safety assessment for a tourist
        
        Args:
            current_data: Current tourist location and movement data
            historical_data: Historical movement data for this tourist
            additional_context: Additional context (SOS signals, manual flags, etc.)
            
        Returns:
            SafetyAssessment with unified risk analysis
        """
        tourist_id = current_data.tourist_id
        
        # Step 1: Extract features
        processed_features = self.feature_extractor.extract_features(
            current_data, 
            historical_data or []
        )
        
        # Step 2: Update feature cache
        self._update_feature_cache(tourist_id, processed_features)
        
        # Step 3: Run all models in parallel
        predictions = {}
        
        # Geo-fencing (always runs - deterministic)
        try:
            predictions['geofence'] = self.geofence_model.predict(current_data)
        except Exception as e:
            print(f"Geo-fencing prediction error: {e}")
            predictions['geofence'] = None
            
        # Anomaly detection (if model is trained)
        try:
            predictions['anomaly'] = self.anomaly_detector.predict(processed_features)
        except Exception as e:
            print(f"Anomaly detection error: {e}")
            predictions['anomaly'] = None
            
        # Temporal analysis (if model is trained and enough history)
        try:
            tourist_features = self.tourist_feature_cache.get(tourist_id, [])
            predictions['temporal'] = self.temporal_detector.predict(tourist_features)
        except Exception as e:
            print(f"Temporal analysis error: {e}")
            predictions['temporal'] = None
            
        # Step 4: Fuse predictions into safety assessment
        assessment = self.safety_scorer.calculate_safety_score(
            geofence_prediction=predictions.get('geofence'),
            anomaly_prediction=predictions.get('anomaly'), 
            temporal_prediction=predictions.get('temporal'),
            additional_context=additional_context
        )
        
        return assessment
    
    def handle_sos_signal(self, 
                         tourist_id: int,
                         latitude: float,
                         longitude: float,
                         additional_info: Optional[Dict[str, Any]] = None) -> SafetyAssessment:
        """
        Handle emergency SOS signal from tourist
        
        Args:
            tourist_id: ID of the tourist sending SOS
            latitude: Current latitude
            longitude: Current longitude
            additional_info: Additional emergency information
            
        Returns:
            Critical SafetyAssessment for emergency response
        """
        # Create emergency movement data
        emergency_data = TouristMovementData(
            tourist_id=tourist_id,
            latitude=latitude,
            longitude=longitude,
            timestamp=datetime.now(),
            speed=0.0,
            zone_type='emergency'
        )
        
        # Generate SOS prediction
        sos_prediction = self.geofence_model.check_sos_signal(emergency_data)
        
        # Create critical assessment
        assessment = SafetyAssessment(
            tourist_id=tourist_id,
            timestamp=datetime.now(),
            safety_score=0.0,  # Critical
            risk_level="critical",
            geofence_result={'sos_activated': True, 'available': True},
            anomaly_result={'available': False},
            temporal_result={'available': False},
            should_alert_tourist=True,
            should_alert_authorities=True,
            alert_message="EMERGENCY: SOS signal received from tourist",
            location={'latitude': latitude, 'longitude': longitude},
            zone_info={'emergency': True}
        )
        
        return assessment
    
    def train_models(self, training_data: List[ProcessedFeatures]) -> Dict[str, Any]:
        """
        Train all ML models with provided data
        
        Args:
            training_data: List of processed features for training
            
        Returns:
            Training results from all models
        """
        results = {}
        
        # Train anomaly detector
        try:
            if len(training_data) >= 10:
                anomaly_results = self.anomaly_detector.train(training_data)
                results['anomaly_detector'] = anomaly_results
            else:
                results['anomaly_detector'] = {'error': 'Insufficient training data'}
        except Exception as e:
            results['anomaly_detector'] = {'error': str(e)}
            
        # Train temporal detector
        try:
            if len(training_data) >= 20:  # Need more data for sequence modeling
                temporal_results = self.temporal_detector.train(training_data)
                results['temporal_detector'] = temporal_results
            else:
                results['temporal_detector'] = {'error': 'Insufficient training data'}
        except Exception as e:
            results['temporal_detector'] = {'error': str(e)}
            
        return results
    
    def save_models(self, model_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Save all trained models to disk
        
        Returns:
            Dictionary with file paths of saved models
        """
        saved_paths = {}
        
        try:
            if self.anomaly_detector.is_trained:
                path = self.anomaly_detector.save_model(
                    f"{model_dir}/isolation_forest.pkl" if model_dir else None
                )
                saved_paths['anomaly_detector'] = path
        except Exception as e:
            saved_paths['anomaly_detector'] = f"Error: {e}"
            
        try:
            if self.temporal_detector.is_trained:
                path = self.temporal_detector.save_model(
                    f"{model_dir}/lstm_autoencoder.pth" if model_dir else None
                )
                saved_paths['temporal_detector'] = path
        except Exception as e:
            saved_paths['temporal_detector'] = f"Error: {e}"
            
        return saved_paths
    
    def load_models(self, model_dir: Optional[str] = None) -> Dict[str, bool]:
        """
        Load trained models from disk
        
        Returns:
            Dictionary indicating which models were successfully loaded
        """
        loaded_status = {}
        
        # Load anomaly detector
        try:
            loaded_status['anomaly_detector'] = self.anomaly_detector.load_model(
                f"{model_dir}/isolation_forest.pkl" if model_dir else None
            )
        except Exception as e:
            print(f"Error loading anomaly detector: {e}")
            loaded_status['anomaly_detector'] = False
            
        # Load temporal detector
        try:
            loaded_status['temporal_detector'] = self.temporal_detector.load_model(
                f"{model_dir}/lstm_autoencoder.pth" if model_dir else None
            )
        except Exception as e:
            print(f"Error loading temporal detector: {e}")
            loaded_status['temporal_detector'] = False
            
        return loaded_status
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get status of all components in the pipeline
        
        Returns:
            Dictionary with status of all models and components
        """
        return {
            'pipeline_version': '1.0.0',
            'timestamp': datetime.now(),
            'components': {
                'geofence_model': {
                    'status': 'active',
                    'type': 'rule_based',
                    'zones_loaded': len(self.geofence_model.restricted_zones) + 
                                  len(self.geofence_model.risky_zones) +
                                  len(self.geofence_model.safe_zones)
                },
                'anomaly_detector': {
                    'status': 'active' if self.anomaly_detector.is_trained else 'untrained',
                    'type': 'isolation_forest',
                    'model_info': self.anomaly_detector.get_model_info()
                },
                'temporal_detector': {
                    'status': 'active' if self.temporal_detector.is_trained else 'untrained',
                    'type': 'lstm_autoencoder',
                    'model_info': self.temporal_detector.get_model_info()
                }
            },
            'cache_status': {
                'tourists_in_cache': len(self.tourist_feature_cache),
                'total_cached_features': sum(len(features) for features in self.tourist_feature_cache.values())
            }
        }
    
    def _update_feature_cache(self, tourist_id: int, features: ProcessedFeatures):
        """Update the feature cache for a tourist"""
        if tourist_id not in self.tourist_feature_cache:
            self.tourist_feature_cache[tourist_id] = []
            
        # Add new features
        self.tourist_feature_cache[tourist_id].append(features)
        
        # Keep only recent features
        if len(self.tourist_feature_cache[tourist_id]) > self.cache_max_size:
            self.tourist_feature_cache[tourist_id] = self.tourist_feature_cache[tourist_id][-self.cache_max_size:]
            
    def clear_cache(self, tourist_id: Optional[int] = None):
        """Clear feature cache for a specific tourist or all tourists"""
        if tourist_id:
            self.tourist_feature_cache.pop(tourist_id, None)
        else:
            self.tourist_feature_cache.clear()
            
    def get_tourist_history(self, tourist_id: int) -> List[ProcessedFeatures]:
        """Get cached feature history for a tourist"""
        return self.tourist_feature_cache.get(tourist_id, [])
    
    def batch_assess_safety(self, 
                           tourist_data_list: List[TouristMovementData]) -> List[SafetyAssessment]:
        """
        Perform safety assessment for multiple tourists in batch
        
        Args:
            tourist_data_list: List of tourist movement data
            
        Returns:
            List of safety assessments
        """
        assessments = []
        
        for data in tourist_data_list:
            try:
                assessment = self.assess_tourist_safety(data)
                assessments.append(assessment)
            except Exception as e:
                print(f"Error assessing safety for tourist {data.tourist_id}: {e}")
                # Create a default safe assessment for errors
                default_assessment = SafetyAssessment(
                    tourist_id=data.tourist_id,
                    timestamp=datetime.now(),
                    safety_score=70.0,
                    risk_level="safe",
                    geofence_result={'available': False},
                    anomaly_result={'available': False},
                    temporal_result={'available': False},
                    should_alert_tourist=False,
                    should_alert_authorities=False,
                    location={'latitude': data.latitude, 'longitude': data.longitude},
                    zone_info={}
                )
                assessments.append(default_assessment)
                
        return assessments