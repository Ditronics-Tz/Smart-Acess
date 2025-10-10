# Smart Access System Integration Architecture

## System Overview

This document outlines how the Access Control Microservice integrates with the existing Smart Access Card Management System to create a complete access control solution.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SMART ACCESS ECOSYSTEM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────┐    ┌─────────────────────────────────┐ │
│  │     Main Card Management        │    │    Access Control Service      │ │
│  │         System                  │    │        (New Microservice)      │ │
│  │  ┌─────────────────────────────┐│    │  ┌─────────────────────────────┐│ │
│  │  │ • User Management           ││    │  │ • RFID Card Scanning        ││ │
│  │  │ • Card Creation & Mgmt      ││◄──►│  │ • Real-time Validation      ││ │
│  │  │ • Student Management        ││    │  │ • Gate Control              ││ │
│  │  │ • Staff Management          ││    │  │ • Access Logging            ││ │
│  │  │ • Security Personnel Mgmt   ││    │  │ • Offline Mode Support      ││ │
│  │  │ • PDF Card Generation       ││    │  │ • Hardware Integration      ││ │
│  │  │ • QR Code Verification      ││    │  │ • Policy Engine             ││ │
│  │  │ • Audit Logging             ││    │  │ • Synchronization           ││ │
│  │  │ • Statistics & Reporting    ││    │  │ • Health Monitoring         ││ │
│  │  └─────────────────────────────┘│    │  └─────────────────────────────┘│ │
│  │                                 │    │                                 │ │
│  │  Technology Stack:              │    │  Technology Stack:              │ │
│  │  • Django REST Framework       │    │  • FastAPI                      │ │
│  │  • PostgreSQL                  │    │  • SQLite (local cache)        │ │
│  │  • Redis (optional caching)    │    │  • Redis (required caching)    │ │
│  │  • Port: 8000                  │    │  • Port: 8001                  │ │
│  └─────────────────────────────────┘    └─────────────────────────────────┘ │
│                   │                                        │                │
│                   │          API Integration               │                │
│                   │     ┌─────────────────────────┐       │                │
│                   └────►│  • REST API Calls       │◄──────┘                │
│                         │  • Webhook Notifications│                        │
│                         │  • Real-time Sync       │                        │
│                         │  • Access Log Forwarding│                        │
│                         └─────────────────────────┘                        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                            PHYSICAL LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────┐    ┌─────────────────────────────────┐ │
│  │        RFID Hardware            │    │      Gate Control Hardware     │ │
│  │  ┌─────────────────────────────┐│    │  ┌─────────────────────────────┐│ │
│  │  │ • RFID Readers (125kHz)     ││    │  │ • Servo Motors              ││ │
│  │  │ • Mifare Classic/Plus       ││    │  │ • Magnetic Locks            ││ │
│  │  │ • HID Proximity Cards       ││    │  │ • Electric Barriers         ││ │
│  │  │ • Multi-protocol Readers    ││    │  │ • Turnstiles                ││ │
│  │  │ • Long-range Readers        ││    │  │ • LED Indicators            ││ │
│  │  │ • Serial/USB Connection     ││    │  │ • Audio Feedback            ││ │
│  │  └─────────────────────────────┘│    │  │ • GPIO Control (RPi)        ││ │
│  └─────────────────────────────────┘    │  │ • Emergency Override        ││ │
│                                         │  └─────────────────────────────┘│ │
│                                         └─────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

### 1. Card Registration Flow
```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin/    │───►│  Main System    │───►│ Access Control  │
│Registration │    │ Creates Card    │    │ Receives Card   │
│  Officer    │    │ Record          │    │ Data via Sync   │
└─────────────┘    └─────────────────┘    └─────────────────┘
                            │                        │
                            ▼                        ▼
                   ┌─────────────────┐    ┌─────────────────┐
                   │  Card Data      │    │ Local Cache     │
                   │  Stored in      │    │ Updated for     │
                   │  Main Database  │    │ Fast Access     │
                   └─────────────────┘    └─────────────────┘
```

### 2. Real-time Access Control Flow
```
┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐
│ RFID Card    │───►│ Access Control  │───►│ Validation      │───►│ Gate Control │
│ Presented    │    │ Service Reads   │    │ Against Cache   │    │ Mechanism    │
│ to Reader    │    │ Card Number     │    │ & Policies      │    │ Activated    │
└──────────────┘    └─────────────────┘    └─────────────────┘    └──────────────┘
                             │                        │                     │
                             ▼                        ▼                     ▼
                   ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐
                   │ Hardware        │    │ Access Decision │    │ Physical     │
                   │ Integration     │    │ Logged Locally  │    │ Access       │
                   │ (Serial/GPIO)   │    │ & Queued for    │    │ Granted/     │
                   │                 │    │ Main System     │    │ Denied       │
                   └─────────────────┘    └─────────────────┘    └──────────────┘
```

### 3. Synchronization Flow
```
┌─────────────────┐    Periodic Sync    ┌─────────────────┐
│   Main System   │◄────(Every 5min)────│ Access Control  │
│                 │                     │    Service      │
│ • Card Updates  │──────Push New──────►│                 │
│ • Status Changes│      Card Data      │ • Cache Updates │
│ • Policy Updates│                     │ • Access Logs   │
└─────────────────┘                     └─────────────────┘
         ▲                                        │
         │              Webhook/API               │
         └──────────Push Access Logs─────────────┘
```

## Integration Points

### 1. API Integration

#### Main System → Access Control Service

**Card Synchronization Endpoint:**
- **GET** `/api/cards/active/` - Fetch active cards
- **POST** `/webhooks/card-updated/` - Real-time card updates
- **POST** `/webhooks/card-deactivated/` - Card deactivation

**Policy Updates:**
- **GET** `/api/policies/access/` - Fetch access policies
- **POST** `/webhooks/policy-updated/` - Policy changes

#### Access Control Service → Main System

**Access Logging:**
- **POST** `/api/access/logs/batch/` - Send access attempts
- **POST** `/api/access/alerts/` - Security alerts

**Health Monitoring:**
- **POST** `/api/monitoring/heartbeat/` - Service health
- **POST** `/api/monitoring/gate-status/` - Gate status updates

### 2. Database Integration

#### Main System Database (PostgreSQL)
```sql
-- Existing tables remain unchanged
-- New table for access control integration

CREATE TABLE access_control_gates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gate_id VARCHAR(50) UNIQUE NOT NULL,
    gate_name VARCHAR(100) NOT NULL,
    location_id UUID REFERENCES physical_locations(id),
    is_active BOOLEAN DEFAULT TRUE,
    service_url VARCHAR(255),
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE access_log_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    gate_id VARCHAR(50),
    total_attempts INTEGER DEFAULT 0,
    successful_attempts INTEGER DEFAULT 0,
    denied_attempts INTEGER DEFAULT 0,
    unique_cards INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Access Control Database (SQLite)
```sql
-- Local cache optimized for fast lookups
-- Tables already defined in implementation guide
```

### 3. Real-time Communication

#### WebSocket Integration
```python
# In Main System - Real-time card updates
class CardUpdateConsumer(AsyncWebsocketConsumer):
    async def card_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'card_update',
            'card_data': event['card_data']
        }))

# In Access Control Service - WebSocket client
class MainSystemWebSocketClient:
    async def connect_to_updates(self):
        uri = f"ws://{settings.MAIN_SYSTEM_URL}/ws/card-updates/"
        async with websockets.connect(uri) as websocket:
            async for message in websocket:
                await self.handle_card_update(json.loads(message))
```

#### Event-Driven Updates
```python
# Main System - Send updates when cards change
@receiver(post_save, sender=Card)
def card_updated_signal(sender, instance, **kwargs):
    # Notify access control service
    notify_access_control_service.delay(instance.card_uuid)

# Access Control Service - Handle card updates
async def handle_card_update(card_data):
    await update_local_card_cache(card_data)
    await invalidate_redis_cache(card_data['rfid_number'])
```

## Configuration Integration

### 1. Environment Variables

#### Main System (.env additions)
```env
# Access Control Integration
ACCESS_CONTROL_SERVICE_URL=http://access-control:8001
ACCESS_CONTROL_API_KEY=your-secure-api-key
ACCESS_CONTROL_WEBHOOK_SECRET=webhook-secret-key

# Gate Management
ENABLE_GATE_MANAGEMENT=true
DEFAULT_GATE_OPEN_DURATION=3
```

#### Access Control Service (.env)
```env
# Main System Integration
MAIN_SYSTEM_URL=http://main-system:8000
MAIN_SYSTEM_API_KEY=your-api-key
MAIN_SYSTEM_WEBHOOK_SECRET=webhook-secret-key

# Service Configuration
SYNC_INTERVAL=300
OFFLINE_GRACE_PERIOD=86400
CARD_CACHE_TTL=3600
```

### 2. Docker Compose Integration

```yaml
version: '3.8'

services:
  # Main system services
  web:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ACCESS_CONTROL_SERVICE_URL=http://access-control:8001
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    # ... existing postgres config

  # Access control service
  access-control:
    build: ./access-control-service
    ports:
      - "8001:8001"
    environment:
      - MAIN_SYSTEM_URL=http://web:8000
    depends_on:
      - redis
      - web
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0  # RFID reader
    privileged: true  # For GPIO access

  redis:
    image: redis:7-alpine
    # ... shared redis instance

  # Monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Security Integration

### 1. Authentication & Authorization

#### API Key Management
```python
# Main System - Generate API keys for access control service
class AccessControlAPIKey(models.Model):
    service_name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=255, unique=True)
    permissions = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True)

# Access Control Service - API key validation
async def validate_api_key(api_key: str) -> bool:
    # Validate against main system or local cache
    pass
```

