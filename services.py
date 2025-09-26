from supabase_client import get_supabase_admin
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

supabase = get_supabase_admin()

class TouristService:
    @staticmethod
    def create_tourist(tourist_data: Dict[str, Any]) -> Dict[str, Any]:
        tourist_data['safety_score'] = 100
        tourist_data['created_at'] = datetime.utcnow().isoformat()
        
        result = supabase.table('tourists').insert(tourist_data).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_tourist(tourist_id: int) -> Optional[Dict[str, Any]]:
        result = supabase.table('tourists').select('*').eq('id', tourist_id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def update_safety_score(tourist_id: int, change: int, reason: str) -> bool:
        tourist = TouristService.get_tourist(tourist_id)
        if not tourist:
            return False
        
        new_score = max(0, min(100, tourist['safety_score'] + change))
        
        result = supabase.table('tourists').update({
            'safety_score': new_score,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', tourist_id).execute()
        
        return len(result.data) > 0

class LocationService:
    @staticmethod
    def update_location(tourist_id: int, latitude: float, longitude: float) -> Dict[str, Any]:
        location_data = {
            'tourist_id': tourist_id,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('locations').insert(location_data).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_all_locations() -> List[Dict[str, Any]]:
        result = supabase.table('locations').select('*').order('timestamp', desc=True).execute()
        
        latest_locations = {}
        for location in result.data:
            tourist_id = location['tourist_id']
            if tourist_id not in latest_locations:
                latest_locations[tourist_id] = location
        
        return list(latest_locations.values())

class AlertService:
    @staticmethod
    def create_panic_alert(tourist_id: int, latitude: float, longitude: float) -> Dict[str, Any]:
        tourist = TouristService.get_tourist(tourist_id)
        tourist_name = tourist['name'] if tourist else f"Tourist {tourist_id}"
        
        alert_data = {
            'tourist_id': tourist_id,
            'type': 'panic',
            'message': f"PANIC ALERT: {tourist_name} has triggered an emergency alert at coordinates ({latitude}, {longitude})",
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'active',
            'latitude': latitude,
            'longitude': longitude
        }
        
        result = supabase.table('alerts').insert(alert_data).execute()
        
        if result.data:
            TouristService.update_safety_score(tourist_id, -40, "Panic alert triggered")
        
        return result.data[0] if result.data else None
    
    @staticmethod
    def create_geofence_alert(tourist_id: int, latitude: float, longitude: float, zone_name: str) -> Dict[str, Any]:
        tourist = TouristService.get_tourist(tourist_id)
        tourist_name = tourist['name'] if tourist else f"Tourist {tourist_id}"
        
        alert_data = {
            'tourist_id': tourist_id,
            'type': 'geofence',
            'message': f"GEOFENCE ALERT: {tourist_name} has entered restricted zone '{zone_name}' at coordinates ({latitude}, {longitude})",
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'active',
            'latitude': latitude,
            'longitude': longitude
        }
        
        result = supabase.table('alerts').insert(alert_data).execute()
        
        if result.data:
            TouristService.update_safety_score(tourist_id, -20, f"Entered restricted zone: {zone_name}")
        
        return result.data[0] if result.data else None
    
    @staticmethod
    def get_all_alerts() -> List[Dict[str, Any]]:
        result = supabase.table('alerts').select('*').order('timestamp', desc=True).execute()
        return result.data or []
    
    @staticmethod
    def resolve_alert(alert_id: int) -> bool:
        result = supabase.table('alerts').update({
            'status': 'resolved'
        }).eq('id', alert_id).execute()
        
        return len(result.data) > 0

class AdminService:
    @staticmethod
    def initialize_database() -> Dict[str, Any]:
        restricted_zones = [
            {
                'name': 'Delhi Red Fort Restricted Area',
                'coordinates': json.dumps([
                    [28.6562, 77.2410], [28.6580, 77.2410], 
                    [28.6580, 77.2440], [28.6562, 77.2440], [28.6562, 77.2410]
                ]),
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'name': 'Goa Beach Danger Zone',
                'coordinates': json.dumps([
                    [15.2993, 74.1240], [15.3010, 74.1240], 
                    [15.3010, 74.1260], [15.2993, 74.1260], [15.2993, 74.1240]
                ]),
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'name': 'Shillong Restricted Military Zone',
                'coordinates': json.dumps([
                    [25.5788, 91.8933], [25.5800, 91.8933], 
                    [25.5800, 91.8950], [25.5788, 91.8950], [25.5788, 91.8933]
                ]),
                'created_at': datetime.utcnow().isoformat()
            }
        ]
        
        supabase.table('restricted_zones').delete().neq('id', 0).execute()
        result = supabase.table('restricted_zones').insert(restricted_zones).execute()
        
        return {
            'message': 'Database initialized with restricted zones',
            'restricted_zones_created': len(result.data) if result.data else 0
        }
    
    @staticmethod
    def health_check() -> Dict[str, Any]:
        try:
            result = supabase.table('tourists').select('count').execute()
            supabase_status = "connected"
        except Exception as e:
            supabase_status = f"error: {str(e)}"
        
        return {
            'status': 'healthy' if supabase_status == 'connected' else 'unhealthy',
            'timestamp': datetime.utcnow(),
            'supabase': supabase_status
        }