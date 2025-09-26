"""
Training utilities for AI/ML models
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from ..schemas.ai_schemas import ProcessedFeatures, TrainingData, ModelMetrics
from ..preprocessors.feature_extractor import FeatureExtractor
from ..preprocessors.data_preprocessor import DataPreprocessor

class ModelTrainer:
    """
    Utilities for training and validating AI/ML models
    """
    
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.preprocessor = DataPreprocessor()
        
    def generate_synthetic_training_data(self, 
                                       num_tourists: int = 100,
                                       days_per_tourist: int = 7,
                                       samples_per_day: int = 48) -> List[ProcessedFeatures]:
        """
        Generate synthetic training data for model development
        
        Args:
            num_tourists: Number of different tourists to simulate
            days_per_tourist: Number of days to simulate per tourist
            samples_per_day: Number of location samples per day (every 30 minutes = 48)
            
        Returns:
            List of ProcessedFeatures for training
        """
        synthetic_features = []
        
        # Define some tourist behavior patterns
        tourist_profiles = [
            {'type': 'normal', 'speed_range': (0, 60), 'deviation_range': (0, 200)},
            {'type': 'adventurous', 'speed_range': (0, 80), 'deviation_range': (0, 1000)},
            {'type': 'cautious', 'speed_range': (0, 30), 'deviation_range': (0, 100)},
        ]
        
        # Sample locations (Indian tourist destinations)
        base_locations = [
            {'name': 'Delhi', 'lat': 28.6129, 'lon': 77.2295, 'type': 'safe'},
            {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777, 'type': 'safe'},
            {'name': 'Goa Beach', 'lat': 15.2993, 'lon': 73.7821, 'type': 'safe'},
            {'name': 'Himalayan Trek', 'lat': 31.1048, 'lon': 77.1734, 'type': 'risky'},
            {'name': 'Agra', 'lat': 27.1751, 'lon': 78.0421, 'type': 'safe'},
        ]
        
        for tourist_id in range(1, num_tourists + 1):
            # Assign random profile
            profile = np.random.choice(tourist_profiles)
            base_location = np.random.choice(base_locations)
            
            # Generate timeline
            start_date = datetime.now() - timedelta(days=days_per_tourist)
            
            for day in range(days_per_tourist):
                current_date = start_date + timedelta(days=day)
                
                for sample in range(samples_per_day):
                    timestamp = current_date + timedelta(minutes=sample * 30)
                    
                    # Generate realistic movement
                    lat_offset = np.random.normal(0, 0.01)  # ~1km variation
                    lon_offset = np.random.normal(0, 0.01)
                    
                    latitude = base_location['lat'] + lat_offset
                    longitude = base_location['lon'] + lon_offset
                    
                    # Generate derived features
                    speed = np.random.uniform(
                        profile['speed_range'][0], 
                        profile['speed_range'][1]
                    )
                    
                    distance_per_min = speed / 60 * 1000  # Convert to m/min
                    
                    # Inactivity duration (occasional stops)
                    if np.random.random() < 0.1:  # 10% chance of being stationary
                        inactivity_duration = np.random.uniform(15, 120)  # 15min to 2 hours
                        distance_per_min = 0
                    else:
                        inactivity_duration = 0
                    
                    # Route deviation
                    deviation_from_route = np.random.uniform(
                        profile['deviation_range'][0],
                        profile['deviation_range'][1]
                    )
                    
                    # Create feature object
                    features = ProcessedFeatures(
                        tourist_id=tourist_id,
                        timestamp=timestamp,
                        latitude=latitude,
                        longitude=longitude,
                        speed=speed,
                        zone_type=base_location['type'],
                        distance_per_min=distance_per_min,
                        inactivity_duration=inactivity_duration,
                        deviation_from_route=deviation_from_route,
                        recent_locations=[]
                    )
                    
                    synthetic_features.append(features)
                    
        return synthetic_features
    
    def create_anomaly_labels(self, features: List[ProcessedFeatures]) -> List[int]:
        """
        Create labels for supervised anomaly detection (future use)
        
        Returns:
            List of labels (0 = normal, 1 = anomaly)
        """
        labels = []
        
        for feature in features:
            is_anomaly = False
            
            # Define anomaly conditions
            if feature.distance_per_min > 2000:  # Very fast movement
                is_anomaly = True
            elif feature.inactivity_duration > 180:  # >3 hours inactive
                is_anomaly = True
            elif feature.deviation_from_route > 2000:  # Very far from route
                is_anomaly = True
            elif feature.zone_type == 'restricted':
                is_anomaly = True
                
            labels.append(1 if is_anomaly else 0)
            
        return labels
    
    def split_training_data(self, 
                           features: List[ProcessedFeatures],
                           test_size: float = 0.2,
                           random_state: int = 42) -> Tuple[List[ProcessedFeatures], List[ProcessedFeatures]]:
        """
        Split data into training and test sets
        """
        return train_test_split(
            features, 
            test_size=test_size, 
            random_state=random_state
        )
    
    def evaluate_anomaly_detection(self,
                                 predictions: List[int],
                                 true_labels: List[int]) -> Dict[str, Any]:
        """
        Evaluate anomaly detection performance
        """
        from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
        
        metrics = {
            'accuracy': accuracy_score(true_labels, predictions),
            'precision': precision_score(true_labels, predictions, average='binary'),
            'recall': recall_score(true_labels, predictions, average='binary'),
            'f1_score': f1_score(true_labels, predictions, average='binary'),
            'confusion_matrix': confusion_matrix(true_labels, predictions).tolist(),
            'classification_report': classification_report(true_labels, predictions, output_dict=True)
        }
        
        return metrics
    
    def create_training_report(self, 
                             training_results: Dict[str, Any],
                             model_name: str) -> str:
        """
        Generate a training report in markdown format
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# AI/ML Model Training Report

