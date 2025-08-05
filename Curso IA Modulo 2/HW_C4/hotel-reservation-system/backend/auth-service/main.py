"""
Microservicio de Autenticación
Maneja registro, login, autenticación JWT y autorización de usuarios
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

# Agregar el directorio padre al path para importar shared
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config import AuthServiceSettings
from shared.models import UserCreate, UserLogin, User, Token, APIResponse
from shared.utils import (
    hash_password, verify_password, create_access_token, 
    verify_token, setup_logging, create_response, create_error_response,
    AuthenticationError, ValidationError
)

# Configuración
settings = AuthServiceSettings()
logger = setup_logging("auth-service", settings.log_level)

# Configuración de base de datos
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de base de datos
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(String, default="registered")
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Configuración de FastAPI
app = FastAPI(
    title="Hotel Reservation - Auth Service",
    description="Microservicio de autenticación y autorización",
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

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Obtener usuario actual desde token JWT"""
    try:
        token = credentials.credentials
        payload = verify_token(token, settings.secret_key, settings.algorithm)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inactivo"
            )
        
        return user
    
    except Exception as e:
        logger.error(f"Error en autenticación: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación"
        )

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
                "service": "auth-service",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "connected"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return create_error_response("Service unhealthy", [str(e)])

@app.post("/register", response_model=APIResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    try:
        logger.info(f"Intentando registrar usuario: {user_data.email}")
        
        # Verificar si el email ya existe
        existing_user = db.query(UserDB).filter(UserDB.email == user_data.email).first()
        if existing_user:
            raise ValidationError("El email ya está registrado")
        
        # Crear nuevo usuario
        from shared.utils import generate_uuid
        user_db = UserDB(
            id=generate_uuid(),
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            role=user_data.role,
            is_active=user_data.is_active
        )
        
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
        
        logger.info(f"Usuario registrado exitosamente: {user_data.email}")
        
        return create_response(
            data={
                "user_id": user_db.id,
                "email": user_db.email,
                "first_name": user_db.first_name,
                "last_name": user_db.last_name
            },
            message="Usuario registrado exitosamente"
        )
    
    except ValidationError as e:
        logger.warning(f"Error de validación en registro: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/login", response_model=APIResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Iniciar sesión de usuario"""
    try:
        logger.info(f"Intento de login: {login_data.email}")
        
        # Buscar usuario
        user = db.query(UserDB).filter(UserDB.email == login_data.email).first()
        if not user:
            raise AuthenticationError("Credenciales inválidas")
        
        # Verificar contraseña
        if not verify_password(login_data.password, user.hashed_password):
            raise AuthenticationError("Credenciales inválidas")
        
        # Verificar si el usuario está activo
        if not user.is_active:
            raise AuthenticationError("Usuario inactivo")
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Crear token de acceso
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        token_data = {"sub": user.id, "email": user.email, "role": user.role}
        access_token = create_access_token(
            data=token_data,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            expires_delta=access_token_expires
        )
        
        logger.info(f"Login exitoso: {login_data.email}")
        
        return create_response(
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.access_token_expire_minutes * 60,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role
                }
            },
            message="Login exitoso"
        )
    
    except AuthenticationError as e:
        logger.warning(f"Error de autenticación: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/me", response_model=APIResponse)
async def get_current_user_info(current_user: UserDB = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    try:
        return create_response(
            data={
                "id": current_user.id,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "phone": current_user.phone,
                "role": current_user.role,
                "is_active": current_user.is_active,
                "email_verified": current_user.email_verified,
                "phone_verified": current_user.phone_verified,
                "created_at": current_user.created_at.isoformat(),
                "last_login": current_user.last_login.isoformat() if current_user.last_login else None
            }
        )
    
    except Exception as e:
        logger.error(f"Error obteniendo información del usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/verify-token", response_model=APIResponse)
async def verify_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT"""
    try:
        token = credentials.credentials
        payload = verify_token(token, settings.secret_key, settings.algorithm)
        
        if payload is None:
            raise AuthenticationError("Token inválido")
        
        return create_response(
            data={
                "valid": True,
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "expires": payload.get("exp")
            },
            message="Token válido"
        )
    
    except AuthenticationError as e:
        logger.warning(f"Token inválido: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error verificando token: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/logout", response_model=APIResponse)
async def logout_user(current_user: UserDB = Depends(get_current_user)):
    """Cerrar sesión de usuario"""
    try:
        logger.info(f"Usuario {current_user.email} cerrando sesión")
        
        # En una implementación real, aquí se podría invalidar el token
        # agregándolo a una lista negra en Redis
        
        return create_response(
            message="Sesión cerrada exitosamente"
        )
    
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/users", response_model=APIResponse)
async def list_users(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Listar usuarios (solo admin)"""
    try:
        if current_user.role not in ["admin", "hotel_manager"]:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        
        users = db.query(UserDB).all()
        users_data = [
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            }
            for user in users
        ]
        
        return create_response(
            data=users_data,
            message=f"Se encontraron {len(users_data)} usuarios"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listando usuarios: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Iniciando Auth Service en puerto {settings.port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )
