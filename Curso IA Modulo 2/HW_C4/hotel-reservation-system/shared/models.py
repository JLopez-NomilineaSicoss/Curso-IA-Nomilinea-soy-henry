"""
Modelos de datos compartidos para todos los microservicios
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid

# ==================== ENUMS ====================

class UserRole(str, Enum):
    """Roles de usuario"""
    GUEST = "guest"
    REGISTERED = "registered"
    PREMIUM = "premium"
    ADMIN = "admin"
    HOTEL_MANAGER = "hotel_manager"

class ReservationStatus(str, Enum):
    """Estados de la reservación"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    MODIFIED = "modified"
    REFUNDED = "refunded"

class PaymentStatus(str, Enum):
    """Estados del pago"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class PaymentMethod(str, Enum):
    """Métodos de pago"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"

class RoomType(str, Enum):
    """Tipos de habitación"""
    SINGLE = "single"
    DOUBLE = "double"
    TWIN = "twin"
    TRIPLE = "triple"
    SUITE = "suite"
    PRESIDENTIAL = "presidential"
    FAMILY = "family"

class NotificationType(str, Enum):
    """Tipos de notificación"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

# ==================== BASE MODELS ====================

class BaseEntity(BaseModel):
    """Modelo base para todas las entidades"""
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# ==================== USER MODELS ====================

class UserBase(BaseModel):
    """Modelo base de usuario"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = Field(None, regex=r"^\+?1?\d{9,15}$")
    role: UserRole = UserRole.REGISTERED
    is_active: bool = True

class UserCreate(UserBase):
    """Modelo para crear usuario"""
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class UserUpdate(BaseModel):
    """Modelo para actualizar usuario"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, regex=r"^\+?1?\d{9,15}$")
    is_active: Optional[bool] = None

class User(UserBase, BaseEntity):
    """Modelo completo de usuario"""
    hashed_password: str
    last_login: Optional[datetime] = None
    email_verified: bool = False
    phone_verified: bool = False

class UserLogin(BaseModel):
    """Modelo para login"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Modelo de token de autenticación"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str

# ==================== HOTEL MODELS ====================

class HotelBase(BaseModel):
    """Modelo base de hotel"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    address: str = Field(..., min_length=1, max_length=300)
    city: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    amenities: Optional[List[str]] = []
    images: Optional[List[str]] = []

class Hotel(HotelBase, BaseEntity):
    """Modelo completo de hotel"""
    is_active: bool = True
    total_rooms: int = 0

# ==================== ROOM MODELS ====================

class RoomBase(BaseModel):
    """Modelo base de habitación"""
    hotel_id: str
    room_number: str = Field(..., min_length=1, max_length=20)
    room_type: RoomType
    description: Optional[str] = Field(None, max_length=500)
    capacity: int = Field(..., ge=1, le=10)
    price_per_night: float = Field(..., ge=0)
    amenities: Optional[List[str]] = []
    images: Optional[List[str]] = []
    is_available: bool = True

class Room(RoomBase, BaseEntity):
    """Modelo completo de habitación"""
    pass

class RoomAvailability(BaseModel):
    """Modelo de disponibilidad de habitación"""
    room_id: str
    date: date
    is_available: bool = True
    price_override: Optional[float] = None

# ==================== RESERVATION MODELS ====================

class ReservationBase(BaseModel):
    """Modelo base de reservación"""
    user_id: str
    hotel_id: str
    room_id: str
    check_in_date: date
    check_out_date: date
    guests: int = Field(..., ge=1, le=10)
    special_requests: Optional[str] = Field(None, max_length=500)
    
    @validator('check_out_date')
    def check_out_after_check_in(cls, v, values):
        if 'check_in_date' in values and v <= values['check_in_date']:
            raise ValueError('La fecha de check-out debe ser posterior al check-in')
        return v

class ReservationCreate(ReservationBase):
    """Modelo para crear reservación"""
    pass

class ReservationUpdate(BaseModel):
    """Modelo para actualizar reservación"""
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    guests: Optional[int] = Field(None, ge=1, le=10)
    special_requests: Optional[str] = Field(None, max_length=500)
    status: Optional[ReservationStatus] = None

class Reservation(ReservationBase, BaseEntity):
    """Modelo completo de reservación"""
    status: ReservationStatus = ReservationStatus.PENDING
    total_amount: float = Field(..., ge=0)
    confirmation_code: str
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None

# ==================== PAYMENT MODELS ====================

class PaymentBase(BaseModel):
    """Modelo base de pago"""
    reservation_id: str
    amount: float = Field(..., ge=0)
    currency: str = Field(default="USD", max_length=3)
    payment_method: PaymentMethod
    
class PaymentCreate(PaymentBase):
    """Modelo para crear pago"""
    payment_data: Optional[Dict[str, Any]] = {}

class Payment(PaymentBase, BaseEntity):
    """Modelo completo de pago"""
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: Optional[str] = None
    gateway_reference: Optional[str] = None
    processed_at: Optional[datetime] = None
    refunded_amount: float = 0.0

# ==================== NOTIFICATION MODELS ====================

class NotificationBase(BaseModel):
    """Modelo base de notificación"""
    user_id: str
    type: NotificationType
    subject: str = Field(..., max_length=200)
    message: str = Field(..., max_length=1000)
    data: Optional[Dict[str, Any]] = {}

class NotificationCreate(NotificationBase):
    """Modelo para crear notificación"""
    pass

class Notification(NotificationBase, BaseEntity):
    """Modelo completo de notificación"""
    sent: bool = False
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    read: bool = False
    read_at: Optional[datetime] = None

# ==================== SEARCH MODELS ====================

class RoomSearchCriteria(BaseModel):
    """Criterios de búsqueda de habitaciones"""
    city: Optional[str] = None
    check_in_date: date
    check_out_date: date
    guests: int = Field(..., ge=1, le=10)
    room_type: Optional[RoomType] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    amenities: Optional[List[str]] = []
    hotel_rating: Optional[float] = Field(None, ge=0, le=5)
    
    @validator('check_out_date')
    def check_out_after_check_in(cls, v, values):
        if 'check_in_date' in values and v <= values['check_in_date']:
            raise ValueError('La fecha de check-out debe ser posterior al check-in')
        return v

class RoomSearchResult(BaseModel):
    """Resultado de búsqueda de habitaciones"""
    room: Room
    hotel: Hotel
    available_dates: List[date]
    total_price: float
    average_rating: Optional[float] = None

# ==================== API RESPONSE MODELS ====================

class APIResponse(BaseModel):
    """Respuesta estándar de la API"""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Any] = None
    errors: Optional[List[str]] = None

class PaginatedResponse(BaseModel):
    """Respuesta paginada"""
    items: List[Any]
    total: int
    page: int = 1
    per_page: int = 10
    pages: int
    has_next: bool
    has_prev: bool

# ==================== HEALTH CHECK ====================

class HealthCheck(BaseModel):
    """Modelo para health check"""
    service: str
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    database_status: str = "connected"
    redis_status: str = "connected"
