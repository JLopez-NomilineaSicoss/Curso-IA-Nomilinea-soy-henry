"""
Microservicio de Pagos
Maneja el procesamiento de pagos con Stripe y PayPal
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, Dict, Any
import sys
import os
import httpx
import json

# Agregar el directorio padre al path para importar shared
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config import PaymentServiceSettings
from shared.models import (
    PaymentCreate, Payment, PaymentStatus, PaymentMethod, APIResponse
)
from shared.utils import (
    setup_logging, create_response, create_error_response,
    generate_uuid, ValidationError, NotFoundError, PaymentError
)

# Configuración
settings = PaymentServiceSettings()
logger = setup_logging("payment-service", settings.log_level)

# Configuración de base de datos
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de base de datos
class PaymentDB(Base):
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True, index=True)
    reservation_id = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    payment_method = Column(String, nullable=False)
    status = Column(String, default="pending")
    transaction_id = Column(String, nullable=True)
    gateway_reference = Column(String, nullable=True)
    payment_data = Column(Text, nullable=True)  # JSON string
    processed_at = Column(DateTime, nullable=True)
    refunded_amount = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Configuración de FastAPI
app = FastAPI(
    title="Hotel Reservation - Payment Service",
    description="Microservicio de procesamiento de pagos",
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

# ==================== PAYMENT PROCESSORS ====================

class StripeProcessor:
    """Procesador de pagos con Stripe"""
    
    def __init__(self):
        self.secret_key = settings.stripe_secret_key
        self.public_key = settings.stripe_public_key
    
    async def process_payment(self, amount: float, currency: str, payment_data: dict) -> dict:
        """Procesar pago con Stripe"""
        try:
            # Simulación de pago con Stripe
            # En producción, aquí se usaría la API real de Stripe
            
            if not self.secret_key or self.secret_key == "":
                raise PaymentError("Stripe no configurado")
            
            # Simular procesamiento
            import random
            success = random.choice([True, True, True, False])  # 75% éxito
            
            if success:
                transaction_id = f"stripe_{generate_uuid()[:8]}"
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "gateway_reference": f"ch_{transaction_id}",
                    "status": "completed",
                    "message": "Pago procesado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "error": "Tarjeta declinada",
                    "status": "failed"
                }
        
        except Exception as e:
            logger.error(f"Error procesando pago con Stripe: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }

class PayPalProcessor:
    """Procesador de pagos con PayPal"""
    
    def __init__(self):
        self.client_id = settings.paypal_client_id
        self.client_secret = settings.paypal_client_secret
        self.mode = settings.paypal_mode
    
    async def process_payment(self, amount: float, currency: str, payment_data: dict) -> dict:
        """Procesar pago con PayPal"""
        try:
            if not self.client_id or self.client_id == "":
                raise PaymentError("PayPal no configurado")
            
            # Simular procesamiento
            import random
            success = random.choice([True, True, False])  # 67% éxito
            
            if success:
                transaction_id = f"paypal_{generate_uuid()[:8]}"
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "gateway_reference": f"PAYID-{transaction_id.upper()}",
                    "status": "completed",
                    "message": "Pago procesado exitosamente"
                }
            else:
                return {
                    "success": False,
                    "error": "Fondos insuficientes",
                    "status": "failed"
                }
        
        except Exception as e:
            logger.error(f"Error procesando pago con PayPal: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }

# Inicializar procesadores
stripe_processor = StripeProcessor()
paypal_processor = PayPalProcessor()

# ==================== UTILITY FUNCTIONS ====================

def get_payment_processor(payment_method: PaymentMethod):
    """Obtener procesador según método de pago"""
    if payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD, PaymentMethod.STRIPE]:
        return stripe_processor
    elif payment_method == PaymentMethod.PAYPAL:
        return paypal_processor
    else:
        raise PaymentError(f"Método de pago no soportado: {payment_method}")

async def update_reservation_status(reservation_id: str, status: str, payment_info: dict = None):
    """Actualizar estado de reserva en el servicio de booking"""
    try:
        async with httpx.AsyncClient() as client:
            update_data = {"status": status}
            
            response = await client.put(
                f"{settings.booking_service_url}/reservations/{reservation_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                logger.info(f"Estado de reserva actualizado: {reservation_id} -> {status}")
            else:
                logger.warning(f"Error actualizando reserva: {response.status_code}")
    
    except Exception as e:
        logger.error(f"Error actualizando reserva: {e}")

async def send_payment_notification(user_id: str, payment: PaymentDB, success: bool):
    """Enviar notificación de pago"""
    try:
        if success:
            subject = "Pago procesado exitosamente"
            message = f"Su pago de ${payment.amount} ha sido procesado exitosamente."
        else:
            subject = "Error en el procesamiento del pago"
            message = f"Hubo un error procesando su pago de ${payment.amount}."
        
        notification_data = {
            "user_id": user_id,
            "type": "email",
            "subject": subject,
            "message": message,
            "data": {
                "payment_id": payment.id,
                "amount": payment.amount,
                "status": payment.status
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.notification_service_url}/notifications",
                json=notification_data
            )
            
            if response.status_code == 200:
                logger.info(f"Notificación de pago enviada para usuario {user_id}")
    
    except Exception as e:
        logger.error(f"Error enviando notificación de pago: {e}")

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
                "service": "payment-service",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "connected",
                "stripe_configured": bool(settings.stripe_secret_key),
                "paypal_configured": bool(settings.paypal_client_id)
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return create_error_response("Service unhealthy", [str(e)])

@app.post("/payments", response_model=APIResponse)
async def process_payment(
    payment_data: PaymentCreate,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Procesar nuevo pago"""
    try:
        logger.info(f"Procesando pago para reserva {payment_data.reservation_id}")
        
        # Verificar que la reserva existe y pertenece al usuario
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.booking_service_url}/reservations/{payment_data.reservation_id}",
                headers={"Authorization": f"Bearer {current_user.get('access_token', '')}"}
            )
            
            if response.status_code != 200:
                raise NotFoundError("Reserva no encontrada")
            
            reservation_data = response.json()["data"]
        
        # Verificar que el monto coincide
        if abs(payment_data.amount - reservation_data["total_amount"]) > 0.01:
            raise ValidationError("El monto del pago no coincide con el total de la reserva")
        
        # Crear registro de pago
        payment_db = PaymentDB(
            id=generate_uuid(),
            reservation_id=payment_data.reservation_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            payment_method=payment_data.payment_method,
            status=PaymentStatus.PROCESSING,
            payment_data=json.dumps(payment_data.payment_data or {})
        )
        
        db.add(payment_db)
        db.commit()
        db.refresh(payment_db)
        
        # Procesar pago con el gateway correspondiente
        try:
            processor = get_payment_processor(PaymentMethod(payment_data.payment_method))
            result = await processor.process_payment(
                amount=payment_data.amount,
                currency=payment_data.currency,
                payment_data=payment_data.payment_data or {}
            )
            
            # Actualizar registro con el resultado
            if result["success"]:
                payment_db.status = PaymentStatus.COMPLETED
                payment_db.transaction_id = result.get("transaction_id")
                payment_db.gateway_reference = result.get("gateway_reference")
                payment_db.processed_at = datetime.utcnow()
                
                # Actualizar estado de reserva a "pagada"
                await update_reservation_status(
                    payment_data.reservation_id,
                    "paid",
                    {"payment_id": payment_db.id}
                )
                
                logger.info(f"Pago procesado exitosamente: {payment_db.id}")
                
            else:
                payment_db.status = PaymentStatus.FAILED
                payment_db.error_message = result.get("error", "Error desconocido")
                
                logger.warning(f"Pago falló: {payment_db.id} - {result.get('error')}")
            
            payment_db.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(payment_db)
            
            # Enviar notificación
            await send_payment_notification(
                user_id=current_user.get("user_id"),
                payment=payment_db,
                success=result["success"]
            )
            
            return create_response(
                data={
                    "payment_id": payment_db.id,
                    "status": payment_db.status,
                    "amount": payment_db.amount,
                    "currency": payment_db.currency,
                    "transaction_id": payment_db.transaction_id,
                    "gateway_reference": payment_db.gateway_reference,
                    "processed_at": payment_db.processed_at.isoformat() if payment_db.processed_at else None,
                    "success": result["success"],
                    "message": result.get("message", "Pago procesado")
                },
                message="Pago procesado" if result["success"] else "Error en el pago"
            )
        
        except Exception as e:
            # Error en el procesamiento
            payment_db.status = PaymentStatus.FAILED
            payment_db.error_message = str(e)
            payment_db.updated_at = datetime.utcnow()
            db.commit()
            
            logger.error(f"Error procesando pago: {e}")
            raise PaymentError(f"Error procesando pago: {e}")
    
    except (ValidationError, NotFoundError, PaymentError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error en proceso de pago: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/payments/{payment_id}", response_model=APIResponse)
async def get_payment(
    payment_id: str,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Obtener pago por ID"""
    try:
        payment = db.query(PaymentDB).filter(PaymentDB.id == payment_id).first()
        
        if not payment:
            raise NotFoundError("Pago no encontrado")
        
        # Verificar que el usuario tiene acceso al pago
        # (a través de la reserva asociada)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.booking_service_url}/reservations/{payment.reservation_id}",
                headers={"Authorization": f"Bearer {current_user.get('access_token', '')}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=403, detail="No tienes acceso a este pago")
        
        return create_response(
            data={
                "id": payment.id,
                "reservation_id": payment.reservation_id,
                "amount": payment.amount,
                "currency": payment.currency,
                "payment_method": payment.payment_method,
                "status": payment.status,
                "transaction_id": payment.transaction_id,
                "gateway_reference": payment.gateway_reference,
                "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
                "refunded_amount": payment.refunded_amount,
                "error_message": payment.error_message,
                "created_at": payment.created_at.isoformat(),
                "updated_at": payment.updated_at.isoformat()
            }
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo pago: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/payments/{payment_id}/refund", response_model=APIResponse)
async def refund_payment(
    payment_id: str,
    refund_amount: Optional[float] = None,
    reason: str = "Solicitud de reembolso",
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Procesar reembolso de pago"""
    try:
        payment = db.query(PaymentDB).filter(PaymentDB.id == payment_id).first()
        
        if not payment:
            raise NotFoundError("Pago no encontrado")
        
        if payment.status != PaymentStatus.COMPLETED:
            raise ValidationError("Solo se pueden reembolsar pagos completados")
        
        # Determinar monto del reembolso
        if refund_amount is None:
            refund_amount = payment.amount - payment.refunded_amount
        
        if refund_amount <= 0:
            raise ValidationError("Monto de reembolso inválido")
        
        if payment.refunded_amount + refund_amount > payment.amount:
            raise ValidationError("El monto del reembolso excede el pago original")
        
        # Verificar permisos
        role = current_user.get("role")
        if role not in ["admin", "hotel_manager"]:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        
        # Simular procesamiento de reembolso
        # En producción, aquí se llamaría a la API del gateway de pago
        try:
            import random
            success = random.choice([True, True, True, False])  # 75% éxito
            
            if success:
                # Actualizar registro de pago
                payment.refunded_amount += refund_amount
                
                if payment.refunded_amount >= payment.amount:
                    payment.status = PaymentStatus.REFUNDED
                else:
                    payment.status = PaymentStatus.PARTIALLY_REFUNDED
                
                payment.updated_at = datetime.utcnow()
                db.commit()
                
                # Actualizar estado de reserva si es reembolso completo
                if payment.refunded_amount >= payment.amount:
                    await update_reservation_status(
                        payment.reservation_id,
                        "refunded"
                    )
                
                logger.info(f"Reembolso procesado: {payment_id} - ${refund_amount}")
                
                return create_response(
                    data={
                        "payment_id": payment.id,
                        "refund_amount": refund_amount,
                        "total_refunded": payment.refunded_amount,
                        "status": payment.status,
                        "processed_at": datetime.utcnow().isoformat()
                    },
                    message="Reembolso procesado exitosamente"
                )
            else:
                raise PaymentError("Error procesando reembolso")
        
        except Exception as e:
            logger.error(f"Error en reembolso: {e}")
            raise PaymentError(f"Error procesando reembolso: {e}")
    
    except (ValidationError, NotFoundError, PaymentError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en reembolso: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/payments", response_model=APIResponse)
async def list_payments(
    reservation_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Listar pagos con filtros"""
    try:
        role = current_user.get("role")
        
        # Solo admin/hotel_manager pueden ver todos los pagos
        if role not in ["admin", "hotel_manager"]:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        
        query = db.query(PaymentDB)
        
        if reservation_id:
            query = query.filter(PaymentDB.reservation_id == reservation_id)
        
        if status:
            query = query.filter(PaymentDB.status == status)
        
        payments = query.order_by(PaymentDB.created_at.desc()).all()
        
        payments_data = [
            {
                "id": payment.id,
                "reservation_id": payment.reservation_id,
                "amount": payment.amount,
                "currency": payment.currency,
                "payment_method": payment.payment_method,
                "status": payment.status,
                "transaction_id": payment.transaction_id,
                "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
                "created_at": payment.created_at.isoformat()
            }
            for payment in payments
        ]
        
        return create_response(
            data=payments_data,
            message=f"Se encontraron {len(payments_data)} pagos"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listando pagos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Iniciando Payment Service en puerto {settings.port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )
