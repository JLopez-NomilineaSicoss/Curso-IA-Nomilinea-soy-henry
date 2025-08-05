"""
Microservicio de Inventario
Maneja habitaciones, hoteles, disponibilidad y precios
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Float, Integer, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, date
from typing import Optional, List
import sys
import os
import httpx

# Agregar el directorio padre al path para importar shared
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config import InventoryServiceSettings
from shared.models import (
    HotelBase, Hotel, RoomBase, Room, RoomSearchCriteria, RoomSearchResult,
    RoomAvailability, APIResponse, RoomType
)
from shared.utils import (
    setup_logging, create_response, create_error_response,
    generate_uuid, ValidationError, NotFoundError
)

# Configuración
settings = InventoryServiceSettings()
logger = setup_logging("inventory-service", settings.log_level)

# Configuración de base de datos
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos de base de datos
class HotelDB(Base):
    __tablename__ = "hotels"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    amenities = Column(Text, nullable=True)  # JSON string
    images = Column(Text, nullable=True)    # JSON string
    is_active = Column(Boolean, default=True)
    total_rooms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class RoomDB(Base):
    __tablename__ = "rooms"
    
    id = Column(String, primary_key=True, index=True)
    hotel_id = Column(String, nullable=False, index=True)
    room_number = Column(String, nullable=False)
    room_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    capacity = Column(Integer, nullable=False)
    price_per_night = Column(Float, nullable=False)
    amenities = Column(Text, nullable=True)  # JSON string
    images = Column(Text, nullable=True)    # JSON string
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class RoomAvailabilityDB(Base):
    __tablename__ = "room_availability"
    
    id = Column(String, primary_key=True, index=True)
    room_id = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False)
    is_available = Column(Boolean, default=True)
    price_override = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Configuración de FastAPI
app = FastAPI(
    title="Hotel Reservation - Inventory Service",
    description="Microservicio de gestión de inventario de habitaciones",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Dependencias
def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token con el servicio de autenticación"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.auth_service_url}/verify-token",
                headers={"Authorization": f"Bearer {credentials.credentials}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            return response.json()["data"]
    
    except Exception as e:
        logger.error(f"Error verificando token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación"
        )

# ==================== UTILITY FUNCTIONS ====================

def serialize_json_field(field_value: str) -> list:
    """Convertir campo JSON string a lista"""
    import json
    try:
        return json.loads(field_value) if field_value else []
    except:
        return []

def deserialize_json_field(field_value: list) -> str:
    """Convertir lista a JSON string"""
    import json
    try:
        return json.dumps(field_value) if field_value else "[]"
    except:
        return "[]"

# ==================== ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """Health check del servicio"""
    try:
        # Verificar conexión a base de datos
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return create_response(
            data={
                "service": "inventory-service",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "connected"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return create_error_response("Service unhealthy", [str(e)])

# ==================== HOTEL ENDPOINTS ====================

@app.post("/hotels", response_model=APIResponse)
async def create_hotel(
    hotel_data: HotelBase,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Crear nuevo hotel"""
    try:
        logger.info(f"Creando hotel: {hotel_data.name}")
        
        # Verificar permisos
        if current_user.get("role") not in ["admin", "hotel_manager"]:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        
        # Crear hotel
        hotel_db = HotelDB(
            id=generate_uuid(),
            name=hotel_data.name,
            description=hotel_data.description,
            address=hotel_data.address,
            city=hotel_data.city,
            country=hotel_data.country,
            phone=hotel_data.phone,
            email=hotel_data.email,
            rating=hotel_data.rating,
            amenities=deserialize_json_field(hotel_data.amenities),
            images=deserialize_json_field(hotel_data.images)
        )
        
        db.add(hotel_db)
        db.commit()
        db.refresh(hotel_db)
        
        logger.info(f"Hotel creado exitosamente: {hotel_data.name}")
        
        return create_response(
            data={
                "hotel_id": hotel_db.id,
                "name": hotel_db.name,
                "city": hotel_db.city,
                "country": hotel_db.country
            },
            message="Hotel creado exitosamente"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando hotel: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/hotels", response_model=APIResponse)
async def list_hotels(
    city: Optional[str] = None,
    country: Optional[str] = None,
    rating_min: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Listar hoteles con filtros opcionales"""
    try:
        query = db.query(HotelDB).filter(HotelDB.is_active == True)
        
        if city:
            query = query.filter(HotelDB.city.ilike(f"%{city}%"))
        
        if country:
            query = query.filter(HotelDB.country.ilike(f"%{country}%"))
        
        if rating_min:
            query = query.filter(HotelDB.rating >= rating_min)
        
        hotels = query.all()
        
        hotels_data = [
            {
                "id": hotel.id,
                "name": hotel.name,
                "description": hotel.description,
                "address": hotel.address,
                "city": hotel.city,
                "country": hotel.country,
                "rating": hotel.rating,
                "total_rooms": hotel.total_rooms,
                "amenities": serialize_json_field(hotel.amenities),
                "images": serialize_json_field(hotel.images)
            }
            for hotel in hotels
        ]
        
        return create_response(
            data=hotels_data,
            message=f"Se encontraron {len(hotels_data)} hoteles"
        )
    
    except Exception as e:
        logger.error(f"Error listando hoteles: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/hotels/{hotel_id}", response_model=APIResponse)
async def get_hotel(hotel_id: str, db: Session = Depends(get_db)):
    """Obtener hotel por ID"""
    try:
        hotel = db.query(HotelDB).filter(HotelDB.id == hotel_id, HotelDB.is_active == True).first()
        
        if not hotel:
            raise NotFoundError("Hotel no encontrado")
        
        return create_response(
            data={
                "id": hotel.id,
                "name": hotel.name,
                "description": hotel.description,
                "address": hotel.address,
                "city": hotel.city,
                "country": hotel.country,
                "phone": hotel.phone,
                "email": hotel.email,
                "rating": hotel.rating,
                "total_rooms": hotel.total_rooms,
                "amenities": serialize_json_field(hotel.amenities),
                "images": serialize_json_field(hotel.images),
                "created_at": hotel.created_at.isoformat()
            }
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error obteniendo hotel: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# ==================== ROOM ENDPOINTS ====================

@app.post("/rooms", response_model=APIResponse)
async def create_room(
    room_data: RoomBase,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Crear nueva habitación"""
    try:
        logger.info(f"Creando habitación: {room_data.room_number}")
        
        # Verificar permisos
        if current_user.get("role") not in ["admin", "hotel_manager"]:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        
        # Verificar que el hotel existe
        hotel = db.query(HotelDB).filter(HotelDB.id == room_data.hotel_id).first()
        if not hotel:
            raise NotFoundError("Hotel no encontrado")
        
        # Verificar que no existe otra habitación con el mismo número en el hotel
        existing_room = db.query(RoomDB).filter(
            RoomDB.hotel_id == room_data.hotel_id,
            RoomDB.room_number == room_data.room_number
        ).first()
        
        if existing_room:
            raise ValidationError("Ya existe una habitación con ese número en el hotel")
        
        # Crear habitación
        room_db = RoomDB(
            id=generate_uuid(),
            hotel_id=room_data.hotel_id,
            room_number=room_data.room_number,
            room_type=room_data.room_type,
            description=room_data.description,
            capacity=room_data.capacity,
            price_per_night=room_data.price_per_night,
            amenities=deserialize_json_field(room_data.amenities),
            images=deserialize_json_field(room_data.images),
            is_available=room_data.is_available
        )
        
        db.add(room_db)
        
        # Actualizar contador de habitaciones del hotel
        hotel.total_rooms += 1
        
        db.commit()
        db.refresh(room_db)
        
        logger.info(f"Habitación creada exitosamente: {room_data.room_number}")
        
        return create_response(
            data={
                "room_id": room_db.id,
                "hotel_id": room_db.hotel_id,
                "room_number": room_db.room_number,
                "room_type": room_db.room_type,
                "price_per_night": room_db.price_per_night
            },
            message="Habitación creada exitosamente"
        )
    
    except (ValidationError, NotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando habitación: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/rooms/search", response_model=APIResponse)
async def search_rooms(
    city: Optional[str] = None,
    check_in_date: Optional[date] = Query(None),
    check_out_date: Optional[date] = Query(None),
    guests: Optional[int] = Query(1, ge=1, le=10),
    room_type: Optional[RoomType] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db)
):
    """Buscar habitaciones disponibles"""
    try:
        logger.info(f"Búsqueda de habitaciones - Ciudad: {city}, Check-in: {check_in_date}, Check-out: {check_out_date}")
        
        # Query base
        query = db.query(RoomDB, HotelDB).join(HotelDB, RoomDB.hotel_id == HotelDB.id).filter(
            RoomDB.is_available == True,
            HotelDB.is_active == True,
            RoomDB.capacity >= guests
        )
        
        # Filtros
        if city:
            query = query.filter(HotelDB.city.ilike(f"%{city}%"))
        
        if room_type:
            query = query.filter(RoomDB.room_type == room_type)
        
        if min_price:
            query = query.filter(RoomDB.price_per_night >= min_price)
        
        if max_price:
            query = query.filter(RoomDB.price_per_night <= max_price)
        
        results = query.all()
        
        # Verificar disponibilidad por fechas si se especifican
        available_rooms = []
        for room, hotel in results:
            is_available = True
            
            if check_in_date and check_out_date:
                # Verificar disponibilidad en el rango de fechas
                current_date = check_in_date
                while current_date < check_out_date:
                    availability = db.query(RoomAvailabilityDB).filter(
                        RoomAvailabilityDB.room_id == room.id,
                        RoomAvailabilityDB.date == current_date,
                        RoomAvailabilityDB.is_available == False
                    ).first()
                    
                    if availability:
                        is_available = False
                        break
                    
                    current_date = current_date + timedelta(days=1)
            
            if is_available:
                nights = (check_out_date - check_in_date).days if check_in_date and check_out_date else 1
                total_price = room.price_per_night * nights
                
                available_rooms.append({
                    "room": {
                        "id": room.id,
                        "room_number": room.room_number,
                        "room_type": room.room_type,
                        "description": room.description,
                        "capacity": room.capacity,
                        "price_per_night": room.price_per_night,
                        "amenities": serialize_json_field(room.amenities),
                        "images": serialize_json_field(room.images)
                    },
                    "hotel": {
                        "id": hotel.id,
                        "name": hotel.name,
                        "description": hotel.description,
                        "address": hotel.address,
                        "city": hotel.city,
                        "country": hotel.country,
                        "rating": hotel.rating,
                        "amenities": serialize_json_field(hotel.amenities)
                    },
                    "total_price": total_price,
                    "nights": nights
                })
        
        return create_response(
            data=available_rooms,
            message=f"Se encontraron {len(available_rooms)} habitaciones disponibles"
        )
    
    except Exception as e:
        logger.error(f"Error en búsqueda de habitaciones: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/rooms/{room_id}", response_model=APIResponse)
async def get_room(room_id: str, db: Session = Depends(get_db)):
    """Obtener habitación por ID"""
    try:
        room = db.query(RoomDB).filter(RoomDB.id == room_id).first()
        
        if not room:
            raise NotFoundError("Habitación no encontrada")
        
        # Obtener información del hotel
        hotel = db.query(HotelDB).filter(HotelDB.id == room.hotel_id).first()
        
        return create_response(
            data={
                "id": room.id,
                "hotel_id": room.hotel_id,
                "hotel_name": hotel.name if hotel else None,
                "room_number": room.room_number,
                "room_type": room.room_type,
                "description": room.description,
                "capacity": room.capacity,
                "price_per_night": room.price_per_night,
                "amenities": serialize_json_field(room.amenities),
                "images": serialize_json_field(room.images),
                "is_available": room.is_available,
                "created_at": room.created_at.isoformat()
            }
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error obteniendo habitación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/rooms/{room_id}/availability", response_model=APIResponse)
async def set_room_availability(
    room_id: str,
    availability_date: date,
    is_available: bool = True,
    price_override: Optional[float] = None,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Establecer disponibilidad de habitación para una fecha específica"""
    try:
        # Verificar permisos
        if current_user.get("role") not in ["admin", "hotel_manager"]:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        
        # Verificar que la habitación existe
        room = db.query(RoomDB).filter(RoomDB.id == room_id).first()
        if not room:
            raise NotFoundError("Habitación no encontrada")
        
        # Buscar o crear registro de disponibilidad
        availability = db.query(RoomAvailabilityDB).filter(
            RoomAvailabilityDB.room_id == room_id,
            RoomAvailabilityDB.date == availability_date
        ).first()
        
        if availability:
            availability.is_available = is_available
            availability.price_override = price_override
        else:
            availability = RoomAvailabilityDB(
                id=generate_uuid(),
                room_id=room_id,
                date=availability_date,
                is_available=is_available,
                price_override=price_override
            )
            db.add(availability)
        
        db.commit()
        
        return create_response(
            data={
                "room_id": room_id,
                "date": availability_date.isoformat(),
                "is_available": is_available,
                "price_override": price_override
            },
            message="Disponibilidad actualizada exitosamente"
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error estableciendo disponibilidad: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    from datetime import timedelta
    import uvicorn
    logger.info(f"Iniciando Inventory Service en puerto {settings.port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )
