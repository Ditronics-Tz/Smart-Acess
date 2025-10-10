# Access Control Microservice Architecture

## Overview

The Access Control Microservice is a dedicated service responsible for real-time card scanning, access validation, and gate control operations. This microservice operates independently from the main card management system while integrating seamlessly for authentication and logging purposes.

## System Architecture

### Microservice Separation

```
┌─────────────────────────────────────┐
│         Main Card Management        │
│              System                 │
│  ┌─────────────────────────────────┐│
│  │ • Card Creation & Management    ││
│  │ • User Management              ││
│  │ • PDF Generation               ││
│  │ • QR Code Verification         ││
│  │ • Audit Logging                ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
                  │
                  │ API Integration
                  ▼
┌─────────────────────────────────────┐
│       Access Control Service       │
│  ┌─────────────────────────────────┐│
│  │ • RFID Card Scanning           ││
│  │ • Real-time Access Validation  ││
│  │ • Gate Control                 ││
│  │ • Access Logging               ││
│  │ • Offline Mode Support         ││
│  │ • Hardware Integration         ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
                  │
                  │ Hardware Integration
                  ▼
┌─────────────────────────────────────┐
│        Physical Hardware           │
│  ┌─────────────────────────────────┐│
│  │ • RFID Readers                 ││
│  │ • Access Gates/Barriers        ││
│  │ • LED Indicators               ││
│  │ • Audio Feedback               ││
│  │ • Emergency Override           ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

## Microservice Components

### 1. Core Services

#### A. Card Validation Service
- **Purpose**: Validate RFID cards against the main system
- **Technology**: Python/FastAPI for high performance
- **Caching**: Redis for offline mode and performance
- **Database**: Local SQLite for offline operations

#### B. Access Control Engine
- **Purpose**: Make access decisions based on card data and policies
- **Rules Engine**: Time-based access, location-based access, role-based access
- **Policy Management**: Flexible access control policies

#### C. Hardware Interface Service
- **Purpose**: Interface with physical RFID readers and gate controllers
- **Protocols**: Serial communication, TCP/IP, GPIO
- **Hardware Support**: Multiple RFID reader types, various gate mechanisms

#### D. Synchronization Service
- **Purpose**: Sync with main card management system
- **Real-time**: WebSocket connections for live updates
- **Batch Sync**: Periodic synchronization for offline resilience

### 2. Database Schema (Access Control Service)

```sql
-- Local cache of valid cards
CREATE TABLE valid_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_uuid VARCHAR(36) UNIQUE NOT NULL,
    rfid_number VARCHAR(50) UNIQUE NOT NULL,
    card_type VARCHAR(20) NOT NULL,
    holder_name VARCHAR(255) NOT NULL,
    holder_id VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    access_level INTEGER DEFAULT 1,
    valid_from DATETIME,
    valid_until DATETIME,
    last_synced DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Access gate configurations
CREATE TABLE access_gates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gate_id VARCHAR(50) UNIQUE NOT NULL,
    gate_name VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    gate_type VARCHAR(50), -- entry, exit, bidirectional
    required_access_level INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    hardware_config JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Real-time access attempts
CREATE TABLE access_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfid_number VARCHAR(50),
    gate_id VARCHAR(50),
    access_granted BOOLEAN,
    denial_reason VARCHAR(255),
    holder_name VARCHAR(255),
    holder_id VARCHAR(50),
    card_type VARCHAR(20),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    synced_to_main BOOLEAN DEFAULT FALSE
);

-- System health and status
CREATE TABLE system_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gate_id VARCHAR(50),
    status VARCHAR(50), -- online, offline, error
    last_heartbeat DATETIME,
    error_message TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Access policies
CREATE TABLE access_policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_name VARCHAR(100) NOT NULL,
    policy_type VARCHAR(50), -- time_based, location_based, role_based
    conditions JSON,
    actions JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3. API Endpoints (Access Control Service)