## Model: {model_name}
**Training Date:** {timestamp}

## Training Summary
- **Training Samples:** {training_results.get('training_samples', 'N/A')}
- **Feature Count:** {training_results.get('feature_count', 'N/A')}
- **Training Duration:** {training_results.get('training_duration', 'N/A')}

## Model Configuration
```json
{training_results.get('config', {})}
```

## Training Results
"""
        
        if 'final_loss' in training_results:
            report += f"- **Final Loss:** {training_results['final_loss']:.6f}\n"
            
        if 'contamination_rate' in training_results:
            report += f"- **Contamination Rate:** {training_results['contamination_rate']}\n"
            
        if 'reconstruction_threshold' in training_results:
            report += f"- **Reconstruction Threshold:** {training_results['reconstruction_threshold']:.6f}\n"
            
        if 'detected_anomalies' in training_results:
            report += f"- **Detected Anomalies:** {training_results['detected_anomalies']}\n"
            report += f"- **Normal Samples:** {training_results['normal_samples']}\n"
            
        report += """
## Next Steps
1. Evaluate model performance on test data
2. Fine-tune hyperparameters if needed
3. Deploy model for real-time inference
4. Monitor model performance in production
5. Collect feedback for continuous improvement

---
*Generated by Tourist Safety AI/ML Pipeline*
"""
        
        return report
    
    def visualize_training_data(self, 
                              features: List[ProcessedFeatures],
                              output_dir: str = "./plots") -> Dict[str, str]:
        """
        Create visualizations of training data
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert to DataFrame for easier plotting
        df = self.preprocessor.create_feature_dataframe(features)
        
        plots = {}
        
        # Feature distributions
        plt.figure(figsize=(15, 10))
        
        # Distance per minute distribution
        plt.subplot(2, 3, 1)
        plt.hist(df['distance_per_min'], bins=50, alpha=0.7)
        plt.title('Distance per Minute Distribution')
        plt.xlabel('Distance (m/min)')
        plt.ylabel('Frequency')
        
        # Speed distribution
        plt.subplot(2, 3, 2)
        plt.hist(df['speed'], bins=50, alpha=0.7)
        plt.title('Speed Distribution')
        plt.xlabel('Speed')
        plt.ylabel('Frequency')
        
        # Inactivity duration
        plt.subplot(2, 3, 3)
        plt.hist(df['inactivity_duration'], bins=50, alpha=0.7)
        plt.title('Inactivity Duration Distribution')
        plt.xlabel('Duration (minutes)')
        plt.ylabel('Frequency')
        
        # Route deviation
        plt.subplot(2, 3, 4)
        plt.hist(df['deviation_from_route'], bins=50, alpha=0.7)
        plt.title('Route Deviation Distribution')
        plt.xlabel('Deviation (meters)')
        plt.ylabel('Frequency')
        
        # Zone type distribution
        plt.subplot(2, 3, 5)
        zone_counts = df['zone_type'].value_counts()
        plt.bar(zone_counts.index, zone_counts.values)
        plt.title('Zone Type Distribution')
        plt.xlabel('Zone Type')
        plt.ylabel('Count')
        
        # Geographic scatter
        plt.subplot(2, 3, 6)
        plt.scatter(df['longitude'], df['latitude'], alpha=0.5, s=1)
        plt.title('Tourist Locations')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        
        plt.tight_layout()
        plot_path = os.path.join(output_dir, 'feature_distributions.png')
        plt.savefig(plot_path)
        plt.close()
        
        plots['feature_distributions'] = plot_path
        
        return plots
    
    def create_validation_dataset(self,
                                features: List[ProcessedFeatures],
                                anomaly_rate: float = 0.1) -> Tuple[List[ProcessedFeatures], List[int]]:
        """
        Create a validation dataset with known anomalies
        """
        validation_features = []
        validation_labels = []
        
        normal_count = int(len(features) * (1 - anomaly_rate))
        anomaly_count = len(features) - normal_count
        
        # Add normal samples
        normal_features = features[:normal_count]
        for feature in normal_features:
            validation_features.append(feature)
            validation_labels.append(0)  # Normal
            
        # Create anomalous samples by modifying existing features
        base_features = np.random.choice(features, anomaly_count, replace=True)
        
        for feature in base_features:
            # Create anomalous version
            anomalous_feature = ProcessedFeatures(
                tourist_id=feature.tourist_id,
                timestamp=feature.timestamp,
                latitude=feature.latitude,
                longitude=feature.longitude,
                speed=feature.speed * np.random.uniform(3, 10),  # Abnormally high speed
                zone_type='restricted',  # Make it restricted
                distance_per_min=feature.distance_per_min * np.random.uniform(5, 15),
                inactivity_duration=np.random.uniform(300, 600),  # 5-10 hours
                deviation_from_route=np.random.uniform(5000, 10000),  # Far from route
                recent_locations=feature.recent_locations
            )
            
            validation_features.append(anomalous_feature)
            validation_labels.append(1)  # Anomaly
            
        return validation_features, validation_labels