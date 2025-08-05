"""
Configuración compartida para todos los microservicios
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Configuración base para todos los servicios"""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://hotel_user:hotel_password@localhost:5432/hotel_reservations")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8000"
    ]
    
    # Services URLs
    auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
    booking_service_url: str = os.getenv("BOOKING_SERVICE_URL", "http://localhost:8002")
    inventory_service_url: str = os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8003")
    payment_service_url: str = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8004")
    notification_service_url: str = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8005")
    
    # Email Configuration
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_tls: bool = os.getenv("SMTP_TLS", "true").lower() == "true"
    smtp_ssl: bool = os.getenv("SMTP_SSL", "false").lower() == "true"
    
    # SMS Configuration (Twilio)
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_phone_number: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Payment Gateways
    stripe_public_key: str = os.getenv("STRIPE_PUBLIC_KEY", "")
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    paypal_client_id: str = os.getenv("PAYPAL_CLIENT_ID", "")
    paypal_client_secret: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    paypal_mode: str = os.getenv("PAYPAL_MODE", "sandbox")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Rate Limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    rate_limit_burst: int = int(os.getenv("RATE_LIMIT_BURST", "10"))
    
    # File Storage
    upload_folder: str = os.getenv("UPLOAD_FOLDER", "uploads/")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "5242880"))  # 5MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()

# Configuraciones específicas por servicio
class AuthServiceSettings(Settings):
    """Configuración específica para el servicio de autenticación"""
    service_name: str = "auth-service"
    port: int = 8001
    
class BookingServiceSettings(Settings):
    """Configuración específica para el servicio de reservas"""
    service_name: str = "booking-service"
    port: int = 8002
    
class InventoryServiceSettings(Settings):
    """Configuración específica para el servicio de inventario"""
    service_name: str = "inventory-service"
    port: int = 8003
    
class PaymentServiceSettings(Settings):
    """Configuración específica para el servicio de pagos"""
    service_name: str = "payment-service"
    port: int = 8004
    
class NotificationServiceSettings(Settings):
    """Configuración específica para el servicio de notificaciones"""
    service_name: str = "notification-service"
    port: int = 8005
    
class APIGatewaySettings(Settings):
    """Configuración específica para el API Gateway"""
    service_name: str = "api-gateway"
    port: int = 8000
