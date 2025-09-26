# Smart Tourist Safety AI/ML System

## Overview

The Smart Tourist Safety AI/ML System is a hybrid pipeline that combines rule-based systems with machine learning and deep learning approaches to provide real-time safety assessment for tourists. The system uses multiple AI models to detect anomalies, assess risks, and generate alerts.

## Architecture

The system consists of five main components:

### 1. Rule-Based Geo-fencing
- **Purpose**: Immediate, deterministic response to critical situations
- **Input**: GPS coordinates (latitude, longitude, zone_type)
- **Output**: Instant alerts for restricted zones and SOS signals
- **Response Time**: < 100ms

### 2. Unsupervised Anomaly Detection (Isolation Forest)
- **Purpose**: Early warning system for unusual patterns
- **Algorithm**: Isolation Forest (scikit-learn)
- **Features**: [distance_per_min, inactivity_duration, deviation_from_route, speed]
- **Output**: Anomaly score (0 = anomaly, 1 = normal)

### 3. Sequence Modeling (LSTM/GRU Autoencoder)
- **Purpose**: Temporal pattern analysis to reduce false positives
- **Algorithm**: LSTM Autoencoder (PyTorch)
- **Input**: Sequential tourist movement data (sliding window)
- **Output**: Temporal risk score (0-1)

### 4. Safety Scoring & Alert Fusion
- **Purpose**: Unified decision engine combining all model outputs
- **Input**: Results from all models + additional context
- **Output**: Safety score (0-100) and alert decisions

### 5. Supervised Classification (Future)
- **Purpose**: Long-term improvement using historical incident data
- **Algorithm**: LightGBM/XGBoost
- **Status**: Planned for future implementation

## Data Flow

```
Tourist Location Data → Feature Extraction → Model Pipeline → Safety Assessment → Alert Generation
```

1. Tourist sends GPS location to backend
2. FeatureExtractor computes derived features
3. All models run in parallel:
   - Geo-fence checks for restricted zones
   - Isolation Forest detects anomalies
   - LSTM analyzes temporal patterns
4. SafetyScorer fuses results into unified score
5. System generates appropriate alerts

## API Endpoints

### Core Assessment
- `POST /ai/assess-safety` - Comprehensive safety assessment
- `POST /ai/sos-alert` - Handle emergency SOS signals
- `POST /ai/batch-assess` - Batch assessment for multiple tourists

### Management
- `GET /ai/pipeline-status` - Pipeline and model status
- `GET /ai/zone-info/{lat}/{lon}` - Zone information for location
- `GET /ai/tourist-history/{id}` - Cached feature history

### Training & Administration
- `POST /ai/train-models` - Train ML models (background task)
- `GET /ai/model-metrics` - Model performance metrics
- `POST /ai/clear-cache` - Clear feature cache

## Safety Score Calculation

Safety score ranges from 0-100:
- **> 80**: Safe (no alerts)
- **50-80**: Warning (notify tourist)
- **< 50**: Critical (notify authorities + tourist, auto E-FIR)

### Score Components

#### Geo-fencing Penalties
- SOS Signal: Score = 0 (critical)
- Restricted Zone: -30 points
- Risky Zone: -20 points
- Safe Zone: +5 points

#### ML Model Contributions
- Isolation Forest: Weight 30% (anomaly penalty)
- LSTM Autoencoder: Weight 25% (temporal penalty)
- Additional Context: Variable (SOS, manual flags, etc.)

#### Bonus Adjustments
- Safe Duration: +10 points per hour in safe zones

## Model Details

### Isolation Forest
- **Contamination Rate**: 0.1 (10% expected outliers)
- **Estimators**: 100 trees
- **Features**: 4 (distance_per_min, inactivity_duration, deviation_from_route, speed)
- **Training**: Unsupervised on historical normal behavior

### LSTM Autoencoder
- **Architecture**: Encoder-Decoder with LSTM layers
- **Sequence Length**: 10 time steps
- **Hidden Size**: 64 units
- **Layers**: 2 LSTM layers with dropout
- **Training**: Reconstruction loss on normal sequences

