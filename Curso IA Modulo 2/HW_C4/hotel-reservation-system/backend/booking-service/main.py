"""
Microservicio de Reservas
Maneja la creación, modificación, cancelación y gestión de reservas
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
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
import asyncio

# Agregar el directorio padre al path para importar shared
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config import BookingServiceSettings
from shared.models import (
    ReservationBase, ReservationCreate, ReservationUpdate, Reservation,
    ReservationStatus, APIResponse, NotificationCreate, NotificationType
)
from shared.utils import (
    setup_logging, create_response, create_error_response,
    generate_uuid, generate_confirmation_code, ValidationError, 
    NotFoundError, calculate_nights, calculate_total_price
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
    status = Column(String, default=ReservationStatus.PENDING)
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

# Funciones auxiliares
async def get_room_info(room_id: str):
    """Obtener información de la habitación del servicio de inventario"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.inventory_service_url}/rooms/{room_id}")
            
            if response.status_code == 200:
                return response.json()["data"]
            else:
                return None
    except Exception as e:
        logger.error(f"Error obteniendo información de habitación: {e}")
        return None

async def check_room_availability(room_id: str, check_in: date, check_out: date):
    """Verificar disponibilidad de habitación en el servicio de inventario"""
    try:
        async with httpx.AsyncClient() as client:
            params = {
                "check_in_date": check_in.isoformat(),
                "check_out_date": check_out.isoformat()
            }
            response = await client.get(
                f"{settings.inventory_service_url}/rooms/search",
                params=params
            )
            
            if response.status_code == 200:
                rooms_data = response.json()["data"]
                # Verificar si la habitación específica está en los resultados
                for room_result in rooms_data:
                    if room_result["room"]["id"] == room_id:
                        return True
                return False
            else:
                return False
    except Exception as e:
        logger.error(f"Error verificando disponibilidad: {e}")
        return False

async def block_room_availability(room_id: str, check_in: date, check_out: date):
    """Bloquear disponibilidad de habitación en el servicio de inventario"""
    try:
        current_date = check_in
        async with httpx.AsyncClient() as client:
            while current_date < check_out:
                response = await client.post(
                    f"{settings.inventory_service_url}/rooms/{room_id}/availability",
                    json={
                        "availability_date": current_date.isoformat(),
                        "is_available": False
                    },
                    headers={"Authorization": f"Bearer {settings.secret_key}"}  # Token de servicio
                )
                current_date += timedelta(days=1)
        return True
    except Exception as e:
        logger.error(f"Error bloqueando disponibilidad: {e}")
        return False

async def send_notification(notification_data: dict):
    """Enviar notificación al servicio de notificaciones"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.notification_service_url}/notifications",
                json=notification_data
            )
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")
        return False

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
    background_tasks: BackgroundTasks,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Crear nueva reserva"""
    try:
        logger.info(f"Creando reserva para usuario: {current_user['user_id']}")
        
        # Verificar que las fechas sean válidas
        if reservation_data.check_in_date <= date.today():
            raise ValidationError("La fecha de check-in debe ser futura")
        
        if reservation_data.check_out_date <= reservation_data.check_in_date:
            raise ValidationError("La fecha de check-out debe ser posterior al check-in")
        
        # Obtener información de la habitación
        room_info = await get_room_info(reservation_data.room_id)
        if not room_info:
            raise NotFoundError("Habitación no encontrada")
        
        # Verificar capacidad
        if reservation_data.guests > room_info["capacity"]:
            raise ValidationError(f"La habitación solo tiene capacidad para {room_info['capacity']} huéspedes")
        
        # Verificar disponibilidad
        is_available = await check_room_availability(
            reservation_data.room_id,
            reservation_data.check_in_date,
            reservation_data.check_out_date
        )
        
        if not is_available:
            raise ValidationError("La habitación no está disponible en las fechas seleccionadas")
        
        # Calcular precio total
        nights = calculate_nights(
            datetime.combine(reservation_data.check_in_date, datetime.min.time()),
            datetime.combine(reservation_data.check_out_date, datetime.min.time())
        )
        
        pricing = calculate_total_price(
            room_info["price_per_night"],
            nights,
            reservation_data.guests
        )
        
        # Crear reserva
        confirmation_code = generate_confirmation_code()
        reservation_db = ReservationDB(
            id=generate_uuid(),
            user_id=current_user["user_id"],
            hotel_id=reservation_data.hotel_id,
            room_id=reservation_data.room_id,
            check_in_date=reservation_data.check_in_date,
            check_out_date=reservation_data.check_out_date,
            guests=reservation_data.guests,
            special_requests=reservation_data.special_requests,
            status=ReservationStatus.PENDING,
            total_amount=pricing["total"],
            confirmation_code=confirmation_code
        )
        
        db.add(reservation_db)
        db.commit()
        db.refresh(reservation_db)
        
        # Bloquear disponibilidad de la habitación
        await block_room_availability(
            reservation_data.room_id,
            reservation_data.check_in_date,
            reservation_data.check_out_date
        )
        
        # Enviar notificación de confirmación
        notification_data = {
            "user_id": current_user["user_id"],
            "type": NotificationType.EMAIL,
            "subject": f"Confirmación de Reserva - {confirmation_code}",
            "message": f"Su reserva ha sido creada exitosamente. Código de confirmación: {confirmation_code}",
            "data": {
                "reservation_id": reservation_db.id,
                "confirmation_code": confirmation_code,
                "hotel_name": room_info.get("hotel_name", ""),
                "room_number": room_info["room_number"],
                "check_in": reservation_data.check_in_date.isoformat(),
                "check_out": reservation_data.check_out_date.isoformat(),
                "total_amount": pricing["total"]
            }
        }
        
        background_tasks.add_task(send_notification, notification_data)
        
        logger.info(f"Reserva creada exitosamente: {confirmation_code}")
        
        return create_response(
            data={
                "reservation_id": reservation_db.id,
                "confirmation_code": confirmation_code,
                "status": reservation_db.status,
                "total_amount": reservation_db.total_amount,
                "pricing_breakdown": pricing,
                "room_info": {
                    "room_number": room_info["room_number"],
                    "room_type": room_info["room_type"],
                    "hotel_name": room_info.get("hotel_name", "")
                }
            },
            message="Reserva creada exitosamente"
        )
    
    except (ValidationError, NotFoundError) as e:
        logger.warning(f"Error de validación en reserva: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error creando reserva: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/reservations", response_model=APIResponse)
async def list_user_reservations(
    status_filter: Optional[ReservationStatus] = None,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Listar reservas del usuario actual"""
    try:
        query = db.query(ReservationDB).filter(ReservationDB.user_id == current_user["user_id"])
        
        if status_filter:
            query = query.filter(ReservationDB.status == status_filter)
        
        reservations = query.order_by(ReservationDB.created_at.desc()).all()
        
        # Enriquecer con información de habitaciones
        reservations_data = []
        for reservation in reservations:
            room_info = await get_room_info(reservation.room_id)
            
            reservation_data = {
                "id": reservation.id,
                "hotel_id": reservation.hotel_id,
                "room_id": reservation.room_id,
                "check_in_date": reservation.check_in_date.isoformat(),
                "check_out_date": reservation.check_out_date.isoformat(),
                "guests": reservation.guests,
                "special_requests": reservation.special_requests,
                "status": reservation.status,
                "total_amount": reservation.total_amount,
                "confirmation_code": reservation.confirmation_code,
                "created_at": reservation.created_at.isoformat(),
                "room_info": room_info if room_info else {},
                "nights": (reservation.check_out_date - reservation.check_in_date).days
            }
            
            if reservation.cancelled_at:
                reservation_data["cancelled_at"] = reservation.cancelled_at.isoformat()
                reservation_data["cancellation_reason"] = reservation.cancellation_reason
            
            reservations_data.append(reservation_data)
        
        return create_response(
            data=reservations_data,
            message=f"Se encontraron {len(reservations_data)} reservas"
        )
    
    except Exception as e:
        logger.error(f"Error listando reservas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/reservations/{reservation_id}", response_model=APIResponse)
async def get_reservation(
    reservation_id: str,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Obtener detalles de una reserva específica"""
    try:
        reservation = db.query(ReservationDB).filter(
            ReservationDB.id == reservation_id,
            ReservationDB.user_id == current_user["user_id"]
        ).first()
        
        if not reservation:
            raise NotFoundError("Reserva no encontrada")
        
        # Obtener información adicional
        room_info = await get_room_info(reservation.room_id)
        
        reservation_data = {
            "id": reservation.id,
            "hotel_id": reservation.hotel_id,
            "room_id": reservation.room_id,
            "check_in_date": reservation.check_in_date.isoformat(),
            "check_out_date": reservation.check_out_date.isoformat(),
            "guests": reservation.guests,
            "special_requests": reservation.special_requests,
            "status": reservation.status,
            "total_amount": reservation.total_amount,
            "confirmation_code": reservation.confirmation_code,
            "created_at": reservation.created_at.isoformat(),
            "updated_at": reservation.updated_at.isoformat(),
            "room_info": room_info if room_info else {},
            "nights": (reservation.check_out_date - reservation.check_in_date).days
        }
        
        if reservation.cancelled_at:
            reservation_data["cancelled_at"] = reservation.cancelled_at.isoformat()
            reservation_data["cancellation_reason"] = reservation.cancellation_reason
        
        return create_response(data=reservation_data)
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error obteniendo reserva: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.put("/reservations/{reservation_id}", response_model=APIResponse)
async def update_reservation(
    reservation_id: str,
    update_data: ReservationUpdate,
    background_tasks: BackgroundTasks,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Actualizar una reserva existente"""
    try:
        reservation = db.query(ReservationDB).filter(
            ReservationDB.id == reservation_id,
            ReservationDB.user_id == current_user["user_id"]
        ).first()
        
        if not reservation:
            raise NotFoundError("Reserva no encontrada")
        
        if reservation.status in [ReservationStatus.CANCELLED, ReservationStatus.CHECKED_OUT]:
            raise ValidationError("No se puede modificar una reserva cancelada o finalizada")
        
        # Verificar si es una modificación de fechas
        dates_changed = False
        if (update_data.check_in_date and update_data.check_in_date != reservation.check_in_date) or \
           (update_data.check_out_date and update_data.check_out_date != reservation.check_out_date):
            dates_changed = True
        
        # Si cambian las fechas, verificar disponibilidad
        if dates_changed:
            new_check_in = update_data.check_in_date or reservation.check_in_date
            new_check_out = update_data.check_out_date or reservation.check_out_date
            
            if new_check_in <= date.today():
                raise ValidationError("La fecha de check-in debe ser futura")
            
            if new_check_out <= new_check_in:
                raise ValidationError("La fecha de check-out debe ser posterior al check-in")
            
            # Verificar disponibilidad para las nuevas fechas
            is_available = await check_room_availability(
                reservation.room_id,
                new_check_in,
                new_check_out
            )
            
            if not is_available:
                raise ValidationError("La habitación no está disponible en las nuevas fechas")
        
        # Actualizar campos
        if update_data.check_in_date:
            reservation.check_in_date = update_data.check_in_date
        if update_data.check_out_date:
            reservation.check_out_date = update_data.check_out_date
        if update_data.guests:
            reservation.guests = update_data.guests
        if update_data.special_requests is not None:
            reservation.special_requests = update_data.special_requests
        if update_data.status:
            reservation.status = update_data.status
        
        reservation.updated_at = datetime.utcnow()
        
        # Recalcular precio si cambiaron las fechas
        if dates_changed:
            room_info = await get_room_info(reservation.room_id)
            if room_info:
                nights = calculate_nights(
                    datetime.combine(reservation.check_in_date, datetime.min.time()),
                    datetime.combine(reservation.check_out_date, datetime.min.time())
                )
                pricing = calculate_total_price(room_info["price_per_night"], nights, reservation.guests)
                reservation.total_amount = pricing["total"]
        
        db.commit()
        db.refresh(reservation)
        
        # Enviar notificación de modificación
        notification_data = {
            "user_id": current_user["user_id"],
            "type": NotificationType.EMAIL,
            "subject": f"Reserva Modificada - {reservation.confirmation_code}",
            "message": "Su reserva ha sido modificada exitosamente.",
            "data": {
                "reservation_id": reservation.id,
                "confirmation_code": reservation.confirmation_code,
                "changes": "Fechas actualizadas" if dates_changed else "Detalles actualizados"
            }
        }
        
        background_tasks.add_task(send_notification, notification_data)
        
        logger.info(f"Reserva modificada: {reservation.confirmation_code}")
        
        return create_response(
            data={
                "reservation_id": reservation.id,
                "confirmation_code": reservation.confirmation_code,
                "status": reservation.status,
                "total_amount": reservation.total_amount,
                "updated_at": reservation.updated_at.isoformat()
            },
            message="Reserva actualizada exitosamente"
        )
    
    except (ValidationError, NotFoundError) as e:
        logger.warning(f"Error actualizando reserva: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error actualizando reserva: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/reservations/{reservation_id}/cancel", response_model=APIResponse)
async def cancel_reservation(
    reservation_id: str,
    cancellation_reason: Optional[str] = None,
    background_tasks: BackgroundTasks,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Cancelar una reserva"""
    try:
        reservation = db.query(ReservationDB).filter(
            ReservationDB.id == reservation_id,
            ReservationDB.user_id == current_user["user_id"]
        ).first()
        
        if not reservation:
            raise NotFoundError("Reserva no encontrada")
        
        if reservation.status in [ReservationStatus.CANCELLED, ReservationStatus.CHECKED_OUT]:
            raise ValidationError("La reserva ya está cancelada o finalizada")
        
        # Actualizar estado de la reserva
        reservation.status = ReservationStatus.CANCELLED
        reservation.cancelled_at = datetime.utcnow()
        reservation.cancellation_reason = cancellation_reason
        reservation.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Liberar disponibilidad de la habitación
        # (Aquí se podría implementar la lógica para liberar las fechas bloqueadas)
        
        # Enviar notificación de cancelación
        notification_data = {
            "user_id": current_user["user_id"],
            "type": NotificationType.EMAIL,
            "subject": f"Reserva Cancelada - {reservation.confirmation_code}",
            "message": "Su reserva ha sido cancelada exitosamente.",
            "data": {
                "reservation_id": reservation.id,
                "confirmation_code": reservation.confirmation_code,
                "cancellation_reason": cancellation_reason
            }
        }
        
        background_tasks.add_task(send_notification, notification_data)
        
        logger.info(f"Reserva cancelada: {reservation.confirmation_code}")
        
        return create_response(
            data={
                "reservation_id": reservation.id,
                "confirmation_code": reservation.confirmation_code,
                "status": reservation.status,
                "cancelled_at": reservation.cancelled_at.isoformat()
            },
            message="Reserva cancelada exitosamente"
        )
    
    except (ValidationError, NotFoundError) as e:
        logger.warning(f"Error cancelando reserva: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error cancelando reserva: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/reservations/{reservation_id}/confirmation", response_model=APIResponse)
async def get_reservation_confirmation(
    reservation_id: str,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Obtener detalles de confirmación de reserva para imprimir"""
    try:
        reservation = db.query(ReservationDB).filter(
            ReservationDB.id == reservation_id,
            ReservationDB.user_id == current_user["user_id"]
        ).first()
        
        if not reservation:
            raise NotFoundError("Reserva no encontrada")
        
        # Obtener información completa
        room_info = await get_room_info(reservation.room_id)
        
        confirmation_data = {
            "confirmation_code": reservation.confirmation_code,
            "status": reservation.status,
            "guest_info": {
                "name": f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}",
                "email": current_user.get('email', ''),
                "guests": reservation.guests
            },
            "reservation_details": {
                "check_in_date": reservation.check_in_date.isoformat(),
                "check_out_date": reservation.check_out_date.isoformat(),
                "nights": (reservation.check_out_date - reservation.check_in_date).days,
                "special_requests": reservation.special_requests
            },
            "accommodation": {
                "hotel_name": room_info.get("hotel_name", "") if room_info else "",
                "room_number": room_info.get("room_number", "") if room_info else "",
                "room_type": room_info.get("room_type", "") if room_info else "",
                "room_amenities": room_info.get("amenities", []) if room_info else []
            },
            "pricing": {
                "total_amount": reservation.total_amount,
                "currency": "USD"
            },
            "created_at": reservation.created_at.isoformat()
        }
        
        return create_response(data=confirmation_data)
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error obteniendo confirmación: {e}")
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
