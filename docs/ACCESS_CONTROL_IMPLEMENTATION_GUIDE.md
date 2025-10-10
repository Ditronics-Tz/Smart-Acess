# Access Control Microservice Implementation Guide

## Quick Start Guide

This guide provides step-by-step instructions to implement the Access Control Microservice for the Smart Access system.

## Phase 1: Basic Setup (Week 1-2)

### Step 1: Project Structure Setup

Create the microservice project structure:

```bash
mkdir smart-access-control
cd smart-access-control

# Create directory structure
mkdir -p {app,app/api,app/core,app/db,app/hardware,app/models,app/services}
mkdir -p {tests,docker,scripts,config}

# Create initial files
touch app/__init__.py
touch app/main.py
touch app/api/__init__.py
touch app/core/__init__.py
touch requirements.txt
touch Dockerfile
touch docker-compose.yml
```

### Step 2: Dependencies (requirements.txt)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
aiosqlite==0.19.0
redis[hiredis]==5.0.1
httpx==0.25.2
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
asyncio-mqtt==0.13.0
pyserial-asyncio==0.6
RPi.GPIO==0.7.1  # For Raspberry Pi GPIO
prometheus-client==0.19.0
pytest==7.4.3
pytest-asyncio==0.21.1
```

### Step 3: Core Application (app/main.py)

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from app.core.config import settings
from app.api.routes import router
from app.db.database import init_db
from app.services.sync_service import start_sync_service
from app.services.hardware_service import HardwareService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Access Control Service")
    await init_db()
    
    # Start background services
    asyncio.create_task(start_sync_service())
    
    # Initialize hardware
    hardware_service = HardwareService()
    await hardware_service.initialize()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Access Control Service")
    await hardware_service.cleanup()

app = FastAPI(
    title="Smart Access Control Service",
    description="Real-time RFID card scanning and access control",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "service": "access-control",
        "status": "healthy",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Step 4: Configuration (app/core/config.py)

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Service settings
    SERVICE_NAME: str = "access-control"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./access_control.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Main system integration
    MAIN_SYSTEM_URL: str = "http://localhost:8000"
    MAIN_SYSTEM_API_KEY: str = ""
    
    # Hardware settings
    RFID_READER_PORT: str = "/dev/ttyUSB0"
    RFID_READER_BAUD: int = 9600
    
    # Gate control GPIO pins (for Raspberry Pi)
    GATE_CONTROL_PINS: dict = {
        "GATE_001": 18,
        "GATE_002": 19
    }
    
    # Security settings
    ALLOWED_ORIGINS: List[str] = ["*"]
    OFFLINE_GRACE_PERIOD: int = 86400  # 24 hours
    
    # Sync settings
    SYNC_INTERVAL: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Step 5: Database Models (app/models/schemas.py)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()

class ValidCard(Base):
    __tablename__ = "valid_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    card_uuid = Column(String(36), unique=True, index=True, nullable=False)
    rfid_number = Column(String(50), unique=True, index=True, nullable=False)
    card_type = Column(String(20), nullable=False)
    holder_name = Column(String(255), nullable=False)
    holder_id = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    access_level = Column(Integer, default=1)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    last_synced = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())

class AccessGate(Base):
    __tablename__ = "access_gates"
    
    id = Column(Integer, primary_key=True, index=True)
    gate_id = Column(String(50), unique=True, index=True, nullable=False)
    gate_name = Column(String(100), nullable=False)
    location = Column(String(255))
    gate_type = Column(String(50))  # entry, exit, bidirectional
    required_access_level = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    hardware_config = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class AccessAttempt(Base):
    __tablename__ = "access_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    rfid_number = Column(String(50), index=True)
    gate_id = Column(String(50), index=True)
    access_granted = Column(Boolean)
    denial_reason = Column(String(255))
    holder_name = Column(String(255))
    holder_id = Column(String(50))
    card_type = Column(String(20))
    timestamp = Column(DateTime, default=func.now(), index=True)
    synced_to_main = Column(Boolean, default=False)

class SystemStatus(Base):
    __tablename__ = "system_status"
    
    id = Column(Integer, primary_key=True, index=True)
    gate_id = Column(String(50), index=True)
    status = Column(String(50))  # online, offline, error
    last_heartbeat = Column(DateTime, default=func.now())
    error_message = Column(Text)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

### Step 6: Pydantic Models (app/models/requests.py)

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class CardValidationRequest(BaseModel):
    rfid_number: str
    gate_id: str
    timestamp: Optional[datetime] = None

class CardValidationResponse(BaseModel):
    access_granted: bool
    card_valid: bool
    holder_info: Optional[Dict[str, Any]] = None
    gate_action: str  # open, keep_closed
    message: str
    denial_reason: Optional[str] = None
    timestamp: datetime
    session_id: Optional[str] = None

class AccessAttemptLog(BaseModel):
    rfid_number: str
    gate_id: str
    access_granted: bool
    timestamp: datetime
    holder_name: Optional[str] = None
    holder_id: Optional[str] = None
    denial_reason: Optional[str] = None

class GateStatusResponse(BaseModel):
    gate_id: str
    status: str
    last_access: Optional[datetime]
    total_accesses_today: int
    hardware_status: Dict[str, str]
```

### Step 7: Database Setup (app/db/database.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.schemas import Base

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

## Phase 2: Core Access Control Logic (Week 3-4)

### Step 8: Access Control Service (app/services/access_service.py)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import redis.asyncio as redis
import json
import uuid
import logging

from app.models.schemas import ValidCard, AccessAttempt, AccessGate
from app.models.requests import CardValidationRequest, CardValidationResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

class AccessControlService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
    
    async def validate_card_access(
        self, 
        request: CardValidationRequest, 
        db: AsyncSession
    ) -> CardValidationResponse:
        """Main card validation logic"""
        try:
            # Check cache first
            cached_card = await self._get_cached_card(request.rfid_number)
            
            if cached_card:
                card_data = cached_card
            else:
                # Check local database
                result = await db.execute(
                    select(ValidCard).where(ValidCard.rfid_number == request.rfid_number)
                )
                card = result.scalar_one_or_none()
                
                if not card:
                    return await self._deny_access(
                        request, db, "Card not found"
                    )
                
                card_data = {
                    "card_uuid": card.card_uuid,
                    "rfid_number": card.rfid_number,
                    "card_type": card.card_type,
                    "holder_name": card.holder_name,
                    "holder_id": card.holder_id,
                    "is_active": card.is_active,
                    "access_level": card.access_level,
                    "valid_from": card.valid_from.isoformat() if card.valid_from else None,
                    "valid_until": card.valid_until.isoformat() if card.valid_until else None,
                }
                
                # Cache for next time
                await self._cache_card(request.rfid_number, card_data)
            
            # Validate card status
            if not card_data.get("is_active", False):
                return await self._deny_access(
                    request, db, "Card is inactive"
                )
            
            # Check time-based validity
            now = datetime.utcnow()
            if card_data.get("valid_until"):
                valid_until = datetime.fromisoformat(card_data["valid_until"])
                if now > valid_until:
                    return await self._deny_access(
                        request, db, "Card has expired"
                    )
            
            # Check access policies
            gate_result = await db.execute(
                select(AccessGate).where(AccessGate.gate_id == request.gate_id)
            )
            gate = gate_result.scalar_one_or_none()
            
            if not gate or not gate.is_active:
                return await self._deny_access(
                    request, db, "Gate not found or inactive"
                )
            
            # Check access level
            if card_data.get("access_level", 0) < gate.required_access_level:
                return await self._deny_access(
                    request, db, "Insufficient access level"
                )
            
            # Check time-based access policies
            if not await self._check_time_based_access(card_data["card_type"], now):
                return await self._deny_access(
                    request, db, "Access not allowed at this time"
                )
            
            # Grant access
            return await self._grant_access(request, db, card_data)
            
        except Exception as e:
            logger.error(f"Error validating card: {e}")
            return await self._deny_access(
                request, db, "System error"
            )
    
    async def _grant_access(
        self, 
        request: CardValidationRequest, 
        db: AsyncSession,
        card_data: dict
    ) -> CardValidationResponse:
        """Grant access and log attempt"""
        session_id = str(uuid.uuid4())
        
        # Log access attempt
        access_log = AccessAttempt(
            rfid_number=request.rfid_number,
            gate_id=request.gate_id,
            access_granted=True,
            holder_name=card_data["holder_name"],
            holder_id=card_data["holder_id"],
            card_type=card_data["card_type"],
            timestamp=request.timestamp or datetime.utcnow()
        )
        db.add(access_log)
        await db.commit()
        
        logger.info(f"Access granted: {card_data['holder_name']} at {request.gate_id}")
        
        return CardValidationResponse(
            access_granted=True,
            card_valid=True,
            holder_info={
                "name": card_data["holder_name"],
                "id": card_data["holder_id"],
                "type": card_data["card_type"],
                "access_level": card_data["access_level"]
            },
            gate_action="open",
            message="Access granted",
            timestamp=request.timestamp or datetime.utcnow(),
            session_id=session_id
        )
    
    async def _deny_access(
        self, 
        request: CardValidationRequest, 
        db: AsyncSession,
        reason: str
    ) -> CardValidationResponse:
        """Deny access and log attempt"""
        # Log access attempt
        access_log = AccessAttempt(
            rfid_number=request.rfid_number,
            gate_id=request.gate_id,
            access_granted=False,
            denial_reason=reason,
            timestamp=request.timestamp or datetime.utcnow()
        )
        db.add(access_log)
        await db.commit()
        
        logger.warning(f"Access denied: {reason} for RFID {request.rfid_number} at {request.gate_id}")
        
        return CardValidationResponse(
            access_granted=False,
            card_valid=False,
            gate_action="keep_closed",
            message="Access denied",
            denial_reason=reason,
            timestamp=request.timestamp or datetime.utcnow()
        )
    
    async def _get_cached_card(self, rfid_number: str) -> dict:
        """Get card data from Redis cache"""
        try:
            data = await self.redis.get(f"card:{rfid_number}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None
    
    async def _cache_card(self, rfid_number: str, card_data: dict, ttl: int = 3600):
        """Cache card data in Redis"""
        try:
            await self.redis.setex(
                f"card:{rfid_number}",
                ttl,
                json.dumps(card_data, default=str)
            )
        except Exception as e:
            logger.error(f"Cache write error: {e}")
    
    async def _check_time_based_access(self, card_type: str, current_time: datetime) -> bool:
        """Check time-based access policies"""
        hour = current_time.hour
        
        if card_type == "student":
            # Students: 6 AM - 10 PM
            return 6 <= hour <= 22
        elif card_type in ["staff", "security"]:
            # Staff and security: 24/7 access
            return True
        
        return False
```

### Step 9: API Routes (app/api/routes.py)

```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List

from app.db.database import get_db
from app.models.requests import (
    CardValidationRequest, 
    CardValidationResponse,
    AccessAttemptLog,
    GateStatusResponse
)
from app.services.access_service import AccessControlService
from app.services.hardware_service import HardwareService

router = APIRouter()
access_service = AccessControlService()
hardware_service = HardwareService()

@router.post("/access/validate-card/", response_model=CardValidationResponse)
async def validate_card(
    request: CardValidationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Validate RFID card for access"""
    # Validate card
    response = await access_service.validate_card_access(request, db)
    
    # Control hardware if access granted
    if response.access_granted:
        background_tasks.add_task(
            hardware_service.open_gate, 
            request.gate_id, 
            duration=3
        )
    
    return response

@router.get("/gates/{gate_id}/status/", response_model=GateStatusResponse)
async def get_gate_status(
    gate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get status of specific gate"""
    # Get today's access count
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    result = await db.execute(
        select(func.count(AccessAttempt.id))
        .where(AccessAttempt.gate_id == gate_id)
        .where(AccessAttempt.timestamp >= today)
        .where(AccessAttempt.access_granted == True)
    )
    today_count = result.scalar() or 0
    
    # Get last access time
    result = await db.execute(
        select(AccessAttempt.timestamp)
        .where(AccessAttempt.gate_id == gate_id)
        .where(AccessAttempt.access_granted == True)
        .order_by(AccessAttempt.timestamp.desc())
        .limit(1)
    )
    last_access = result.scalar()
    
    # Check hardware status
    hw_status = await hardware_service.get_gate_status(gate_id)
    
    return GateStatusResponse(
        gate_id=gate_id,
        status="online",  # TODO: Implement actual status check
        last_access=last_access,
        total_accesses_today=today_count,
        hardware_status=hw_status
    )

@router.post("/access/log-batch/")
async def log_access_batch(
    access_logs: List[AccessAttemptLog],
    db: AsyncSession = Depends(get_db)
):
    """Log multiple access attempts"""
    for log in access_logs:
        access_attempt = AccessAttempt(
            rfid_number=log.rfid_number,
            gate_id=log.gate_id,
            access_granted=log.access_granted,
            holder_name=log.holder_name,
            holder_id=log.holder_id,
            denial_reason=log.denial_reason,
            timestamp=log.timestamp
        )
        db.add(access_attempt)
    
    await db.commit()
    
    return {"message": f"Logged {len(access_logs)} access attempts"}

@router.get("/sync/status/")
async def get_sync_status():
    """Get synchronization status with main system"""
    # TODO: Implement sync status check
    return {
        "last_sync": "2025-10-11T10:30:00Z",
        "sync_status": "healthy",
        "cached_cards": 1500,
        "pending_logs": 25
    }
```

## Phase 3: Hardware Integration (Week 5-6)

### Step 10: Hardware Service (app/services/hardware_service.py)

```python
import asyncio
import serial_asyncio
import logging
from typing import Dict, Optional
import json

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("GPIO not available - running in simulation mode")

from app.core.config import settings

logger = logging.getLogger(__name__)

class HardwareService:
    def __init__(self):
        self.rfid_reader = None
        self.gate_pins = settings.GATE_CONTROL_PINS
        self.gpio_initialized = False
    
    async def initialize(self):
        """Initialize hardware connections"""
        try:
            # Initialize RFID reader
            await self._init_rfid_reader()
            
            # Initialize GPIO for gate control
            if GPIO_AVAILABLE:
                await self._init_gpio()
            
            logger.info("Hardware service initialized successfully")
        except Exception as e:
            logger.error(f"Hardware initialization failed: {e}")
    
    async def _init_rfid_reader(self):
        """Initialize RFID reader connection"""
        try:
            self.rfid_reader = await serial_asyncio.open_serial_connection(
                url=settings.RFID_READER_PORT,
                baudrate=settings.RFID_READER_BAUD
            )
            logger.info(f"RFID reader connected on {settings.RFID_READER_PORT}")
        except Exception as e:
            logger.warning(f"RFID reader not available: {e}")
    
    async def _init_gpio(self):
        """Initialize GPIO pins for gate control"""
        if not GPIO_AVAILABLE:
            return
        
        try:
            GPIO.setmode(GPIO.BCM)
            for gate_id, pin in self.gate_pins.items():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)  # Gates closed by default
            
            self.gpio_initialized = True
            logger.info("GPIO initialized for gate control")
        except Exception as e:
            logger.error(f"GPIO initialization failed: {e}")
    
    async def read_rfid_card(self) -> Optional[str]:
        """Read RFID card from reader"""
        if not self.rfid_reader:
            return None
        
        try:
            reader, writer = self.rfid_reader
            data = await reader.read(100)
            
            # Parse RFID data (format depends on reader)
            rfid_data = data.decode('ascii').strip()
            
            # Basic validation
            if len(rfid_data) >= 8:  # Minimum RFID length
                logger.info(f"RFID card read: {rfid_data}")
                return rfid_data
            
        except Exception as e:
            logger.error(f"RFID read error: {e}")
        
        return None
    
    async def open_gate(self, gate_id: str, duration: int = 3):
        """Control gate opening"""
        if not self.gpio_initialized or gate_id not in self.gate_pins:
            logger.warning(f"Gate control not available for {gate_id}")
            return
        
        try:
            pin = self.gate_pins[gate_id]
            
            # Open gate
            GPIO.output(pin, GPIO.HIGH)
            logger.info(f"Gate {gate_id} opened")
            
            # Keep open for specified duration
            await asyncio.sleep(duration)
            
            # Close gate
            GPIO.output(pin, GPIO.LOW)
            logger.info(f"Gate {gate_id} closed")
            
        except Exception as e:
            logger.error(f"Gate control error: {e}")
    
    async def get_gate_status(self, gate_id: str) -> Dict[str, str]:
        """Get hardware status for gate"""
        status = {
            "rfid_reader": "unknown",
            "gate_mechanism": "unknown",
            "network": "connected"
        }
        
        # Check RFID reader
        if self.rfid_reader:
            status["rfid_reader"] = "connected"
        else:
            status["rfid_reader"] = "disconnected"
        
        # Check gate mechanism
        if gate_id in self.gate_pins and self.gpio_initialized:
            status["gate_mechanism"] = "operational"
        else:
            status["gate_mechanism"] = "not_configured"
        
        return status
    
    async def cleanup(self):
        """Cleanup hardware resources"""
        try:
            if self.rfid_reader:
                writer = self.rfid_reader[1]
                writer.close()
                await writer.wait_closed()
            
            if GPIO_AVAILABLE and self.gpio_initialized:
                GPIO.cleanup()
            
            logger.info("Hardware cleanup completed")
        except Exception as e:
            logger.error(f"Hardware cleanup error: {e}")

# Background task for continuous RFID reading
async def rfid_reader_task():
    """Background task to continuously read RFID cards"""
    hardware_service = HardwareService()
    access_service = AccessControlService()
    
    while True:
        try:
            rfid_number = await hardware_service.read_rfid_card()
            
            if rfid_number:
                # TODO: Determine gate_id from hardware configuration
                gate_id = "GATE_001"  # Default gate
                
                # Create validation request
                request = CardValidationRequest(
                    rfid_number=rfid_number,
                    gate_id=gate_id
                )
                
                # Validate card (you'll need to pass db session)
                # response = await access_service.validate_card_access(request, db)
                
                # Control gate based on response
                # if response.access_granted:
                #     await hardware_service.open_gate(gate_id)
        
        except Exception as e:
            logger.error(f"RFID reader task error: {e}")
        
        await asyncio.sleep(0.1)  # 100ms polling interval
```

### Step 11: Synchronization Service (app/services/sync_service.py)

```python
import asyncio
import httpx
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.models.schemas import ValidCard, AccessAttempt

logger = logging.getLogger(__name__)

class SyncService:
    def __init__(self):
        self.main_system_url = settings.MAIN_SYSTEM_URL
        self.api_key = settings.MAIN_SYSTEM_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def sync_cards_from_main(self) -> bool:
        """Synchronize card data from main system"""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Get active cards from main system
            response = await self.client.get(
                f"{self.main_system_url}/api/cards/",
                headers=headers,
                params={"is_active": True, "page_size": 1000}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch cards: {response.status_code}")
                return False
            
            cards_data = response.json()
            cards = cards_data.get("results", [])
            
            async with AsyncSessionLocal() as db:
                for card_data in cards:
                    await self._update_local_card(db, card_data)
                await db.commit()
            
            logger.info(f"Synchronized {len(cards)} cards from main system")
            return True
            
        except Exception as e:
            logger.error(f"Card sync failed: {e}")
            return False
    
    async def _update_local_card(self, db: AsyncSession, card_data: dict):
        """Update or create local card record"""
        try:
            # Extract card information
            card_uuid = card_data.get("card_uuid")
            rfid_number = card_data.get("rfid_number")
            is_active = card_data.get("is_active", True)
            card_type = card_data.get("card_type", "student")
            
            # Get holder information based on card type
            holder_info = self._extract_holder_info(card_data, card_type)
            
            # Check if card exists
            result = await db.execute(
                select(ValidCard).where(ValidCard.card_uuid == card_uuid)
            )
            existing_card = result.scalar_one_or_none()
            
            if existing_card:
                # Update existing card
                await db.execute(
                    update(ValidCard)
                    .where(ValidCard.card_uuid == card_uuid)
                    .values(
                        rfid_number=rfid_number,
                        is_active=is_active,
                        holder_name=holder_info["name"],
                        holder_id=holder_info["id"],
                        card_type=card_type,
                        last_synced=datetime.utcnow()
                    )
                )
            else:
                # Create new card
                new_card = ValidCard(
                    card_uuid=card_uuid,
                    rfid_number=rfid_number,
                    card_type=card_type,
                    holder_name=holder_info["name"],
                    holder_id=holder_info["id"],
                    is_active=is_active,
                    access_level=self._determine_access_level(card_type),
                    last_synced=datetime.utcnow()
                )
                db.add(new_card)
                
        except Exception as e:
            logger.error(f"Error updating local card {card_data.get('card_uuid')}: {e}")
    
    def _extract_holder_info(self, card_data: dict, card_type: str) -> dict:
        """Extract holder information from card data"""
        if card_type == "student" and card_data.get("student"):
            student = card_data["student"]
            return {
                "name": f"{student.get('first_name', '')} {student.get('surname', '')}".strip(),
                "id": student.get("registration_number", "")
            }
        elif card_type == "staff" and card_data.get("staff"):
            staff = card_data["staff"]
            return {
                "name": f"{staff.get('first_name', '')} {staff.get('surname', '')}".strip(),
                "id": staff.get("staff_number", "")
            }
        elif card_type == "security" and card_data.get("security_personnel"):
            security = card_data["security_personnel"]
            return {
                "name": security.get("full_name", ""),
                "id": security.get("employee_id", "")
            }
        
        return {"name": "Unknown", "id": "Unknown"}
    
    def _determine_access_level(self, card_type: str) -> int:
        """Determine access level based on card type"""
        access_levels = {
            "student": 1,
            "staff": 2,
            "security": 3
        }
        return access_levels.get(card_type, 1)
    
    async def push_access_logs_to_main(self) -> bool:
        """Push unsynced access logs to main system"""
        try:
            async with AsyncSessionLocal() as db:
                # Get unsynced logs
                result = await db.execute(
                    select(AccessAttempt)
                    .where(AccessAttempt.synced_to_main == False)
                    .limit(100)  # Process in batches
                )
                logs = result.scalars().all()
                
                if not logs:
                    return True
                
                # Prepare log data
                log_data = []
                for log in logs:
                    log_data.append({
                        "rfid_number": log.rfid_number,
                        "gate_id": log.gate_id,
                        "access_granted": log.access_granted,
                        "denial_reason": log.denial_reason,
                        "holder_name": log.holder_name,
                        "holder_id": log.holder_id,
                        "card_type": log.card_type,
                        "timestamp": log.timestamp.isoformat()
                    })
                
                # Send to main system
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = await self.client.post(
                    f"{self.main_system_url}/api/access/logs/batch/",
                    json={"access_logs": log_data},
                    headers=headers
                )
                
                if response.status_code == 200:
                    # Mark logs as synced
                    log_ids = [log.id for log in logs]
                    await db.execute(
                        update(AccessAttempt)
                        .where(AccessAttempt.id.in_(log_ids))
                        .values(synced_to_main=True)
                    )
                    await db.commit()
                    
                    logger.info(f"Pushed {len(logs)} access logs to main system")
                    return True
                else:
                    logger.error(f"Failed to push logs: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Log push failed: {e}")
            return False

# Background sync service
async def start_sync_service():
    """Start background synchronization service"""
    sync_service = SyncService()
    
    while True:
        try:
            # Sync cards from main system
            await sync_service.sync_cards_from_main()
            
            # Push access logs to main system
            await sync_service.push_access_logs_to_main()
            
        except Exception as e:
            logger.error(f"Sync service error: {e}")
        
        # Wait for next sync interval
        await asyncio.sleep(settings.SYNC_INTERVAL)
```

## Phase 4: Deployment (Week 7-8)

### Step 12: Docker Configuration

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  access-control:
    build: .
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/access_control.db
      - REDIS_URL=redis://redis:6379/0
      - MAIN_SYSTEM_URL=http://main-system:8000
    volumes:
      - ./data:/app/data
      - /dev/ttyUSB0:/dev/ttyUSB0  # RFID reader
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
    privileged: true  # For GPIO access
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - access-control
    restart: unless-stopped

volumes:
  redis_data:
```

### Step 13: Environment Configuration

Create `.env` file:
```env
# Service settings
SERVICE_NAME=access-control
DEBUG=false

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/access_control.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Main system integration
MAIN_SYSTEM_URL=http://localhost:8000
MAIN_SYSTEM_API_KEY=your-api-key-here

# Hardware settings
RFID_READER_PORT=/dev/ttyUSB0
RFID_READER_BAUD=9600

# Security
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
OFFLINE_GRACE_PERIOD=86400

# Sync settings
SYNC_INTERVAL=300
```

### Step 14: Deployment Script

Create `deploy.sh`:
```bash
#!/bin/bash

echo "Deploying Access Control Microservice..."

# Stop existing containers
docker-compose down

# Build and start services
docker-compose up -d --build

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check health
curl -f http://localhost:8001/health

if [ $? -eq 0 ]; then
    echo "✅ Access Control Service deployed successfully!"
else
    echo "❌ Deployment failed - check logs"
    docker-compose logs
    exit 1
fi

echo "🚀 Service is running at http://localhost:8001"
echo "📊 Redis is available at localhost:6379"
echo "📝 Check logs with: docker-compose logs -f"
```

## Testing and Monitoring

### Step 15: Basic Tests

Create `tests/test_access_control.py`:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_validate_card_endpoint():
    response = client.post("/api/access/validate-card/", json={
        "rfid_number": "TEST123456",
        "gate_id": "GATE_001"
    })
    assert response.status_code == 200
    # Note: Will likely return access denied for test card
    assert "access_granted" in response.json()

@pytest.mark.asyncio
async def test_access_service():
    from app.services.access_service import AccessControlService
    service = AccessControlService()
    # Add your specific tests here
```

### Step 16: Monitoring Setup

Create `monitoring/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'access-control'
    static_configs:
      - targets: ['access-control:8001']
```

## Quick Deployment Checklist

1. **Hardware Setup**:
   - [ ] RFID reader connected to `/dev/ttyUSB0`
   - [ ] GPIO pins configured for gate control
   - [ ] Network connectivity to main system

2. **Configuration**:
   - [ ] `.env` file created with correct settings
   - [ ] Hardware ports and pins configured
   - [ ] Main system URL and API key set

3. **Deploy**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **Test**:
   ```bash
   # Test health
   curl http://localhost:8001/health
   
   # Test card validation
   curl -X POST http://localhost:8001/api/access/validate-card/ \
     -H "Content-Type: application/json" \
     -d '{"rfid_number": "TEST123", "gate_id": "GATE_001"}'
   ```

5. **Monitor**:
   ```bash
   # Check logs
   docker-compose logs -f
   
   # Check Redis
   docker-compose exec redis redis-cli ping
   ```

This implementation provides a solid foundation for your access control microservice that can be extended based on your specific hardware and requirements.