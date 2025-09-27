# 🚀 Frontend Developer's Guide - Smart Tourist Safety System API

## 📖 Quick Start Guide for Frontend Integration

This guide provides frontend developers with everything needed to integrate with the Smart Tourist Safety System backend API.

---

## 🌐 Base URLs & Environment Setup

### Development
```
Base URL: http://localhost:8000
Docs: http://localhost:8000/docs
Health: http://localhost:8000/health
```

### Production
```
Base URL: https://your-production-domain.com
Docs: https://your-production-domain.com/docs
Health: https://your-production-domain.com/health
```

### Headers Required
```javascript
{
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

---

## 🎯 Core API Endpoints for Frontend

### 1. System Health Check

#### `GET /health`
**Purpose**: Check if backend is running and database is connected
**When to use**: App startup, periodic health checks

```javascript
// Example Request
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => {
    console.log('Backend Status:', data.status); // "healthy" or "unhealthy"
    console.log('Database:', data.database);     // "connected" or "disconnected"
  });
```

**Response Example**:
```json
{
  "status": "healthy",
  "timestamp": 1695825600,
  "version": "3.0.0",
  "database": "connected"
}
```

---

## 👤 Tourist Management APIs

### 2. Register New Tourist

#### `POST /registerTourist` ⭐ **REQUIRED ENDPOINT**
**Purpose**: Register a new user in the system
**When to use**: User sign-up, profile creation

```javascript
// Example Request
const registerTourist = async (userData) => {
  const response = await fetch('http://localhost:8000/registerTourist', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: "John Doe",
      contact: "+91-9876543210",        // Must be unique
      email: "john.doe@email.com",      // Optional
      emergency_contact: "+91-9876543211",
      age: 25,                          // Optional
      nationality: "Indian",            // Optional, defaults to "Indian"
      trip_info: {                      // Optional JSON object
        destination: "Delhi",
        duration: "3 days",
        hotel: "Hotel Name"
      }
    })
  });
  
  if (response.ok) {
    const tourist = await response.json();
    localStorage.setItem('tourist_id', tourist.id);
    return tourist;
  } else {
    const error = await response.json();
    throw new Error(error.detail);
  }
};
```

**Response Example**:
```json
{
  "id": 123,
  "name": "John Doe",
  "contact": "+91-9876543210",
  "email": "john.doe@email.com",
  "emergency_contact": "+91-9876543211",
  "safety_score": 100,
  "age": 25,
  "nationality": "Indian",
  "is_active": true,
  "created_at": "2025-09-27T10:30:00Z"
}
```

**Error Handling**:
```javascript
// Handle duplicate contact error
catch (error) {
  if (error.message.includes("already exists")) {
    alert("This phone number is already registered");
  }
}
```

### 3. Get Tourist Details

#### `GET /api/v1/tourists/{id}`
**Purpose**: Retrieve tourist profile and current safety score
**When to use**: Profile page, dashboard, safety score display

```javascript
// Example Request
const getTouristDetails = async (touristId) => {
  const response = await fetch(`http://localhost:8000/api/v1/tourists/${touristId}`);
  
  if (response.ok) {
    const tourist = await response.json();
    return {
      name: tourist.name,
      safety_score: tourist.safety_score,  // 0-100 scale
      last_location_update: tourist.last_location_update,
      trip_info: tourist.trip_info
    };
  }
};
```

---

## 📍 Location Tracking APIs

### 4. Send Location Update

#### `POST /sendLocation` ⭐ **REQUIRED ENDPOINT**
**Purpose**: Send GPS location and trigger AI safety assessment
**When to use**: Every 30-60 seconds while app is active, location changes

```javascript
// Example Request with Geolocation API
const sendLocation = async () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(async (position) => {
      const locationData = {
        tourist_id: parseInt(localStorage.getItem('tourist_id')),
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        altitude: position.coords.altitude || null,        // Optional
        accuracy: position.coords.accuracy || null,        // Optional  
        speed: position.coords.speed || null,              // Optional (m/s)
        heading: position.coords.heading || null           // Optional (degrees)
      };
      
      const response = await fetch('http://localhost:8000/sendLocation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(locationData)
      });
      
      if (response.ok) {
        const location = await response.json();
        console.log('Location sent, AI assessment triggered');
        
        // Check if AI found any safety concerns
        // AI assessment runs in background, check alerts separately
        checkForAlerts();
      }
    });
  }
};

