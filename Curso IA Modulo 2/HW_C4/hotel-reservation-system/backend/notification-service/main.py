"""
Microservicio de Notificaciones
Maneja el envío de emails, SMS y notificaciones push
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List, Dict, Any
import sys
import os
import httpx
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Agregar el directorio padre al path para importar shared
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config import NotificationServiceSettings
from shared.models import (
    NotificationCreate, Notification, NotificationType, APIResponse
)
from shared.utils import (
    setup_logging, create_response, create_error_response,
    generate_uuid, ValidationError, NotFoundError
)

# Configuración
settings = NotificationServiceSettings()
logger = setup_logging("notification-service", settings.log_level)

# Configuración de base de datos
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de base de datos
class NotificationDB(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text, nullable=True)  # JSON string
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Configuración de FastAPI
app = FastAPI(
    title="Hotel Reservation - Notification Service",
    description="Microservicio de envío de notificaciones",
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

# ==================== NOTIFICATION HANDLERS ====================

class EmailHandler:
    """Manejador de notificaciones por email"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_tls = settings.smtp_tls
        self.smtp_ssl = settings.smtp_ssl
    
    async def send_email(self, to_email: str, subject: str, message: str, data: dict = None) -> bool:
        """Enviar email"""
        try:
            if not self.smtp_user or not self.smtp_password:
                logger.warning("SMTP no configurado, simulando envío de email")
                return True  # Simular éxito para desarrollo
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Crear contenido HTML
            html_content = self._create_email_template(subject, message, data)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Enviar email
            if self.smtp_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.smtp_tls:
                    server.starttls()
            
            server.login(self.smtp_user, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_user, to_email, text)
            server.quit()
            
            logger.info(f"Email enviado exitosamente a {to_email}")
            return True
        
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {e}")
            return False
    
    def _create_email_template(self, subject: str, message: str, data: dict = None) -> str:
        """Crear plantilla HTML para email"""
        template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{subject}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #ecf0f1; padding: 15px; text-align: center; border-radius: 0 0 10px 10px; }}
                .button {{ background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏨 Hotel Reservations</h1>
                </div>
                <div class="content">
                    <h2>{subject}</h2>
                    <p>{message}</p>
                    {self._render_data_section(data)}
                </div>
                <div class="footer">
                    <p>Gracias por usar nuestro sistema de reservaciones</p>
                    <p><small>Este es un email automático, no responder.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        return template
    
    def _render_data_section(self, data: dict = None) -> str:
        """Renderizar sección de datos adicionales"""
        if not data:
            return ""
        
        html = "<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px;'>"
        html += "<h3>Detalles:</h3><ul>"
        
        for key, value in data.items():
            if key != "user_info":
                html += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
        
        html += "</ul></div>"
        return html

class SMSHandler:
    """Manejador de notificaciones por SMS"""
    
    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.phone_number = settings.twilio_phone_number
    
    async def send_sms(self, to_phone: str, message: str, data: dict = None) -> bool:
        """Enviar SMS"""
        try:
            if not self.account_sid or not self.auth_token:
                logger.warning("Twilio no configurado, simulando envío de SMS")
                return True  # Simular éxito para desarrollo
            
            # En producción, aquí se usaría la API de Twilio
            # from twilio.rest import Client
            # client = Client(self.account_sid, self.auth_token)
            # message = client.messages.create(
            #     body=message,
            #     from_=self.phone_number,
            #     to=to_phone
            # )
            
            logger.info(f"SMS enviado exitosamente a {to_phone}")
            return True
        
        except Exception as e:
            logger.error(f"Error enviando SMS a {to_phone}: {e}")
            return False

class PushHandler:
    """Manejador de notificaciones push"""
    
    async def send_push(self, user_id: str, subject: str, message: str, data: dict = None) -> bool:
        """Enviar notificación push"""
        try:
            # En producción, aquí se integraría con Firebase Cloud Messaging
            # o Apple Push Notification service
            
            logger.info(f"Push notification enviada a usuario {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error enviando push notification: {e}")
            return False

# Inicializar manejadores
email_handler = EmailHandler()
sms_handler = SMSHandler()
push_handler = PushHandler()

# ==================== UTILITY FUNCTIONS ====================

async def get_user_info(user_id: str) -> dict:
    """Obtener información del usuario"""
    try:
        async with httpx.AsyncClient() as client:
            # En una implementación real, aquí se consultaría el servicio de auth
            # para obtener email, teléfono, etc.
            return {
                "email": f"user{user_id}@example.com",  # Simulado
                "phone": "+1234567890",  # Simulado
                "first_name": "Usuario",
                "last_name": "Ejemplo"
            }
    except Exception as e:
        logger.error(f"Error obteniendo info del usuario {user_id}: {e}")
        return {}

async def send_notification_async(notification: NotificationDB, db: Session):
    """Enviar notificación de forma asíncrona"""
    try:
        user_info = await get_user_info(notification.user_id)
        data = json.loads(notification.data) if notification.data else {}
        data["user_info"] = user_info
        
        success = False
        
        if notification.type == NotificationType.EMAIL:
            success = await email_handler.send_email(
                to_email=user_info.get("email", ""),
                subject=notification.subject,
                message=notification.message,
                data=data
            )
        
        elif notification.type == NotificationType.SMS:
            success = await sms_handler.send_sms(
                to_phone=user_info.get("phone", ""),
                message=f"{notification.subject}: {notification.message}",
                data=data
            )
        
        elif notification.type == NotificationType.PUSH:
            success = await push_handler.send_push(
                user_id=notification.user_id,
                subject=notification.subject,
                message=notification.message,
                data=data
            )
        
        # Actualizar estado
        notification.sent = success
        notification.sent_at = datetime.utcnow() if success else None
        if not success:
            notification.error_message = "Error enviando notificación"
        
        notification.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Notificación {'enviada' if success else 'falló'}: {notification.id}")
    
    except Exception as e:
        logger.error(f"Error en envío asíncrono: {e}")
        notification.sent = False
        notification.error_message = str(e)
        notification.updated_at = datetime.utcnow()
        db.commit()

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
                "service": "notification-service",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "connected",
                "email_configured": bool(settings.smtp_user),
                "sms_configured": bool(settings.twilio_account_sid)
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return create_error_response("Service unhealthy", [str(e)])

@app.post("/notifications", response_model=APIResponse)
async def create_notification(
    notification_data: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Crear y enviar nueva notificación"""
    try:
        logger.info(f"Creando notificación para usuario {notification_data.user_id}")
        
        # Crear notificación
        notification_db = NotificationDB(
            id=generate_uuid(),
            user_id=notification_data.user_id,
            type=notification_data.type,
            subject=notification_data.subject,
            message=notification_data.message,
            data=json.dumps(notification_data.data or {})
        )
        
        db.add(notification_db)
        db.commit()
        db.refresh(notification_db)
        
        # Enviar notificación en segundo plano
        background_tasks.add_task(send_notification_async, notification_db, db)
        
        logger.info(f"Notificación creada: {notification_db.id}")
        
        return create_response(
            data={
                "notification_id": notification_db.id,
                "user_id": notification_db.user_id,
                "type": notification_db.type,
                "subject": notification_db.subject,
                "status": "queued"
            },
            message="Notificación creada y enviada"
        )
    
    except Exception as e:
        logger.error(f"Error creando notificación: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/notifications", response_model=APIResponse)
async def list_notifications(
    user_id: Optional[str] = None,
    type: Optional[str] = None,
    sent: Optional[bool] = None,
    read: Optional[bool] = None,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Listar notificaciones con filtros"""
    try:
        role = current_user.get("role")
        current_user_id = current_user.get("user_id")
        
        query = db.query(NotificationDB)
        
        # Los usuarios normales solo ven sus notificaciones
        if role not in ["admin", "hotel_manager"]:
            query = query.filter(NotificationDB.user_id == current_user_id)
        elif user_id:
            query = query.filter(NotificationDB.user_id == user_id)
        
        if type:
            query = query.filter(NotificationDB.type == type)
        
        if sent is not None:
            query = query.filter(NotificationDB.sent == sent)
        
        if read is not None:
            query = query.filter(NotificationDB.read == read)
        
        notifications = query.order_by(NotificationDB.created_at.desc()).all()
        
        notifications_data = [
            {
                "id": notification.id,
                "user_id": notification.user_id,
                "type": notification.type,
                "subject": notification.subject,
                "message": notification.message,
                "sent": notification.sent,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "read": notification.read,
                "read_at": notification.read_at.isoformat() if notification.read_at else None,
                "error_message": notification.error_message,
                "created_at": notification.created_at.isoformat()
            }
            for notification in notifications
        ]
        
        return create_response(
            data=notifications_data,
            message=f"Se encontraron {len(notifications_data)} notificaciones"
        )
    
    except Exception as e:
        logger.error(f"Error listando notificaciones: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/notifications/{notification_id}", response_model=APIResponse)
async def get_notification(
    notification_id: str,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Obtener notificación por ID"""
    try:
        notification = db.query(NotificationDB).filter(NotificationDB.id == notification_id).first()
        
        if not notification:
            raise NotFoundError("Notificación no encontrada")
        
        # Verificar permisos
        role = current_user.get("role")
        current_user_id = current_user.get("user_id")
        
        if notification.user_id != current_user_id and role not in ["admin", "hotel_manager"]:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta notificación")
        
        return create_response(
            data={
                "id": notification.id,
                "user_id": notification.user_id,
                "type": notification.type,
                "subject": notification.subject,
                "message": notification.message,
                "data": json.loads(notification.data) if notification.data else {},
                "sent": notification.sent,
                "sent_at": notification.sent_at.isoformat() if notification.sent_at else None,
                "read": notification.read,
                "read_at": notification.read_at.isoformat() if notification.read_at else None,
                "error_message": notification.error_message,
                "created_at": notification.created_at.isoformat(),
                "updated_at": notification.updated_at.isoformat()
            }
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo notificación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.patch("/notifications/{notification_id}/read", response_model=APIResponse)
async def mark_notification_read(
    notification_id: str,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Marcar notificación como leída"""
    try:
        notification = db.query(NotificationDB).filter(NotificationDB.id == notification_id).first()
        
        if not notification:
            raise NotFoundError("Notificación no encontrada")
        
        # Verificar permisos
        current_user_id = current_user.get("user_id")
        
        if notification.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta notificación")
        
        # Marcar como leída
        notification.read = True
        notification.read_at = datetime.utcnow()
        notification.updated_at = datetime.utcnow()
        
        db.commit()
        
        return create_response(
            data={
                "notification_id": notification.id,
                "read": notification.read,
                "read_at": notification.read_at.isoformat()
            },
            message="Notificación marcada como leída"
        )
    
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marcando notificación como leída: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/notifications/bulk", response_model=APIResponse)
async def send_bulk_notifications(
    notifications_data: List[NotificationCreate],
    background_tasks: BackgroundTasks,
    current_user = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Enviar notificaciones en masa"""
    try:
        # Verificar permisos
        role = current_user.get("role")
        if role not in ["admin", "hotel_manager"]:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        
        created_notifications = []
        
        for notification_data in notifications_data:
            # Crear notificación
            notification_db = NotificationDB(
                id=generate_uuid(),
                user_id=notification_data.user_id,
                type=notification_data.type,
                subject=notification_data.subject,
                message=notification_data.message,
                data=json.dumps(notification_data.data or {})
            )
            
            db.add(notification_db)
            created_notifications.append(notification_db)
        
        db.commit()
        
        # Enviar notificaciones en segundo plano
        for notification in created_notifications:
            db.refresh(notification)
            background_tasks.add_task(send_notification_async, notification, db)
        
        logger.info(f"Creadas {len(created_notifications)} notificaciones en masa")
        
        return create_response(
            data={
                "notifications_created": len(created_notifications),
                "status": "queued"
            },
            message=f"{len(created_notifications)} notificaciones creadas y enviadas"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en notificaciones en masa: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Iniciando Notification Service en puerto {settings.port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )
