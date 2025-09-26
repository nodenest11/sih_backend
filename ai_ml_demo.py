"""
Demo script for AI/ML Tourist Safety System
Demonstrates the full pipeline with sample data
"""
import asyncio
from datetime import datetime, timedelta
import numpy as np
from ai_ml.pipeline import TouristSafetyPipeline
from ai_ml.schemas.ai_schemas import TouristMovementData
from ai_ml.utils.training_utils import ModelTrainer

def demo_basic_assessment():
    """Demonstrate basic safety assessment"""
    print("=" * 60)
    print("DEMO 1: Basic Safety Assessment")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = TouristSafetyPipeline()
    
    # Test case 1: Tourist in safe area (India Gate, Delhi)
    print("\n1. Tourist at India Gate (Safe Zone):")
    safe_data = TouristMovementData(
        tourist_id=101,
        latitude=28.6129,
        longitude=77.2295,
        timestamp=datetime.now(),
        speed=5.0,
        zone_type="safe"
    )
    
    assessment = pipeline.assess_tourist_safety(safe_data)
    print(f"   Safety Score: {assessment.safety_score:.1f}/100")
    print(f"   Risk Level: {assessment.risk_level}")
    print(f"   Alert Tourist: {assessment.should_alert_tourist}")
    print(f"   Alert Authorities: {assessment.should_alert_authorities}")
    
    # Test case 2: Tourist in risky area
    print("\n2. Tourist in Dense Forest (Risky Zone):")
    risky_data = TouristMovementData(
        tourist_id=102,
        latitude=15.2993,
        longitude=73.7821,
        timestamp=datetime.now(),
        speed=2.0,
        zone_type="risky"
    )
    
    assessment = pipeline.assess_tourist_safety(risky_data)
    print(f"   Safety Score: {assessment.safety_score:.1f}/100")
    print(f"   Risk Level: {assessment.risk_level}")
    print(f"   Alert Tourist: {assessment.should_alert_tourist}")
    print(f"   Alert Authorities: {assessment.should_alert_authorities}")
    
    # Test case 3: Tourist in restricted area
    print("\n3. Tourist in Restricted Military Area:")
    restricted_data = TouristMovementData(
        tourist_id=103,
        latitude=28.5916,
        longitude=77.1886,
        timestamp=datetime.now(),
        speed=10.0,
        zone_type="restricted"
    )
    
    assessment = pipeline.assess_tourist_safety(restricted_data)
    print(f"   Safety Score: {assessment.safety_score:.1f}/100")
    print(f"   Risk Level: {assessment.risk_level}")
    print(f"   Alert Tourist: {assessment.should_alert_tourist}")
    print(f"   Alert Authorities: {assessment.should_alert_authorities}")

def demo_sos_handling():
    """Demonstrate SOS signal handling"""
    print("\n" + "=" * 60)
    print("DEMO 2: Emergency SOS Signal Handling")
    print("=" * 60)
    
    pipeline = TouristSafetyPipeline()
    
    # Emergency SOS signal
    print("\n🚨 Tourist sends SOS signal from unknown location:")
    assessment = pipeline.handle_sos_signal(
        tourist_id=999,
        latitude=25.3176,
        longitude=82.9739,
        additional_info={"emergency_details": "Lost in remote area"}
    )
    
    print(f"   Emergency ID: SOS_{assessment.tourist_id}_{int(assessment.timestamp.timestamp())}")
    print(f"   Safety Score: {assessment.safety_score:.1f}/100")
    print(f"   Risk Level: {assessment.risk_level}")
    print(f"   Location: {assessment.location}")
    print(f"   Alert Message: {assessment.alert_message}")
    print("   🚁 Emergency response dispatched!")

def demo_anomaly_detection():
    """Demonstrate anomaly detection with training"""
    print("\n" + "=" * 60)
    print("DEMO 3: ML Model Training & Anomaly Detection")
    print("=" * 60)
    
    # Generate synthetic training data
    trainer = ModelTrainer()
    print("\n📊 Generating synthetic training data...")
    training_features = trainer.generate_synthetic_training_data(
        num_tourists=50,
        days_per_tourist=3,
        samples_per_day=24
    )
    print(f"   Generated {len(training_features)} training samples")
    
    # Initialize pipeline and train models
    pipeline = TouristSafetyPipeline()
    print("\n🤖 Training AI/ML models...")
    training_results = pipeline.train_models(training_features)
    
    for model_name, result in training_results.items():
        if 'error' in result:
            print(f"   {model_name}: ❌ {result['error']}")
        else:
            print(f"   {model_name}: ✅ Trained successfully")
            if 'training_samples' in result:
                print(f"      - Training samples: {result['training_samples']}")
            if 'final_loss' in result:
                print(f"      - Final loss: {result['final_loss']:.6f}")
    
    # Test anomaly detection with unusual patterns
    print("\n🔍 Testing anomaly detection:")
    
    # Normal pattern
    normal_data = TouristMovementData(
        tourist_id=201,
        latitude=28.6129,
        longitude=77.2295,
        timestamp=datetime.now(),
        speed=15.0,  # Normal walking/driving speed
        zone_type="safe"
    )
    
    assessment = pipeline.assess_tourist_safety(normal_data)
    print(f"   Normal pattern - Safety Score: {assessment.safety_score:.1f}")
    
    # Anomalous pattern (very high speed + deviation)
    anomaly_data = TouristMovementData(
        tourist_id=202,
        latitude=28.6129,
        longitude=77.2295,
        timestamp=datetime.now(),
        speed=150.0,  # Abnormally high speed
        zone_type="unknown"
    )
    
    # Add historical data to show pattern
    historical_data = []
    for i in range(10):
        hist_data = TouristMovementData(
            tourist_id=202,
            latitude=28.6129 + np.random.normal(0, 0.01),
            longitude=77.2295 + np.random.normal(0, 0.01), 
            timestamp=datetime.now() - timedelta(minutes=30*(i+1)),
            speed=np.random.uniform(100, 200),  # Consistently high speed
            zone_type="unknown"
        )
        historical_data.append(hist_data)
    
    assessment = pipeline.assess_tourist_safety(anomaly_data, historical_data)
    print(f"   Anomaly pattern - Safety Score: {assessment.safety_score:.1f}")