// Auto-send location every minute
setInterval(sendLocation, 60000);
```

**Response Example**:
```json
{
  "id": 456,
  "tourist_id": 123,
  "latitude": 28.6139,
  "longitude": 77.2090,
  "altitude": 216.5,
  "speed": 5.2,
  "timestamp": "2025-09-27T10:35:00Z",
  "created_at": "2025-09-27T10:35:00Z"
}
```

### 5. Get All Tourist Locations

#### `GET /api/v1/locations/all`
**Purpose**: Get current locations of all tourists (for admin/monitoring)
**When to use**: Admin dashboard, family tracking

```javascript
// Example Request
const getAllLocations = async () => {
  const response = await fetch('http://localhost:8000/api/v1/locations/all');
  const locations = await response.json();
  
  // Use for map display
  locations.forEach(location => {
    addMarkerToMap(location.latitude, location.longitude, location.tourist_name);
  });
};
```

---

## 🚨 Emergency & Alert APIs

### 6. Emergency SOS Button

#### `POST /pressSOS` ⭐ **REQUIRED ENDPOINT**
**Purpose**: Send immediate emergency alert
**When to use**: Emergency button press, panic situations

```javascript
// Example Request
const pressSOS = async (emergencyMessage = "Emergency help needed!") => {
  // Get current location first
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(async (position) => {
      const sosData = {
        tourist_id: parseInt(localStorage.getItem('tourist_id')),
        message: emergencyMessage,
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      };
      
      const response = await fetch('http://localhost:8000/pressSOS', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sosData)
      });
      
      if (response.ok) {
        const alert = await response.json();
        
        // Show confirmation to user
        alert('🆘 Emergency alert sent! Authorities have been notified.');
        
        // Update UI to show emergency state
        showEmergencyMode();
        
        return alert;
      }
    });
  }
};

// Emergency button click handler
document.getElementById('sosButton').addEventListener('click', () => {
  if (confirm('Send emergency alert to authorities?')) {
    pressSOS();
  }
});
```

### 7. Get Alerts

#### `GET /getAlerts` ⭐ **REQUIRED ENDPOINT**
**Purpose**: Retrieve alerts for tourist or all alerts (admin)
**When to use**: Check for new alerts, alert history, notifications

```javascript
// Example Request - Get alerts for specific tourist
const getAlertsForTourist = async (touristId) => {
  const response = await fetch(`http://localhost:8000/getAlerts?tourist_id=${touristId}&status=active`);
  const alerts = await response.json();
  
  alerts.forEach(alert => {
    showNotification(alert);
  });
};

// Example Request - Get all active alerts (admin)
const getAllActiveAlerts = async () => {
  const response = await fetch('http://localhost:8000/getAlerts?status=active&severity=HIGH,CRITICAL');
  return await response.json();
};