#### Base URL: `http://access-control-service:8001/`

### Core Access Control Endpoints

#### 1. Card Validation
**POST** `/api/access/validate-card/`

Validates an RFID card for access.

**Request:**
```json
{
  "rfid_number": "RF123456789",
  "gate_id": "GATE_001",
  "timestamp": "2025-10-11T10:30:00Z"
}
```

**Response (Access Granted):**
```json
{
  "access_granted": true,
  "card_valid": true,
  "holder_info": {
    "name": "John Doe Smith",
    "id": "DIT/2024/01234",
    "type": "student",
    "access_level": 1
  },
  "gate_action": "open",
  "message": "Access granted",
  "timestamp": "2025-10-11T10:30:00Z",
  "session_id": "uuid-here"
}
```

**Response (Access Denied):**
```json
{
  "access_granted": false,
  "card_valid": false,
  "denial_reason": "Card not found",
  "gate_action": "keep_closed",
  "message": "Unknown card",
  "timestamp": "2025-10-11T10:30:00Z"
}
```

#### 2. Gate Status
**GET** `/api/gates/{gate_id}/status/`

Get current status of a specific gate.

**Response:**
```json
{
  "gate_id": "GATE_001",
  "status": "online",
  "last_access": "2025-10-11T10:25:00Z",
  "total_accesses_today": 156,
  "hardware_status": {
    "rfid_reader": "connected",
    "gate_mechanism": "operational",
    "network": "connected"
  }
}
```

#### 3. Bulk Access Log
**POST** `/api/access/log-batch/`

Submit multiple access attempts for logging.

**Request:**
```json
{
  "access_attempts": [
    {
      "rfid_number": "RF123456789",
      "gate_id": "GATE_001",
      "access_granted": true,
      "timestamp": "2025-10-11T10:30:00Z"
    }
  ]
}
```

#### 4. Sync Cards
**GET** `/api/sync/cards/`

Synchronize card data from main system.

**Query Parameters:**
- `since` (datetime): Get updates since this timestamp
- `gate_id` (string): Sync for specific gate

**Response:**
```json
{
  "updated_cards": 15,
  "new_cards": 5,
  "deactivated_cards": 2,
  "last_sync": "2025-10-11T10:30:00Z",
  "next_sync": "2025-10-11T10:35:00Z"
}
```

### 4. Hardware Integration

#### Supported Hardware Types

##### RFID Readers
- **Mifare Classic/Plus**: Common student ID cards
- **HID Proximity**: Staff access cards
- **Multi-protocol readers**: Support various card types
- **Long-range readers**: Vehicle access gates

##### Gate Mechanisms
- **Servo-controlled barriers**: Low-cost pedestrian gates
- **Magnetic locks**: Door access control
- **Motor-driven gates**: Vehicle access
- **Turnstiles**: High-traffic pedestrian areas

#### Communication Protocols
- **Serial (RS232/RS485)**: Traditional RFID readers
- **TCP/IP**: Network-connected devices
- **GPIO**: Direct hardware control (Raspberry Pi)
- **Modbus**: Industrial access control systems

### 5. Implementation Stack

#### Backend Technology
```python
# main.py - FastAPI application
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import redis
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="Access Control Service", version="1.0.0")

# Core endpoints
@app.post("/api/access/validate-card/")
async def validate_card(request: CardValidationRequest):
    # Card validation logic
    pass

@app.get("/api/gates/{gate_id}/status/")
async def get_gate_status(gate_id: str):
    # Gate status logic
    pass

# Hardware interface
class RFIDReader:
    def __init__(self, port: str, baud_rate: int = 9600):
        self.port = port
        self.baud_rate = baud_rate
    
    async def read_card(self) -> str:
        # Read RFID card
        pass

class GateController:
    def __init__(self, gpio_pin: int):
        self.gpio_pin = gpio_pin
    
    async def open_gate(self, duration: int = 3):
        # Control gate mechanism
        pass
```