def demo_pipeline_status():
    """Demonstrate pipeline status monitoring"""
    print("\n" + "=" * 60)
    print("DEMO 4: Pipeline Status & Monitoring")
    print("=" * 60)
    
    pipeline = TouristSafetyPipeline()
    
    # Get pipeline status
    status = pipeline.get_pipeline_status()
    
    print(f"\n📈 Pipeline Status (v{status['pipeline_version']}):")
    print(f"   Timestamp: {status['timestamp']}")
    
    print(f"\n🔧 Components Status:")
    for component, info in status['components'].items():
        print(f"   {component}:")
        print(f"      Status: {info['status']}")
        print(f"      Type: {info['type']}")
        if 'zones_loaded' in info:
            print(f"      Zones loaded: {info['zones_loaded']}")
    
    print(f"\n💾 Cache Status:")
    cache = status['cache_status']
    print(f"   Tourists in cache: {cache['tourists_in_cache']}")
    print(f"   Total cached features: {cache['total_cached_features']}")

def demo_batch_processing():
    """Demonstrate batch processing capabilities"""
    print("\n" + "=" * 60)
    print("DEMO 5: Batch Processing Multiple Tourists")
    print("=" * 60)
    
    pipeline = TouristSafetyPipeline()
    
    # Create batch of tourist data
    tourist_locations = [
        {"id": 301, "name": "Mumbai Marine Drive", "lat": 18.9435, "lon": 72.8234, "zone": "safe"},
        {"id": 302, "name": "Goa Beach", "lat": 15.2993, "lon": 73.7821, "zone": "safe"},
        {"id": 303, "name": "Himalayan Trek", "lat": 31.1048, "lon": 77.1734, "zone": "risky"},
        {"id": 304, "name": "Border Area", "lat": 34.0837, "lon": 74.8730, "zone": "restricted"},
        {"id": 305, "name": "Taj Mahal", "lat": 27.1751, "lon": 78.0421, "zone": "safe"}
    ]
    
    batch_data = []
    for loc in tourist_locations:
        data = TouristMovementData(
            tourist_id=loc["id"],
            latitude=loc["lat"],
            longitude=loc["lon"],
            timestamp=datetime.now(),
            speed=np.random.uniform(5, 30),
            zone_type=loc["zone"]
        )
        batch_data.append(data)
    
    print(f"\n🏃‍♂️ Processing {len(batch_data)} tourists simultaneously:")
    
    # Process batch
    start_time = datetime.now()
    assessments = pipeline.batch_assess_safety(batch_data)
    end_time = datetime.now()
    
    processing_time = (end_time - start_time).total_seconds()
    print(f"   Processing time: {processing_time:.3f} seconds")
    print(f"   Throughput: {len(batch_data)/processing_time:.1f} tourists/second")
    
    # Display results
    print(f"\n📊 Batch Results:")
    for i, (loc, assessment) in enumerate(zip(tourist_locations, assessments)):
        status_icon = "🚨" if assessment.risk_level == "critical" else "⚠️" if assessment.risk_level == "warning" else "✅"
        print(f"   {status_icon} Tourist {loc['id']} at {loc['name']}: {assessment.safety_score:.1f}/100 ({assessment.risk_level})")

def main():
    """Run all demos"""
    print("🏛️ Smart Tourist Safety AI/ML System - Demo")
    print("Smart India Hackathon 2025")
    print("Hybrid AI Pipeline: Rule-based + ML + Deep Learning")
    
    try:
        demo_basic_assessment()
        demo_sos_handling()
        demo_anomaly_detection()
        demo_pipeline_status()
        demo_batch_processing()
        
        print("\n" + "=" * 60)
        print("✅ All demos completed successfully!")
        print("=" * 60)
        print("\n🚀 The AI/ML system is ready for deployment!")
        print("📚 Check /docs endpoint for complete API documentation")
        print("🔧 Use /ai/pipeline-status for real-time monitoring")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()