// Check for new alerts every 30 seconds
setInterval(() => {
  const touristId = localStorage.getItem('tourist_id');
  if (touristId) {
    getAlertsForTourist(touristId);
  }
}, 30000);
```

**Response Example**:
```json
[
  {
    "id": 789,
    "tourist_id": 123,
    "type": "geofence",
    "severity": "MEDIUM",
    "message": "Tourist entered restricted area",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timestamp": "2025-09-27T10:40:00Z",
    "status": "active",
    "auto_generated": true,
    "ai_confidence": 0.85
  }
]
```

### 8. File Electronic FIR

#### `POST /fileEFIR` ⭐ **REQUIRED ENDPOINT**
**Purpose**: File electronic police report
**When to use**: Incident reporting, crime reporting

```javascript
// Example Request
const fileEFIR = async (incidentDetails) => {
  const efirData = {
    tourist_id: parseInt(localStorage.getItem('tourist_id')),
    incident_type: "theft",              // theft, assault, fraud, other
    description: incidentDetails.description,
    incident_date: incidentDetails.date,
    latitude: incidentDetails.latitude,
    longitude: incidentDetails.longitude,
    witnesses: incidentDetails.witnesses || [],
    evidence: incidentDetails.evidence || []
  };
  
  const response = await fetch('http://localhost:8000/fileEFIR', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(efirData)
  });
  
  if (response.ok) {
    const efir = await response.json();
    alert(`E-FIR filed successfully. Reference: ${efir.fir_number}`);
    return efir;
  }
};
```

---

## 🤖 AI & Safety Score APIs

### 9. Get AI Assessment

#### `GET /api/v1/ai/assessment/{tourist_id}`
**Purpose**: Get current AI safety assessment
**When to use**: Safety dashboard, risk indicators

```javascript
// Example Request
const getAIAssessment = async (touristId) => {
  const response = await fetch(`http://localhost:8000/api/v1/ai/assessment/${touristId}`);
  const assessment = await response.json();
  
  return {
    safety_score: assessment.safety_score,      // 0-100
    severity: assessment.severity,              // SAFE, WARNING, CRITICAL
    confidence: assessment.confidence_level,   // 0-1
    recommendations: assessment.recommended_action
  };
};
```

### 10. Force AI Assessment

#### `POST /api/v1/ai/assess/{tourist_id}`
**Purpose**: Trigger immediate AI safety check
**When to use**: Manual safety check, after incident

```javascript
// Example Request
const triggerAIAssessment = async (touristId) => {
  const response = await fetch(`http://localhost:8000/api/v1/ai/assess/${touristId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  });
  
  const assessment = await response.json();
  updateSafetyScore(assessment.safety_score);
};
```

---

## 🎨 Frontend Integration Examples

### Real-time Safety Dashboard

```javascript
class SafetyDashboard {
  constructor(touristId) {
    this.touristId = touristId;
    this.isTracking = false;
    this.init();
  }
  
  async init() {
    // Load tourist details
    const tourist = await this.getTouristDetails();
    this.updateProfileDisplay(tourist);
    
    // Start location tracking
    this.startLocationTracking();
    
    // Check for alerts periodically
    this.startAlertPolling();
  }
  
  startLocationTracking() {
    this.isTracking = true;
    
    const trackLocation = () => {
      if (this.isTracking && navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
          await this.sendLocation(position);
          
          // Update map
          this.updateMapMarker(position.coords.latitude, position.coords.longitude);
        });
      }
    };
    
    // Send location every minute
    trackLocation();
    setInterval(trackLocation, 60000);
  }
  
  async sendLocation(position) {
    // Implementation as shown above
  }
  
  startAlertPolling() {
    setInterval(async () => {
      const alerts = await this.getAlerts();
      alerts.forEach(alert => this.showAlert(alert));
    }, 30000);
  }
  
  showAlert(alert) {
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${alert.severity.toLowerCase()}`;
    alertElement.innerHTML = `
      <h4>⚠️ ${alert.type.toUpperCase()} Alert</h4>
      <p>${alert.message}</p>
      <small>${new Date(alert.timestamp).toLocaleString()}</small>
    `;
    
    document.getElementById('alerts-container').appendChild(alertElement);
    
    // Show browser notification if supported
    if (Notification.permission === 'granted') {
      new Notification('Safety Alert', {
        body: alert.message,
        icon: '/alert-icon.png'
      });
    }
  }
}

// Initialize dashboard
const touristId = localStorage.getItem('tourist_id');
if (touristId) {
  const dashboard = new SafetyDashboard(touristId);
}
```

### Emergency Button Component

```javascript
class EmergencyButton {
  constructor() {
    this.createButton();
    this.bindEvents();
  }
  
  createButton() {
    const button = document.createElement('button');
    button.id = 'emergency-btn';
    button.className = 'emergency-button';
    button.innerHTML = '🆘 EMERGENCY';
    document.body.appendChild(button);
  }
  
  bindEvents() {
    document.getElementById('emergency-btn').addEventListener('click', () => {
      this.handleEmergency();
    });
  }
  
  async handleEmergency() {
    const confirmed = confirm('🆘 Send emergency alert to authorities?');
    if (confirmed) {
      try {
        await this.pressSOS();
        this.showEmergencyMode();
      } catch (error) {
        alert('Failed to send emergency alert. Please try again.');
      }
    }
  }
  
  async pressSOS() {
    // Implementation as shown above
  }
  
  showEmergencyMode() {
    document.body.classList.add('emergency-mode');
    document.getElementById('emergency-btn').innerHTML = '🚨 ALERT SENT';
    document.getElementById('emergency-btn').disabled = true;
  }
}