#### Database Configuration
```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./access_control.db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)
```

#### Redis Caching
```python
# cache.py
import redis.asyncio as redis
import json

class CardCache:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
    
    async def get_card(self, rfid_number: str):
        data = await self.redis.get(f"card:{rfid_number}")
        return json.loads(data) if data else None
    
    async def set_card(self, rfid_number: str, card_data: dict, ttl: int = 3600):
        await self.redis.setex(
            f"card:{rfid_number}", 
            ttl, 
            json.dumps(card_data)
        )
```

### 6. Deployment Architecture

#### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  access-control:
    build: .
    ports:
      - "8001:8001"
    environment:
      - REDIS_URL=redis://redis:6379
      - MAIN_SYSTEM_URL=http://main-system:8000
    depends_on:
      - redis
    volumes:
      - ./data:/app/data
      - /dev/ttyUSB0:/dev/ttyUSB0  # Serial port for RFID reader
    privileged: true  # For GPIO access

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - access-control

volumes:
  redis_data:
```

### 7. Integration with Main System

#### Webhook Integration
```python
# webhooks.py
@app.post("/webhooks/card-updated/")
async def card_updated_webhook(card_data: dict):
    """Receive card updates from main system"""
    await update_local_card_cache(card_data)
    return {"status": "received"}

@app.post("/webhooks/card-deactivated/")
async def card_deactivated_webhook(card_uuid: str):
    """Handle card deactivation"""
    await deactivate_local_card(card_uuid)
    return {"status": "deactivated"}
```

#### Periodic Synchronization
```python
# sync.py
import asyncio
import httpx

class SyncService:
    def __init__(self, main_system_url: str):
        self.main_system_url = main_system_url
        self.client = httpx.AsyncClient()
    
    async def sync_cards(self):
        """Sync card data from main system"""
        response = await self.client.get(
            f"{self.main_system_url}/api/cards/active/"
        )
        cards = response.json()
        await self.update_local_cards(cards)
    
    async def push_access_logs(self):
        """Push access logs to main system"""
        logs = await self.get_unsynced_logs()
        for log in logs:
            await self.client.post(
                f"{self.main_system_url}/api/access/log/",
                json=log
            )
            await self.mark_log_synced(log['id'])

# Background task
async def periodic_sync():
    sync_service = SyncService("http://main-system:8000")
    while True:
        try:
            await sync_service.sync_cards()
            await sync_service.push_access_logs()
        except Exception as e:
            logger.error(f"Sync failed: {e}")
        await asyncio.sleep(300)  # Sync every 5 minutes
```

### 8. Security Considerations

#### Access Control Policies
```python
# policies.py
class AccessPolicy:
    def __init__(self):
        self.policies = []
    
    def check_time_based_access(self, card_type: str, current_time: datetime):
        """Check if access is allowed based on time"""
        if card_type == "student":
            # Students: 6 AM - 10 PM
            return 6 <= current_time.hour <= 22
        elif card_type == "staff":
            # Staff: 24/7 access
            return True
        elif card_type == "security":
            # Security: 24/7 access
            return True
        return False
    
    def check_location_access(self, card_type: str, gate_location: str):
        """Check location-based access"""
        if gate_location == "admin_building" and card_type == "student":
            return False  # Students can't access admin building
        return True
```

#### Offline Mode Security
```python
# offline_security.py
class OfflineSecurityManager:
    def __init__(self):
        self.grace_period = 24 * 3600  # 24 hours
    
    def is_card_valid_offline(self, card_data: dict):
        """Validate card when offline"""
        last_sync = datetime.fromisoformat(card_data['last_synced'])
        time_since_sync = (datetime.utcnow() - last_sync).total_seconds()
        
        if time_since_sync > self.grace_period:
            return False  # Card too old, deny access
        
        return card_data.get('is_active', False)
