"""
API Gateway - Punto de entrada unificado
Maneja el enrutamiento a todos los microservicios
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import sys
import os
from typing import Optional, Dict, Any
import time

# Agregar el directorio padre al path para importar shared
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config import APIGatewaySettings
from shared.utils import setup_logging, create_response, create_error_response

# Configuración
settings = APIGatewaySettings()
logger = setup_logging("api-gateway", settings.log_level)

# Configuración de FastAPI
app = FastAPI(
    title="Hotel Reservation System - API Gateway",
    description="Punto de entrada unificado para todos los microservicios",
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
security = HTTPBearer(auto_error=False)

# ==================== SERVICE REGISTRY ====================

SERVICES = {
    "auth": {
        "url": settings.auth_service_url,
        "name": "Authentication Service",
        "health_endpoint": "/health"
    },
    "booking": {
        "url": settings.booking_service_url,
        "name": "Booking Service",
        "health_endpoint": "/health"
    },
    "inventory": {
        "url": settings.inventory_service_url,
        "name": "Inventory Service",
        "health_endpoint": "/health"
    },
    "payment": {
        "url": settings.payment_service_url,
        "name": "Payment Service",
        "health_endpoint": "/health"
    },
    "notification": {
        "url": settings.notification_service_url,
        "name": "Notification Service",
        "health_endpoint": "/health"
    }
}

# ==================== ROUTE MAPPINGS ====================

ROUTE_MAPPINGS = {
    # Auth Service Routes
    "/auth/register": {"service": "auth", "path": "/register", "methods": ["POST"]},
    "/auth/login": {"service": "auth", "path": "/login", "methods": ["POST"]},
    "/auth/verify-token": {"service": "auth", "path": "/verify-token", "methods": ["POST"]},
    "/auth/me": {"service": "auth", "path": "/me", "methods": ["GET"]},
    "/auth/logout": {"service": "auth", "path": "/logout", "methods": ["POST"]},
    "/auth/users": {"service": "auth", "path": "/users", "methods": ["GET"]},
    
    # Inventory Service Routes
    "/hotels": {"service": "inventory", "path": "/hotels", "methods": ["GET", "POST"]},
    "/hotels/{hotel_id}": {"service": "inventory", "path": "/hotels/{hotel_id}", "methods": ["GET"]},
    "/rooms": {"service": "inventory", "path": "/rooms", "methods": ["POST"]},
    "/rooms/search": {"service": "inventory", "path": "/rooms/search", "methods": ["GET"]},
    "/rooms/{room_id}": {"service": "inventory", "path": "/rooms/{room_id}", "methods": ["GET"]},
    "/rooms/{room_id}/availability": {"service": "inventory", "path": "/rooms/{room_id}/availability", "methods": ["POST"]},
    
    # Booking Service Routes
    "/reservations": {"service": "booking", "path": "/reservations", "methods": ["GET", "POST"]},
    "/reservations/{reservation_id}": {"service": "booking", "path": "/reservations/{reservation_id}", "methods": ["GET", "PUT", "DELETE"]},
    "/reservations/confirmation/{confirmation_code}": {"service": "booking", "path": "/reservations/confirmation/{confirmation_code}", "methods": ["GET"]},
    
    # Payment Service Routes
    "/payments": {"service": "payment", "path": "/payments", "methods": ["GET", "POST"]},
    "/payments/{payment_id}": {"service": "payment", "path": "/payments/{payment_id}", "methods": ["GET"]},
    "/payments/{payment_id}/refund": {"service": "payment", "path": "/payments/{payment_id}/refund", "methods": ["POST"]},
    
    # Notification Service Routes
    "/notifications": {"service": "notification", "path": "/notifications", "methods": ["GET", "POST"]},
    "/notifications/{notification_id}": {"service": "notification", "path": "/notifications/{notification_id}", "methods": ["GET"]},
    "/notifications/{notification_id}/read": {"service": "notification", "path": "/notifications/{notification_id}/read", "methods": ["PATCH"]},
    "/notifications/bulk": {"service": "notification", "path": "/notifications/bulk", "methods": ["POST"]},
}

# ==================== UTILITY FUNCTIONS ====================

async def check_service_health(service_name: str) -> Dict[str, Any]:
    """Verificar salud de un servicio"""
    try:
        service_config = SERVICES.get(service_name)
        if not service_config:
            return {"status": "unknown", "error": "Service not found"}
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{service_config['url']}{service_config['health_endpoint']}"
            )
            
            if response.status_code == 200:
                return {"status": "healthy", "response_time": response.elapsed.total_seconds()}
            else:
                return {"status": "unhealthy", "status_code": response.status_code}
    
    except Exception as e:
        return {"status": "error", "error": str(e)}

async def forward_request(
    service_name: str,
    path: str,
    method: str,
    headers: Dict[str, str] = None,
    params: Dict[str, Any] = None,
    json_data: Dict[str, Any] = None,
    timeout: float = 30.0
) -> httpx.Response:
    """Reenviar solicitud a un microservicio"""
    try:
        service_config = SERVICES.get(service_name)
        if not service_config:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        url = f"{service_config['url']}{path}"
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers or {},
                params=params or {},
                json=json_data
            )
            return response
    
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")
    except Exception as e:
        logger.error(f"Error forwarding request to {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal gateway error")

def extract_path_params(route_pattern: str, actual_path: str) -> Dict[str, str]:
    """Extraer parámetros de la ruta"""
    pattern_parts = route_pattern.split("/")
    path_parts = actual_path.split("/")
    
    params = {}
    for i, part in enumerate(pattern_parts):
        if part.startswith("{") and part.endswith("}"):
            param_name = part[1:-1]
            if i < len(path_parts):
                params[param_name] = path_parts[i]
    
    return params

def build_service_path(route_pattern: str, actual_path: str, service_path: str) -> str:
    """Construir ruta del servicio con parámetros"""
    path_params = extract_path_params(route_pattern, actual_path)
    
    result_path = service_path
    for param_name, param_value in path_params.items():
        result_path = result_path.replace(f"{{{param_name}}}", param_value)
    
    return result_path

# ==================== MIDDLEWARE ====================

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware de logging"""
    start_time = time.time()
    
    # Log de entrada
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log de salida
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Endpoint raíz del API Gateway"""
    return create_response(
        data={
            "service": "API Gateway",
            "version": "1.0.0",
            "description": "Hotel Reservation System",
            "available_services": list(SERVICES.keys()),
            "documentation": "/docs"
        },
        message="Welcome to Hotel Reservation System API"
    )

@app.get("/health")
async def gateway_health():
    """Health check del API Gateway y todos los servicios"""
    try:
        gateway_status = {
            "service": "api-gateway",
            "status": "healthy",
            "timestamp": time.time()
        }
        
        # Verificar salud de todos los servicios
        services_health = {}
        for service_name in SERVICES.keys():
            services_health[service_name] = await check_service_health(service_name)
        
        return create_response(
            data={
                "gateway": gateway_status,
                "services": services_health,
                "overall_status": "healthy" if all(
                    s.get("status") == "healthy" for s in services_health.values()
                ) else "degraded"
            }
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return create_error_response("Gateway health check failed", [str(e)])

@app.get("/services")
async def list_services():
    """Listar servicios disponibles"""
    try:
        services_info = {}
        
        for service_name, config in SERVICES.items():
            health = await check_service_health(service_name)
            services_info[service_name] = {
                "name": config["name"],
                "url": config["url"],
                "status": health.get("status", "unknown"),
                "health_endpoint": config["health_endpoint"]
            }
        
        return create_response(
            data=services_info,
            message=f"Found {len(services_info)} services"
        )
    
    except Exception as e:
        logger.error(f"Error listing services: {e}")
        raise HTTPException(status_code=500, detail="Error listing services")

# ==================== DYNAMIC ROUTING ====================

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_request(
    path: str,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Enrutar solicitudes a los microservicios correspondientes"""
    try:
        method = request.method
        full_path = f"/{path}"
        
        # Buscar mapping de ruta
        matching_route = None
        for route_pattern, config in ROUTE_MAPPINGS.items():
            if method in config["methods"]:
                # Verificar si la ruta coincide (simple matching por ahora)
                if full_path == route_pattern:
                    matching_route = (route_pattern, config)
                    break
                
                # Verificar rutas con parámetros
                if "{" in route_pattern:
                    pattern_parts = route_pattern.split("/")
                    path_parts = full_path.split("/")
                    
                    if len(pattern_parts) == len(path_parts):
                        match = True
                        for i, (pattern_part, path_part) in enumerate(zip(pattern_parts, path_parts)):
                            if not (pattern_part == path_part or 
                                   (pattern_part.startswith("{") and pattern_part.endswith("}"))):
                                match = False
                                break
                        
                        if match:
                            matching_route = (route_pattern, config)
                            break
        
        if not matching_route:
            raise HTTPException(status_code=404, detail=f"Route {full_path} not found")
        
        route_pattern, route_config = matching_route
        service_name = route_config["service"]
        service_path = build_service_path(route_pattern, full_path, route_config["path"])
        
        # Preparar headers
        headers = dict(request.headers)
        if credentials:
            headers["Authorization"] = f"Bearer {credentials.credentials}"
        
        # Obtener parámetros de query
        query_params = dict(request.query_params)
        
        # Obtener body JSON si existe
        json_data = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                json_data = await request.json()
            except:
                pass  # No hay JSON body o es inválido
        
        # Reenviar solicitud
        response = await forward_request(
            service_name=service_name,
            path=service_path,
            method=method,
            headers=headers,
            params=query_params,
            json_data=json_data
        )
        
        # Retornar respuesta
        return JSONResponse(
            status_code=response.status_code,
            content=response.json() if response.content else None,
            headers=dict(response.headers)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error routing request {method} {full_path}: {e}")
        raise HTTPException(status_code=500, detail="Internal gateway error")

# ==================== SPECIFIC ENDPOINTS ====================

@app.post("/auth/register")
async def register_user(request: Request):
    """Endpoint específico para registro (con documentación)"""
    json_data = await request.json()
    
    response = await forward_request(
        service_name="auth",
        path="/register",
        method="POST",
        json_data=json_data
    )
    
    return JSONResponse(
        status_code=response.status_code,
        content=response.json()
    )

@app.post("/auth/login")
async def login_user(request: Request):
    """Endpoint específico para login (con documentación)"""
    json_data = await request.json()
    
    response = await forward_request(
        service_name="auth",
        path="/login",
        method="POST",
        json_data=json_data
    )
    
    return JSONResponse(
        status_code=response.status_code,
        content=response.json()
    )

@app.get("/rooms/search")
async def search_rooms(request: Request):
    """Endpoint específico para búsqueda de habitaciones"""
    query_params = dict(request.query_params)
    
    response = await forward_request(
        service_name="inventory",
        path="/rooms/search",
        method="GET",
        params=query_params
    )
    
    return JSONResponse(
        status_code=response.status_code,
        content=response.json()
    )

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Iniciando API Gateway en puerto {settings.port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower()
    )