// Initialize emergency button
const emergencyButton = new EmergencyButton();
```

---

## 📱 Mobile App Integration Tips

### Location Permissions
```javascript
// Request location permission on app start
const requestLocationPermission = async () => {
  if (navigator.geolocation) {
    const permission = await navigator.permissions.query({name: 'geolocation'});
    
    if (permission.state === 'denied') {
      alert('Location access is required for safety monitoring');
    }
  }
};
```

### Background Location Tracking
```javascript
// Use service worker for background location updates
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/location-worker.js')
    .then(registration => {
      console.log('Location service worker registered');
    });
}
```

### Push Notifications
```javascript
// Setup push notifications for alerts
const setupPushNotifications = async () => {
  if ('Notification' in window) {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
      console.log('Push notifications enabled');
    }
  }
};
```

---

## ⚡ Error Handling & Best Practices

### Common Error Responses
```javascript
// Handle API errors consistently
const handleApiError = (response, data) => {
  switch (response.status) {
    case 400:
      console.error('Bad Request:', data.detail);
      break;
    case 404:
      console.error('Not Found:', data.detail);
      break;
    case 500:
      console.error('Server Error:', data.detail);
      break;
    default:
      console.error('API Error:', data);
  }
};

// Generic API call with error handling
const apiCall = async (url, options = {}) => {
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    
    if (!response.ok) {
      handleApiError(response, data);
      throw new Error(data.detail);
    }
    
    return data;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};
```

### Rate Limiting & Performance
```javascript
// Throttle location updates to avoid overwhelming the server
const throttle = (func, delay) => {
  let timeoutId;
  let lastExecTime = 0;
  return function (...args) {
    const currentTime = Date.now();
    
    if (currentTime - lastExecTime > delay) {
      func.apply(this, args);
      lastExecTime = currentTime;
    } else {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        func.apply(this, args);
        lastExecTime = Date.now();
      }, delay - (currentTime - lastExecTime));
    }
  };
};

// Throttled location sending (max once per minute)
const throttledSendLocation = throttle(sendLocation, 60000);
```

---

## 🔧 Testing Your Integration

### API Testing Checklist
```javascript
// Test all critical endpoints
const runAPITests = async () => {
  try {
    // 1. Test health endpoint
    const health = await fetch('/health');
    console.log('✅ Health check:', await health.json());
    
    // 2. Test tourist registration
    const tourist = await registerTourist(testData);
    console.log('✅ Tourist registered:', tourist.id);
    
    // 3. Test location update
    const location = await sendLocationTest(tourist.id);
    console.log('✅ Location sent:', location.id);
    
    // 4. Test SOS alert
    const alert = await pressSOSTest(tourist.id);
    console.log('✅ SOS alert:', alert.id);
    
    console.log('🎉 All API tests passed!');
    
  } catch (error) {
    console.error('❌ API test failed:', error);
  }
};
```

---

## 📋 Complete API Endpoint Summary

| Method | Endpoint | Purpose | Required |
|--------|----------|---------|----------|
| `GET` | `/health` | System health check | ✅ |
| `POST` | `/registerTourist` | User registration | ✅ |
| `POST` | `/sendLocation` | Location updates + AI | ✅ |
| `POST` | `/pressSOS` | Emergency alerts | ✅ |
| `GET` | `/getAlerts` | Retrieve alerts | ✅ |
| `POST` | `/fileEFIR` | Electronic FIR | ✅ |
| `GET` | `/api/v1/tourists/{id}` | Tourist details | Recommended |
| `GET` | `/api/v1/ai/assessment/{id}` | AI safety assessment | Recommended |
| `POST` | `/api/v1/ai/assess/{id}` | Force AI check | Optional |
| `GET` | `/api/v1/locations/all` | All locations (admin) | Optional |

---

## 🎯 Quick Integration Steps

1. **Setup API Base URL** and test `/health` endpoint
2. **Implement user registration** with `/registerTourist`
3. **Add location tracking** with `/sendLocation` every 60 seconds
4. **Setup emergency button** with `/pressSOS`
5. **Poll for alerts** with `/getAlerts` every 30 seconds
6. **Add incident reporting** with `/fileEFIR`
7. **Display safety scores** using AI assessment endpoints
8. **Test everything** with the provided examples

Your frontend is now ready to communicate with the Smart Tourist Safety System! 🚀

---

**📧 Need Help?** Check the interactive API docs at `http://localhost:8000/docs` for live testing and detailed schemas.