```

### 9. Monitoring and Alerting

#### Health Checks
```python
# health.py
@app.get("/health/")
async def health_check():
    """System health check"""
    status = {
        "service": "access-control",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # Check database
    try:
        await check_database_connection()
        status["components"]["database"] = "healthy"
    except Exception as e:
        status["components"]["database"] = f"unhealthy: {e}"
        status["status"] = "unhealthy"
    
    # Check Redis
    try:
        await check_redis_connection()
        status["components"]["redis"] = "healthy"
    except Exception as e:
        status["components"]["redis"] = f"unhealthy: {e}"
        status["status"] = "unhealthy"
    
    # Check hardware
    try:
        await check_hardware_status()
        status["components"]["hardware"] = "healthy"
    except Exception as e:
        status["components"]["hardware"] = f"unhealthy: {e}"
        status["status"] = "degraded"
    
    return status
```

#### Metrics Collection
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

access_attempts_total = Counter('access_attempts_total', 'Total access attempts', ['gate_id', 'result'])
access_duration = Histogram('access_validation_duration_seconds', 'Access validation duration')
active_gates = Gauge('active_gates_total', 'Number of active gates')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    if request.url.path.startswith("/api/access/"):
        access_duration.observe(duration)
    
    return response
```

### 10. Testing Strategy

#### Unit Tests
```python
# test_access_control.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_validate_valid_card():
    response = client.post("/api/access/validate-card/", json={
        "rfid_number": "RF123456789",
        "gate_id": "GATE_001"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["access_granted"] == True

def test_validate_invalid_card():
    response = client.post("/api/access/validate-card/", json={
        "rfid_number": "INVALID",
        "gate_id": "GATE_001"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["access_granted"] == False
```

#### Integration Tests
```python
# test_integration.py
async def test_card_sync_integration():
    """Test synchronization with main system"""
    # Mock main system response
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value.json.return_value = [
            {"rfid_number": "RF123", "is_active": True}
        ]
        
        sync_service = SyncService("http://mock-main")
        await sync_service.sync_cards()
        
        # Verify card was cached
        card = await get_cached_card("RF123")
        assert card["is_active"] == True
```

### 11. Performance Optimization

#### Caching Strategy
- **Redis Cache**: Hot card data (1-hour TTL)
- **Local SQLite**: Offline card validation
- **Memory Cache**: Frequently accessed policies

#### Database Optimization
- **Indexes**: On RFID numbers, gate IDs, timestamps
- **Partitioning**: Access logs by date
- **Cleanup Jobs**: Remove old access logs

#### Hardware Optimization
- **Connection Pooling**: Reuse serial connections
- **Async I/O**: Non-blocking hardware communication
- **Batch Processing**: Group hardware operations

### 12. Deployment Checklist

#### Prerequisites
- [ ] Docker and Docker Compose installed
- [ ] RFID reader hardware connected
- [ ] Gate control mechanisms configured
- [ ] Network connectivity to main system
- [ ] Redis instance available

#### Configuration
- [ ] Environment variables set
- [ ] Database migrations applied
- [ ] Hardware ports configured
- [ ] SSL certificates installed (if required)
- [ ] Monitoring tools configured

#### Testing
- [ ] Unit tests passing
- [ ] Integration tests with main system
- [ ] Hardware functionality verified
- [ ] Load testing completed
- [ ] Failover scenarios tested

### 13. Maintenance Operations

#### Regular Tasks
- **Daily**: Check system health, review access logs
- **Weekly**: Database cleanup, cache optimization
- **Monthly**: Hardware maintenance, security updates
- **Quarterly**: Performance review, capacity planning

#### Troubleshooting
- **Hardware Issues**: Check connections, restart services
- **Network Issues**: Verify connectivity, check DNS
- **Performance Issues**: Review metrics, optimize queries
- **Security Issues**: Check logs, update access policies

---

This microservice architecture provides a robust, scalable solution for real-time access control while maintaining clear separation from the main card management system.