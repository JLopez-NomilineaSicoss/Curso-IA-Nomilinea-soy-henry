"""
Utilidades compartidas para todos los microservicios
"""
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
import re
import uuid
from passlib.context import CryptContext
from jose import JWTError, jwt
from loguru import logger
import redis
import json

# Configuración de password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Genera hash de contraseña usando bcrypt
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica contraseña contra hash
    """
    return pwd_context.verify(plain_password, hashed_password)

def generate_confirmation_code() -> str:
    """
    Genera código de confirmación único
    """
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

def generate_uuid() -> str:
    """
    Genera UUID único
    """
    return str(uuid.uuid4())

def create_access_token(data: dict, secret_key: str, algorithm: str = "HS256", expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea token JWT de acceso
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def verify_token(token: str, secret_key: str, algorithm: str = "HS256") -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica token JWT
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        return None

def validate_email(email: str) -> bool:
    """
    Valida formato de email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """
    Valida formato de teléfono
    """
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Formatea cantidad de dinero
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "MXN": "$"
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:.2f}"

def calculate_nights(check_in: datetime, check_out: datetime) -> int:
    """
    Calcula número de noches entre fechas
    """
    return (check_out - check_in).days

def calculate_total_price(price_per_night: float, nights: int, guests: int = 1, tax_rate: float = 0.16) -> Dict[str, float]:
    """
    Calcula precio total incluyendo impuestos
    """
    subtotal = price_per_night * nights
    taxes = subtotal * tax_rate
    total = subtotal + taxes
    
    return {
        "subtotal": round(subtotal, 2),
        "taxes": round(taxes, 2),
        "total": round(total, 2),
        "price_per_night": price_per_night,
        "nights": nights
    }

def sanitize_string(text: str, max_length: int = 100) -> str:
    """
    Sanitiza string eliminando caracteres peligrosos
    """
    if not text:
        return ""
    
    # Eliminar caracteres HTML/SQL peligrosos
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '--']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text[:max_length].strip()

def generate_file_hash(file_content: bytes) -> str:
    """
    Genera hash MD5 para archivos
    """
    return hashlib.md5(file_content).hexdigest()

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formatea datetime a string
    """
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parsea string a datetime
    """
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None

# ==================== REDIS UTILITIES ====================

class RedisClient:
    """Cliente Redis para caché y sesiones"""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
    
    def set(self, key: str, value: Any, expiration: int = 3600) -> bool:
        """
        Guarda valor en Redis con expiración
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.redis_client.setex(key, expiration, value)
        except Exception as e:
            logger.error(f"Error setting Redis key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene valor de Redis
        """
        try:
            value = self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Error getting Redis key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Elimina clave de Redis
        """
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting Redis key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Verifica si existe clave en Redis
        """
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Error checking Redis key {key}: {e}")
            return False

# ==================== LOGGING UTILITIES ====================

def setup_logging(service_name: str, log_level: str = "INFO"):
    """
    Configura logging para el servicio
    """
    logger.remove()  # Eliminar configuración por defecto
    
    # Configurar formato de logs
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        f"<magenta>{service_name}</magenta> | "
        "<level>{message}</level>"
    )
    
    # Log a consola
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format=log_format,
        level=log_level,
        colorize=True
    )
    
    # Log a archivo
    logger.add(
        f"logs/{service_name}.log",
        format=log_format,
        level=log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip"
    )
    
    return logger

# ==================== VALIDATION UTILITIES ====================

def validate_date_range(start_date: datetime, end_date: datetime, max_days: int = 365) -> bool:
    """
    Valida rango de fechas
    """
    if start_date >= end_date:
        return False
    
    if (end_date - start_date).days > max_days:
        return False
    
    if start_date < datetime.now():
        return False
    
    return True

def validate_guest_count(guests: int, max_guests: int = 10) -> bool:
    """
    Valida número de huéspedes
    """
    return 1 <= guests <= max_guests

def validate_room_availability(check_in: datetime, check_out: datetime, existing_reservations: list) -> bool:
    """
    Valida disponibilidad de habitación
    """
    for reservation in existing_reservations:
        res_check_in = reservation.get('check_in_date')
        res_check_out = reservation.get('check_out_date')
        
        # Verificar solapamiento
        if not (check_out <= res_check_in or check_in >= res_check_out):
            return False
    
    return True

# ==================== ERROR HANDLING ====================

class HotelReservationException(Exception):
    """Excepción base del sistema"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class AuthenticationError(HotelReservationException):
    """Error de autenticación"""
    pass

class AuthorizationError(HotelReservationException):
    """Error de autorización"""
    pass

class ValidationError(HotelReservationException):
    """Error de validación"""
    pass

class NotFoundError(HotelReservationException):
    """Error de recurso no encontrado"""
    pass

class PaymentError(HotelReservationException):
    """Error de pago"""
    pass

class InventoryError(HotelReservationException):
    """Error de inventario"""
    pass

# ==================== API UTILITIES ====================

def create_response(data: Any = None, message: str = "Success", success: bool = True, errors: list = None) -> Dict[str, Any]:
    """
    Crea respuesta estándar de API
    """
    return {
        "success": success,
        "message": message,
        "data": data,
        "errors": errors,
        "timestamp": datetime.utcnow().isoformat()
    }

def create_error_response(message: str, errors: list = None, error_code: str = None) -> Dict[str, Any]:
    """
    Crea respuesta de error estándar
    """
    return {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors or [],
        "error_code": error_code,
        "timestamp": datetime.utcnow().isoformat()
    }