#### Webhook Security
```python
# Webhook signature verification
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

### 2. Network Security

#### Internal Network Communication
```yaml
# docker-compose.yml - Internal network
networks:
  smart-access-internal:
    driver: bridge
    internal: true

services:
  web:
    networks:
      - smart-access-internal
      - default

  access-control:
    networks:
      - smart-access-internal
    # Only expose necessary ports externally
```

#### TLS/SSL Configuration
```nginx
# nginx.conf - SSL termination
server {
    listen 443 ssl;
    server_name access-control.example.com;
    
    ssl_certificate /etc/ssl/certs/access-control.crt;
    ssl_certificate_key /etc/ssl/private/access-control.key;
    
    location / {
        proxy_pass http://access-control:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring Integration

### 1. Metrics Collection

#### Prometheus Metrics
```python
# Shared metrics across services
from prometheus_client import Counter, Histogram, Gauge

# Access control metrics
access_attempts_total = Counter('access_attempts_total', 'Total access attempts', ['gate_id', 'result', 'card_type'])
access_validation_duration = Histogram('access_validation_duration_seconds', 'Time to validate access')
active_gates_gauge = Gauge('active_gates_total', 'Number of active gates')
card_cache_hits = Counter('card_cache_hits_total', 'Cache hit rate')

# Main system metrics
card_operations_total = Counter('card_operations_total', 'Card operations', ['operation', 'card_type'])
sync_operations_total = Counter('sync_operations_total', 'Sync operations', ['service', 'result'])
```

#### Health Check Integration
```python
# Combined health check endpoint
@app.get("/health/detailed")
async def detailed_health_check():
    health_status = {
        "main_system": await check_main_system_health(),
        "access_control": await check_access_control_health(),
        "database": await check_database_health(),
        "redis": await check_redis_health(),
        "hardware": await check_hardware_health()
    }
    
    overall_status = "healthy" if all(
        status == "healthy" for status in health_status.values()
    ) else "unhealthy"
    
    return {
        "overall_status": overall_status,
        "services": health_status,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 2. Logging Integration

#### Centralized Logging
```yaml
# docker-compose.yml - Add logging driver
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=main-system"

  access-control:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=access-control"
```

#### Log Correlation
```python
# Add correlation IDs for tracing requests across services
import uuid
from contextvars import ContextVar

correlation_id: ContextVar[str] = ContextVar('correlation_id')

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    corr_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
    correlation_id.set(corr_id)
    
    response = await call_next(request)
    response.headers['X-Correlation-ID'] = corr_id
    return response
```

## Deployment Strategy

### 1. Phased Rollout

#### Phase 1: Development Environment
- Deploy both services locally
- Test integration endpoints
- Validate hardware interfaces

#### Phase 2: Staging Environment
- Production-like hardware setup
- Load testing with realistic data
- Security testing and penetration testing

#### Phase 3: Production Deployment
- Blue-green deployment strategy
- Gradual migration of gates
- Monitoring and alerting setup

### 2. Migration Strategy

#### Existing System Migration
```python
# Migration script to prepare existing data
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Migrate existing cards to new format
        cards = Card.objects.all()
        for card in cards:
            # Ensure compatibility with access control service
            self.prepare_card_for_access_control(card)
```

#### Rollback Plan
```bash
#!/bin/bash
# rollback.sh - Quick rollback script
echo "Rolling back to previous version..."

# Stop access control service
docker-compose stop access-control

# Restore main system to standalone mode
docker-compose up -d web

echo "Rollback completed - system running in standalone mode"
```

## Performance Considerations

### 1. Caching Strategy

#### Multi-level Caching
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Memory Cache    │───►│ Redis Cache     │───►│ Database        │
│ (Hot cards)     │    │ (All active)    │    │ (Complete data) │
│ 100ms access    │    │ 1-5ms access    │    │ 10-50ms access  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Cache Invalidation
```python
# Smart cache invalidation
async def invalidate_card_cache(card_uuid: str, rfid_number: str):
    # Clear from all cache levels
    await memory_cache.delete(f"card:{rfid_number}")
    await redis_cache.delete(f"card:{rfid_number}")
    
    # Notify other service instances
    await publish_cache_invalidation(card_uuid)
```

### 2. Database Optimization

#### Read Replicas
```yaml
# Use read replicas for access control queries
services:
  db-master:
    image: postgres:15
    environment:
      - POSTGRES_REPLICATION_MODE=master

  db-replica:
    image: postgres:15
    environment:
      - POSTGRES_REPLICATION_MODE=replica
      - POSTGRES_MASTER_HOST=db-master
```

#### Connection Pooling
```python
# Optimize database connections
from sqlalchemy.pool import QueuePool

engine = create_async_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)
```

This integration architecture ensures seamless operation between your existing card management system and the new access control microservice, providing a robust, scalable, and maintainable solution for your Smart Access system.