### Geo-fencing Zones

#### Restricted Zones (Critical Alert)
- Military areas
- International borders
- Prohibited regions

#### Risky Zones (Warning Alert)
- Dense forests
- Remote mountain areas
- High-crime regions

#### Safe Zones (No Alert)
- Tourist attractions
- Hotels and accommodations
- Government facilities

## Installation & Setup

### Dependencies
```bash
pip install -r requirements.txt
```

### Key Packages
- FastAPI + Uvicorn (web framework)
- scikit-learn (anomaly detection)
- PyTorch (deep learning)
- geopy + shapely (geospatial processing)
- pandas + numpy (data processing)

### Model Initialization
```python
from ai_ml.pipeline import TouristSafetyPipeline

# Initialize pipeline
pipeline = TouristSafetyPipeline()

# Load pre-trained models (if available)
pipeline.load_models()

# Or train models with data
training_features = [...]  # List of ProcessedFeatures
pipeline.train_models(training_features)
```

## Usage Examples

### Basic Safety Assessment
```python
from ai_ml.schemas.ai_schemas import TouristMovementData
from datetime import datetime

# Create movement data
data = TouristMovementData(
    tourist_id=123,
    latitude=28.6129,
    longitude=77.2295,
    timestamp=datetime.now(),
    speed=25.0,
    zone_type="safe"
)

# Assess safety
assessment = pipeline.assess_tourist_safety(data)

print(f"Safety Score: {assessment.safety_score}")
print(f"Risk Level: {assessment.risk_level}")
print(f"Alert Required: {assessment.should_alert_authorities}")
```

### Emergency SOS Handling
```python
# Handle SOS signal
emergency_assessment = pipeline.handle_sos_signal(
    tourist_id=123,
    latitude=28.6129,
    longitude=77.2295
)

# This will generate critical alert
assert emergency_assessment.safety_score == 0.0
assert emergency_assessment.risk_level == "critical"
```

## Configuration

Configuration is managed through `ai_ml/config/ai_config.py`:

```python
# Modify thresholds
CONFIG.safety_scoring.critical_threshold = 50.0
CONFIG.safety_scoring.warning_threshold = 80.0

# Adjust model parameters
CONFIG.lstm.sequence_length = 15
CONFIG.isolation_forest.contamination = 0.15
```

## Performance Considerations

### Real-time Requirements
- **Geo-fencing**: < 100ms response time
- **Complete Assessment**: < 2 seconds
- **Batch Processing**: 10+ tourists per second

### Memory Usage
- Feature cache: ~50 features per tourist
- Model memory: ~100MB for all models
- GPU optional (CPU sufficient for most workloads)

### Scalability
- Stateless design enables horizontal scaling
- Background model training
- Cached feature storage for sequence modeling

## Monitoring & Maintenance

### Model Performance
- Monitor prediction accuracy
- Track false positive/negative rates
- Regular model retraining (weekly/monthly)

### System Health
- Check model training status
- Monitor API response times
- Validate zone configuration

### Alerts & Logging
- Log all critical assessments
- Track SOS signal handling
- Monitor anomaly detection rates

## Future Enhancements

### Supervised Learning
- Collect incident labels from real deployments
- Train LightGBM/XGBoost classifier
- Improve accuracy with historical data

### Advanced Features
- Weather integration
- Social media sentiment analysis
- Group travel pattern analysis
- Predictive risk modeling

### Performance Optimization
- Model quantization for mobile deployment
- Edge computing for offline operation
- Real-time model updates

## Support & Contact

For technical support or questions about the AI/ML system:
- Check system status: `GET /ai/pipeline-status`
- Review model metrics: `GET /ai/model-metrics`
- Clear caches if needed: `POST /ai/clear-cache`

---

**Note**: This AI/ML system is designed for the Smart India Hackathon 2025 and demonstrates a production-ready architecture for tourist safety monitoring.