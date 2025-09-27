# 🚔 Police Dashboard API Integration

## Overview
The Smart Tourist Safety System now includes integration with police dashboard systems to automatically forward panic/SOS alerts to law enforcement agencies.

## New API Endpoints

### 1. Send Alert to Police Dashboard
**Endpoint:** `POST /alerts/sendToPoliceDashboard`

**Purpose:** Forward panic/SOS alerts to police dashboard via API

**Parameters:**
- `alert_id` (int): The ID of the alert to send to police

**Request Example:**
```bash
POST /alerts/sendToPoliceDashboard?alert_id=123
```

**Response Example:**
```json
{
  "success": true,
  "message": "Alert successfully sent to police dashboard",
  "alert_id": 123,
  "police_response_status": 200,
  "timestamp": "2025-09-27T10:30:00"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Only panic/SOS alerts can be sent to police dashboard",
  "alert_id": 123,
  "timestamp": "2025-09-27T10:30:00"
}
```

## Automatic Integration

### SOS Alert Auto-Forwarding
When a tourist presses the SOS button (`POST /alerts/pressSOS`), the system now automatically:

1. ✅ Creates the SOS alert in the database
2. ✅ **Automatically forwards the alert to police dashboard**
3. ✅ Updates the alert as acknowledged by "Police Dashboard System"
4. ✅ Logs the police notification result

**Example SOS Flow:**
```bash
POST /alerts/pressSOS
{
  "tourist_id": 123,
  "latitude": 28.6139,
  "longitude": 77.2090,
  "message": "Emergency SOS - Tourist in distress!"
}
```

The system will automatically:
- Create the SOS alert
- Send it to police dashboard
- Return the alert with police notification status

## Police Dashboard Data Format

When sending to police dashboard, the system sends structured data:

```json
{
  "emergency_type": "TOURIST_SOS_PANIC",
  "alert_id": 123,
  "severity": "CRITICAL",
  "timestamp": "2025-09-27T10:30:00",
  "location": {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "address": "Lat: 28.6139, Lon: 77.2090"
  },
  "tourist_info": {
    "id": 123,
    "name": "John Doe",
    "contact": "+919876543210",
    "age": 30,
    "nationality": "American",
    "emergency_contact": "+919876543211"
  },
  "alert_details": {
    "message": "Emergency SOS - Tourist in distress!",
    "description": null,
    "ai_confidence": 0.95,
    "safety_score": 25
  },
  "response_required": true,
  "priority": "CRITICAL"
}
```

## Configuration

### Environment Variables
Add these to your `.env` file:

```bash
# Police Dashboard Integration
POLICE_DASHBOARD_URL=http://police-dashboard-api.gov.in/api/emergency-alerts
POLICE_API_KEY=your-police-api-key-here
```

### Default Values
If not configured:
- **URL:** `http://police-dashboard-api.gov.in/api/emergency-alerts`
- **API Key:** Empty (no authentication)

## Error Handling

The system handles various error scenarios:

### 1. Invalid Alert Type
- **Error:** Only panic/SOS alerts can be sent to police
- **HTTP Status:** 400 Bad Request

### 2. Alert Not Found
- **Error:** Alert not found
- **HTTP Status:** 404 Not Found

### 3. Tourist Not Found
- **Error:** Tourist not found
- **HTTP Status:** 404 Not Found

### 4. Police API Timeout
- **Error:** Timeout connecting to police dashboard
- **HTTP Status:** 200 OK (with success: false)

### 5. Police API Connection Error
- **Error:** Connection error to police dashboard
- **HTTP Status:** 200 OK (with success: false)

## Security Features

### API Headers
When communicating with police dashboard:

```http
Content-Type: application/json
Authorization: Bearer {POLICE_API_KEY}
X-Source-System: Tourist-Safety-System
X-Alert-Priority: CRITICAL
```

### Data Validation
- Only PANIC and SOS alert types can be sent
- Tourist information is validated before sending
- Alert severity is mapped to police priority levels

## Usage Examples

### Manual Police Notification
```python
import httpx

async def send_alert_to_police(alert_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:8000/alerts/sendToPoliceDashboard?alert_id={alert_id}"
        )
        result = response.json()
        
        if result["success"]:
            print(f"Alert {alert_id} sent to police!")
        else:
            print(f"Failed: {result['message']}")
```

### Check Alert Status
```python
async def check_alert_police_status(alert_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8000/alerts/{alert_id}")
        alert = response.json()
        
        if alert["acknowledged_by"] == "Police Dashboard System":
            print("Alert was sent to police dashboard!")
```

## Integration Benefits

### For Tourists
- ✅ Automatic emergency response
- ✅ Faster police notification
- ✅ No additional action required

### For Police
- ✅ Real-time emergency alerts
- ✅ Complete tourist information
- ✅ Precise location data
- ✅ Context and severity information

### For Tourism Authorities
- ✅ Automated emergency protocols
- ✅ Audit trail of police notifications
- ✅ Integration with existing systems
- ✅ Compliance with emergency response procedures

## Testing

Run the test script to verify the integration:

```bash
python test_police_api.py
```

This will:
1. Register a test tourist
2. Create an SOS alert
3. Send the alert to police dashboard
4. Check the alert status

## Monitoring and Logs

The system logs all police dashboard interactions:

```
CRITICAL - 🆘 SOS ALERT created for tourist 123: Emergency SOS!
CRITICAL - 🚔 PANIC ALERT 123 successfully sent to police dashboard
ERROR - Police dashboard API returned status 500: Internal Server Error
ERROR - Timeout sending alert 123 to police dashboard
```

## Future Enhancements

Planned improvements:
- 📍 Reverse geocoding for readable addresses
- 📊 Police dashboard response analytics
- 🔄 Retry mechanisms for failed notifications
- 📱 SMS/WhatsApp backup notifications
- 🎯 Regional police station routing based on location