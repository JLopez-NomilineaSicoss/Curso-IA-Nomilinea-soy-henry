"""
Microservicio de Reservas
Maneja la creación, modificación y cancelación de reservas
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Float, Integer, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, date, timedelta
from typing import Optional, List
import sys
import os
import httpx
import uuid

# Agregar el directorio padre al path para importar shared
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config import BookingServiceSettings
from shared.models import (
    ReservationCreate, ReservationUpdate, Reservation, ReservationStatus,
    APIResponse
)
from shared.utils import (
    setup_logging, create_response, create_error_response,
    generate_uuid, generate_confirmation_code, ValidationError, NotFoundError
)

# Configuración
settings = BookingServiceSettings()
logger = setup_logging("booking-service", settings.log_level)

# Configuración de base de datos
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de base de datos
class ReservationDB(Base):
    __tablename__ = "reservations"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    hotel_id = Column(String, nullable=False, index=True)
    room_id = Column(String, nullable=False, index=True)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    guests = Column(Integer, nullable=False)
    special_requests = Column(Text, nullable=True)
    status = Column(String, default="pending")
    total_amount = Column(Float, nullable=False)
    confirmation_code = Column(String, unique=True, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Configuración de FastAPI
app = FastAPI(
    title="Hotel Reservation - Booking Service",
    description="Microservicio de gestión de reservas",
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

async def check_room_availability(room_id: str, check_in: date, check_out: date):
    """Verificar disponibilidad de habitación con el servicio de inventario"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.inventory_service_url}/rooms/{room_id}"
            )
            
            if response.status_code != 200:
                return False, "Habitación no encontrada"
            
            room_data = response.json()["data"]
            
            # Verificar disponibilidad básica
            if not room_data.get("is_available", False):
                return False, "Habitación no disponible"
            
            # Aquí se podría agregar lógica adicional para verificar disponibilidad por fechas
            return True, room_data
    
    except Exception as e:
        logger.error(f"Error verificando disponibilidad: {e}")
        return False, "Error verificando disponibilidad"

async def calculate_total_amount(room_id: str, check_in: date, check_out: date, guests: int):
    """Calcular monto total de la reserva"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.inventory_service_url}/rooms/{room_id}"
            )
            
            if response.status_code != 200:
                raise ValueError("No se pudo obtener información de la habitación")
            
            room_data = response.json()["data"]
            price_per_night = room_data["price_per_night"]
            
            nights = (check_out - check_in).days
            subtotal = price_per_night * nights
            taxes = subtotal * 0.16  # 16% de impuestos
            total = subtotal + taxes
            
            return {
                "subtotal": round(subtotal, 2),
                "taxes": round(taxes, 2),
                "total": round(total, 2),
                "nights": nights,
                "price_per_night": price_per_night
            }
    
    except Exception as e:
        logger.error(f"Error calculando monto total: {e}")
        raise ValueError("Error calculando monto total")

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
                "service": "booking-service",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "connected"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return create_error_response("Service unhealthy", [str(e)])

@app.post("/reservations", response_model=APIResponse)
async def create_reservation(
    reservation_data: ReservationCreate,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Crear nueva reserva"""
    try:
        logger.info(f"Creando reserva para usuario {current_user.get('user_id')}")
        
        # Validar fechas
        if reservation_data.check_in_date <= date.today():
            raise ValidationError("La fecha de check-in debe ser futura")
        
        if reservation_data.check_out_date <= reservation_data.check_in_date:
            raise ValidationError("La fecha de check-out debe ser posterior al check-in")
        
        # Verificar disponibilidad de la habitación
        is_available, room_info = await check_room_availability(
            reservation_data.room_id,
            reservation_data.check_in_date,
            reservation_data.check_out_date
        )
        
        if not is_available:
            raise ValidationError(f"Habitación no disponible: {room_info}")
        
        # Calcular monto total
        pricing = await calculate_total_amount(
            reservation_data.room_id,
            reservation_data.check_in_date,
            reservation_data.check_out_date,
            reservation_data.guests
        )
        
        # Crear reserva
        reservation_db = ReservationDB(
            id=generate_uuid(),
            user_id=current_user.get("user_id"),
            hotel_id=reservation_data.hotel_id,
            room_id=reservation_data.room_id,
            check_in_date=reservation_data.check_in_date,
            check_out_date=reservation_data.check_out_date,
            guests=reservation_data.guests,
            special_requests=reservation_data.special_requests,
            status=ReservationStatus.PENDING,
            total_amount=pricing["total"],
            confirmation_code=generate_confirmation_code()
        )
        
        db.add(reservation_db)
        db.commit()
        db.refresh(reservation_db)
        
        logger.info(f"Reserva creada exitosamente: {reservation_db.confirmation_code}")
        
        return create_response(
            data={
                "reservation_id": reservation_db.id,
                "confirmation_code": reservation_db.confirmation_code,
                "status": reservation_db.status,
                "total_amount": reservation_db.total_amount,
                "pricing_details": pricing,
                "check_in_date": reservation_db.check_in_date.isoformat(),
                "check_out_date": reservation_db.check_out_date.isoformat()
            },
            message="Reserva creada exitosamente"
        )
    
    except ValidationError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creando reserva: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Iniciando Booking Service en puerto {settings.port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )
