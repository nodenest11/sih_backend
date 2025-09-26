"""
Isolation Forest anomaly detection for tourist movement patterns
"""
import numpy as np
import pickle
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from ..config.ai_config import CONFIG
from ..schemas.ai_schemas import ProcessedFeatures, ModelPrediction
from ..preprocessors.data_preprocessor import DataPreprocessor

class IsolationForestDetector:
    """
    Unsupervised anomaly detection using Isolation Forest
    Detects unusual patterns in tourist movement without labeled data
    """
    
    def __init__(self):
        self.config = CONFIG.isolation_forest
        self.model = IsolationForest(
            contamination=self.config.contamination,
            n_estimators=self.config.n_estimators,
            max_samples=self.config.max_samples,
            random_state=self.config.random_state,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.preprocessor = DataPreprocessor()
        self.is_trained = False
        self.feature_names = [
            'distance_per_min', 
            'inactivity_duration', 
            'deviation_from_route', 
            'speed'
        ]
        
    def train(self, training_features: List[ProcessedFeatures]) -> Dict[str, Any]:
        """
        Train the Isolation Forest model
        
        Args:
            training_features: List of processed features for training
            
        Returns:
            Training metrics and information
        """
        if not training_features:
            raise ValueError("Training features cannot be empty")
            
        # Prepare training data
        X = self.preprocessor.prepare_isolation_forest_data(training_features)
        
        if X.shape[0] < 10:
            raise ValueError("Need at least 10 samples for training")
            
        # Handle missing values
        X = self.preprocessor.handle_missing_values(X)
        
        # Fit scaler and transform data
        X_scaled = self.preprocessor.normalize_features(X, fit=True)
        
        # Train the model
        self.model.fit(X_scaled)
        self.is_trained = True
        
        # Calculate training metrics
        anomaly_scores = self.model.decision_function(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        training_info = {
            'model_name': 'isolation_forest',
            'training_samples': X.shape[0],
            'feature_count': X.shape[1],
            'contamination_rate': self.config.contamination,
            'mean_anomaly_score': float(np.mean(anomaly_scores)),
            'std_anomaly_score': float(np.std(anomaly_scores)),
            'detected_anomalies': int(np.sum(predictions == -1)),
            'normal_samples': int(np.sum(predictions == 1)),
            'training_timestamp': datetime.now()
        }
        
        return training_info
    
    def predict(self, features: ProcessedFeatures) -> ModelPrediction:
        """
        Predict anomaly score for a single feature set
        
        Args:
            features: Processed features for prediction
            
        Returns:
            ModelPrediction with anomaly analysis
        """
        if not self.is_trained:
            # If model not trained, return neutral score
            return ModelPrediction(
                model_name="isolation_forest",
                score=0.5,
                confidence=0.0,
                details={
                    'trained': False,
                    'message': 'Model not trained yet',
                    'anomaly_score': 0.0,
                    'is_anomaly': False
                },
                timestamp=datetime.now()
            )
        
        # Prepare feature vector
        feature_vector = np.array([[
            features.distance_per_min,
            features.inactivity_duration,
            features.deviation_from_route,
            features.speed
        ]])
        
        # Handle missing values
        feature_vector = self.preprocessor.handle_missing_values(feature_vector)
        
        # Scale features
        feature_vector_scaled = self.preprocessor.normalize_features(feature_vector)
        
        # Get anomaly score and prediction
        anomaly_score = self.model.decision_function(feature_vector_scaled)[0]
        prediction = self.model.predict(feature_vector_scaled)[0]
        
        # Convert to normalized score (0 = anomaly, 1 = normal)
        # Isolation Forest returns negative scores for anomalies
        normalized_score = self._normalize_anomaly_score(anomaly_score)
        
        # Determine confidence based on how extreme the score is
        confidence = min(abs(anomaly_score) * 2, 1.0)
        
        details = {
            'trained': True,
            'raw_anomaly_score': float(anomaly_score),
            'normalized_score': float(normalized_score),
            'is_anomaly': prediction == -1,
            'feature_values': {
                'distance_per_min': features.distance_per_min,
                'inactivity_duration': features.inactivity_duration,
                'deviation_from_route': features.deviation_from_route,
                'speed': features.speed
            },
            'interpretation': self._interpret_anomaly(features, prediction, anomaly_score)
        }
        
        return ModelPrediction(
            model_name="isolation_forest",
            score=normalized_score,
            confidence=confidence,
            details=details,
            timestamp=datetime.now()
        )
    
    def predict_batch(self, features_list: List[ProcessedFeatures]) -> List[ModelPrediction]:
        """
        Predict anomaly scores for a batch of features
        """
        if not self.is_trained or not features_list:
            return []
            
        predictions = []
        for features in features_list:
            prediction = self.predict(features)
            predictions.append(prediction)
            
        return predictions
    
    def _normalize_anomaly_score(self, raw_score: float) -> float:
        """
        Normalize anomaly score to 0-1 range
        Lower scores indicate higher anomaly probability
        """
        # Isolation Forest typically returns scores between -1 and 1
        # We'll map them to 0-1 where 0 = anomaly, 1 = normal
        
        # Clamp the score to reasonable bounds
        clamped_score = max(-1.0, min(1.0, raw_score))
        
        # Map [-1, 1] to [0, 1] where negative scores become low values
        if clamped_score < 0:
            # Anomaly: map [-1, 0] to [0, 0.5]
            return (clamped_score + 1) * 0.25
        else:
            # Normal: map [0, 1] to [0.5, 1]
            return 0.5 + (clamped_score * 0.5)
    
    def _interpret_anomaly(self, features: ProcessedFeatures, prediction: int, score: float) -> str:
        """
        Provide human-readable interpretation of the anomaly detection result
        """
        if prediction == 1:  # Normal
            return "Movement pattern appears normal"
            
        # Anomaly detected - try to identify the cause
        interpretations = []
        
        if features.distance_per_min > 1000:  # Very fast movement
            interpretations.append("unusually high travel speed")
            
        if features.inactivity_duration > 60:  # More than 1 hour inactive
            interpretations.append("extended period of inactivity")
            
        if features.deviation_from_route > 1000:  # Far from planned route
            interpretations.append("significant deviation from planned route")
            
        if features.speed > 50:  # High speed (assuming km/h)
            interpretations.append("high movement speed")
            
        if interpretations:
            return f"Anomaly detected due to: {', '.join(interpretations)}"
        else:
            return "Unusual movement pattern detected (cause unclear)"
    
    def save_model(self, filepath: Optional[str] = None) -> str:
        """Save the trained model to disk"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
            
        if filepath is None:
            filepath = os.path.join(CONFIG.model_save_dir, "isolation_forest_model.pkl")
            
        model_data = {
            'model': self.model,
            'scaler': self.preprocessor.feature_scaler,
            'config': self.config.__dict__,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained,
            'save_timestamp': datetime.now()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
            
        return filepath
    
    def load_model(self, filepath: Optional[str] = None) -> bool:
        """Load a trained model from disk"""
        if filepath is None:
            filepath = os.path.join(CONFIG.model_save_dir, "isolation_forest_model.pkl")
            
        if not os.path.exists(filepath):
            return False
            
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
                
            self.model = model_data['model']
            self.preprocessor.feature_scaler = model_data['scaler']
            self.feature_names = model_data.get('feature_names', self.feature_names)
            self.is_trained = model_data.get('is_trained', False)
            
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'model_name': 'isolation_forest',
            'is_trained': self.is_trained,
            'contamination': self.config.contamination,
            'n_estimators': self.config.n_estimators,
            'feature_names': self.feature_names,
            'model_params': self.model.get_params() if self.is_trained else None
        }
        
    def retrain_if_needed(self, 
                         new_features: List[ProcessedFeatures], 
                         min_samples: int = 100) -> bool:
        """
        Retrain the model if enough new data is available
        
        Returns:
            True if retraining was performed, False otherwise
        """
        if len(new_features) < min_samples:
            return False
            
        try:
            self.train(new_features)
            return True
        except Exception as e:
            print(f"Retraining failed: {e}")
            return False