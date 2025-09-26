"""
Safety scoring system that fuses results from all AI/ML models
"""
import math
from datetime import datetime
from typing import List, Dict, Optional, Any
from ..config.ai_config import CONFIG
from ..schemas.ai_schemas import ModelPrediction, SafetyAssessment, TouristMovementData

class SafetyScorer:
    """
    Fuses predictions from all models into unified safety score and alerts
    """
    
    def __init__(self):
        self.config = CONFIG.safety_scoring
        
    def calculate_safety_score(self,
                             geofence_prediction: Optional[ModelPrediction] = None,
                             anomaly_prediction: Optional[ModelPrediction] = None,
                             temporal_prediction: Optional[ModelPrediction] = None,
                             additional_context: Optional[Dict[str, Any]] = None) -> SafetyAssessment:
        """
        Calculate unified safety score from all model predictions
        
        Args:
            geofence_prediction: Geo-fencing model prediction
            anomaly_prediction: Isolation Forest prediction  
            temporal_prediction: LSTM autoencoder prediction
            additional_context: Additional context like SOS signals, zone info, etc.
            
        Returns:
            SafetyAssessment with unified scoring and alert decisions
        """
        # Initialize base safety score
        safety_score = 100.0
        
        # Collect model results for assessment
        model_results = {
            'geofence_result': self._process_geofence_result(geofence_prediction),
            'anomaly_result': self._process_anomaly_result(anomaly_prediction),
            'temporal_result': self._process_temporal_result(temporal_prediction)
        }
        
        # Apply geo-fencing rules (highest priority)
        if geofence_prediction and geofence_prediction.details:
            safety_score = self._apply_geofence_scoring(safety_score, geofence_prediction)
        
        # Apply anomaly detection results
        if anomaly_prediction:
            safety_score = self._apply_anomaly_scoring(safety_score, anomaly_prediction)
            
        # Apply temporal analysis results  
        if temporal_prediction:
            safety_score = self._apply_temporal_scoring(safety_score, temporal_prediction)
            
        # Apply additional context (SOS, manual alerts, etc.)
        if additional_context:
            safety_score = self._apply_context_scoring(safety_score, additional_context)
            
        # Ensure score is within bounds
        safety_score = max(0.0, min(100.0, safety_score))
        
        # Determine risk level and alert decisions
        risk_level, alert_decisions = self._determine_risk_level(safety_score, model_results)
        
        # Extract location information
        location_info = self._extract_location_info(geofence_prediction, additional_context)
        
        # Create final assessment
        assessment = SafetyAssessment(
            tourist_id=self._extract_tourist_id(geofence_prediction, additional_context),
            timestamp=datetime.now(),
            safety_score=safety_score,
            risk_level=risk_level,
            geofence_result=model_results['geofence_result'],
            anomaly_result=model_results['anomaly_result'],
            temporal_result=model_results['temporal_result'],
            should_alert_tourist=alert_decisions['alert_tourist'],
            should_alert_authorities=alert_decisions['alert_authorities'],
            alert_message=alert_decisions['message'],
            location=location_info['location'],
            zone_info=location_info['zone_info']
        )
        
        return assessment
    
    def _apply_geofence_scoring(self, current_score: float, prediction: ModelPrediction) -> float:
        """Apply geo-fencing results to safety score"""
        details = prediction.details
        
        if details.get('sos_activated'):
            # SOS signal - immediate critical alert
            return 0.0
            
        if details.get('in_restricted'):
            # Restricted zone - critical penalty
            return current_score + self.config.restricted_zone_penalty
            
        if details.get('in_risky'):
            # Risky zone - warning penalty
            return current_score + self.config.risky_zone_penalty
            
        if details.get('in_safe'):
            # Safe zone - small bonus
            return current_score + 5.0
            
        return current_score
    
    def _apply_anomaly_scoring(self, current_score: float, prediction: ModelPrediction) -> float:
        """Apply anomaly detection results to safety score"""
        # Anomaly score is 0-1 where 0=anomaly, 1=normal
        anomaly_score = prediction.score
        confidence = prediction.confidence
        
        # Convert to penalty (lower anomaly score = higher penalty)
        anomaly_penalty = (1.0 - anomaly_score) * 30.0 * confidence
        
        return current_score - anomaly_penalty
    
    def _apply_temporal_scoring(self, current_score: float, prediction: ModelPrediction) -> float:
        """Apply temporal analysis results to safety score"""
        # Temporal score is 0-1 where 0=anomaly, 1=normal
        temporal_score = prediction.score
        confidence = prediction.confidence
        
        # Convert to penalty
        temporal_penalty = (1.0 - temporal_score) * 25.0 * confidence
        
        return current_score - temporal_penalty
    
    def _apply_context_scoring(self, current_score: float, context: Dict[str, Any]) -> float:
        """Apply additional context to safety score"""
        
        # Check for panic signals
        if context.get('panic_signal'):
            current_score += self.config.panic_penalty
            
        # Check for emergency contacts
        if context.get('emergency_contact_triggered'):
            current_score -= 20.0
            
        # Check for safe activity (e.g., staying in safe zone for extended time)
        safe_duration_hours = context.get('safe_duration_hours', 0)
        if safe_duration_hours >= 1:
            bonus = min(safe_duration_hours * self.config.safe_hour_bonus, 20.0)
            current_score += bonus
            
        # Check for manual risk assessments
        manual_risk = context.get('manual_risk_level')
        if manual_risk == 'high':
            current_score -= 30.0
        elif manual_risk == 'medium':
            current_score -= 15.0
            
        return current_score
    
    def _determine_risk_level(self, score: float, model_results: Dict[str, Any]) -> tuple:
        """Determine risk level and alert decisions based on safety score"""
        
        alert_decisions = {
            'alert_tourist': False,
            'alert_authorities': False,
            'message': None
        }
        
        if score < self.config.critical_threshold:
            risk_level = "critical"
            alert_decisions['alert_tourist'] = True
            alert_decisions['alert_authorities'] = True
            alert_decisions['message'] = self._generate_critical_alert_message(model_results)
            
        elif score < self.config.warning_threshold:
            risk_level = "warning"
            alert_decisions['alert_tourist'] = True
            alert_decisions['alert_authorities'] = False
            alert_decisions['message'] = self._generate_warning_alert_message(model_results)
            
        else:
            risk_level = "safe"
            
        return risk_level, alert_decisions
    
    def _generate_critical_alert_message(self, model_results: Dict[str, Any]) -> str:
        """Generate alert message for critical situations"""
        messages = []
        
        # Check geo-fence results
        geo_result = model_results.get('geofence_result', {})
        if geo_result.get('in_restricted'):
            messages.append(f"Tourist entered restricted area: {geo_result.get('zone_name', 'Unknown')}")
        elif geo_result.get('sos_activated'):
            messages.append("EMERGENCY: SOS signal activated")
            
        # Check anomaly results
        anomaly_result = model_results.get('anomaly_result', {})
        if anomaly_result.get('is_anomaly') and anomaly_result.get('score', 1) < 0.3:
            messages.append("Highly unusual movement pattern detected")
            
        # Check temporal results
        temporal_result = model_results.get('temporal_result', {})
        if temporal_result.get('is_anomaly') and temporal_result.get('score', 1) < 0.3:
            messages.append("Abnormal movement sequence detected")
            
        if not messages:
            messages.append("Critical safety threshold reached")
            
        return "CRITICAL ALERT: " + "; ".join(messages)
    
    def _generate_warning_alert_message(self, model_results: Dict[str, Any]) -> str:
        """Generate alert message for warning situations"""
        messages = []
        
        # Check geo-fence results
        geo_result = model_results.get('geofence_result', {})
        if geo_result.get('in_risky'):
            messages.append(f"Entered risky area: {geo_result.get('zone_name', 'Unknown')}")
            
        # Check anomaly results
        anomaly_result = model_results.get('anomaly_result', {})
        if anomaly_result.get('is_anomaly'):
            messages.append("Unusual movement pattern detected")
            
        # Check temporal results
        temporal_result = model_results.get('temporal_result', {})
        if temporal_result.get('is_anomaly'):
            messages.append("Irregular movement sequence")
            
        if not messages:
            messages.append("Please check your safety status")
            
        return "WARNING: " + "; ".join(messages)
    
    def _process_geofence_result(self, prediction: Optional[ModelPrediction]) -> Dict[str, Any]:
        """Process geo-fencing prediction into standard format"""
        if not prediction:
            return {'available': False}
            
        return {
            'available': True,
            'score': prediction.score,
            'confidence': prediction.confidence,
            'in_restricted': prediction.details.get('in_restricted', False),
            'in_risky': prediction.details.get('in_risky', False),
            'in_safe': prediction.details.get('in_safe', False),
            'zone_name': prediction.details.get('zone_name'),
            'sos_activated': prediction.details.get('sos_activated', False)
        }
    
    def _process_anomaly_result(self, prediction: Optional[ModelPrediction]) -> Dict[str, Any]:
        """Process anomaly detection prediction into standard format"""
        if not prediction:
            return {'available': False}
            
        return {
            'available': True,
            'score': prediction.score,
            'confidence': prediction.confidence,
            'is_anomaly': prediction.details.get('is_anomaly', False),
            'raw_score': prediction.details.get('raw_anomaly_score'),
            'interpretation': prediction.details.get('interpretation')
        }
    
    def _process_temporal_result(self, prediction: Optional[ModelPrediction]) -> Dict[str, Any]:
        """Process temporal analysis prediction into standard format"""
        if not prediction:
            return {'available': False}
            
        return {
            'available': True,
            'score': prediction.score,
            'confidence': prediction.confidence,
            'is_anomaly': prediction.details.get('is_anomaly', False),
            'reconstruction_error': prediction.details.get('reconstruction_error'),
            'interpretation': prediction.details.get('interpretation')
        }
    
    def _extract_location_info(self, 
                              geofence_prediction: Optional[ModelPrediction],
                              additional_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract location information from predictions and context"""
        location = {'latitude': 0.0, 'longitude': 0.0}
        zone_info = {}
        
        if additional_context and 'location' in additional_context:
            location = additional_context['location']
            
        if geofence_prediction and geofence_prediction.details:
            zone_info = {
                'current_zone': geofence_prediction.details.get('zone_name'),
                'zone_type': geofence_prediction.details.get('zone_type'),
                'in_restricted': geofence_prediction.details.get('in_restricted', False),
                'in_risky': geofence_prediction.details.get('in_risky', False),
                'in_safe': geofence_prediction.details.get('in_safe', False)
            }
            
        return {'location': location, 'zone_info': zone_info}
    
    def _extract_tourist_id(self, 
                           geofence_prediction: Optional[ModelPrediction],
                           additional_context: Optional[Dict[str, Any]]) -> int:
        """Extract tourist ID from available sources"""
        if additional_context and 'tourist_id' in additional_context:
            return additional_context['tourist_id']
        return 0  # Default value
    
    def get_score_explanation(self, assessment: SafetyAssessment) -> Dict[str, Any]:
        """Provide detailed explanation of how the safety score was calculated"""
        explanation = {
            'final_score': assessment.safety_score,
            'risk_level': assessment.risk_level,
            'components': []
        }
        
        # Explain geo-fencing contribution
        if assessment.geofence_result.get('available'):
            geo_component = {
                'model': 'geofencing',
                'weight': self.config.geofence_weight,
                'contribution': 'rule-based',
                'impact': 'high' if assessment.geofence_result.get('in_restricted') else 'medium'
            }
            explanation['components'].append(geo_component)
            
        # Explain anomaly detection contribution
        if assessment.anomaly_result.get('available'):
            anomaly_component = {
                'model': 'anomaly_detection',
                'weight': self.config.isolation_forest_weight,
                'score': assessment.anomaly_result.get('score'),
                'impact': 'high' if assessment.anomaly_result.get('is_anomaly') else 'low'
            }
            explanation['components'].append(anomaly_component)
            
        # Explain temporal analysis contribution
        if assessment.temporal_result.get('available'):
            temporal_component = {
                'model': 'temporal_analysis',
                'weight': self.config.lstm_weight,
                'score': assessment.temporal_result.get('score'),
                'impact': 'high' if assessment.temporal_result.get('is_anomaly') else 'low'
            }
            explanation['components'].append(temporal_component)
            
        return explanation