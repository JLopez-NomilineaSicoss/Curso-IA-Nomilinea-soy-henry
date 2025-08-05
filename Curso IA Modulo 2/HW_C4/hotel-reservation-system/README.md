# 🏨 Sistema de Reservación de Habitaciones

Sistema completo de microservicios para reservación de habitaciones desarrollado en Python con FastAPI.

## 🚀 Características Principales

- **Arquitectura de Microservicios**: Sistema distribuido con servicios independientes
- **Autenticación JWT**: Sistema de autenticación y autorización seguro
- **API Gateway**: Punto de entrada unificado para todos los servicios
- **Base de Datos Distribuida**: PostgreSQL con Redis para caché
- **Integración de Pagos**: Stripe y PayPal
- **Notificaciones**: Email y SMS
- **Contenedorización**: Docker y Docker Compose
- **Documentación**: Swagger/OpenAPI automática

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────────┐
│   Frontend      │    │   API Gateway    │
│ (React/Streamlit)│◄──►│   (FastAPI)      │
└─────────────────┘    └──────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌──────▼─────┐ ┌──────▼─────┐
        │ Auth Service │ │ Booking    │ │ Inventory  │
        │ (FastAPI)    │ │ Service    │ │ Service    │
        └──────────────┘ └────────────┘ └────────────┘
                │               │               │
        ┌───────▼──────┐ ┌──────▼─────┐ ┌──────▼─────┐
        │ Payment      │ │ Notification│ │ External   │
        │ Service      │ │ Service     │ │ APIs       │
        └──────────────┘ └────────────┘ └────────────┘
```

## 📁 Estructura del Proyecto

```
hotel-reservation-system/
├── backend/
│   ├── api-gateway/           # API Gateway (FastAPI)
│   ├── auth-service/          # Autenticación y autorización
│   ├── booking-service/       # Gestión de reservas
│   ├── inventory-service/     # Gestión de inventario
│   ├── payment-service/       # Procesamiento de pagos
│   └── notification-service/  # Envío de notificaciones
├── frontend/
│   ├── web-app/              # Aplicación web (React/Streamlit)
│   └── mobile-app/           # App móvil (React Native)
├── integration/
│   ├── payment-gateways/     # Integraciones de pago
│   ├── external-apis/        # APIs externas
│   └── messaging/            # Servicios de mensajería
├── shared/
│   ├── models/               # Modelos compartidos
│   ├── utils/                # Utilidades comunes
│   └── configs/              # Configuraciones
├── deployment/
│   ├── docker/               # Archivos Docker
│   ├── kubernetes/           # Configuración K8s
│   └── scripts/              # Scripts de deployment
└── docs/                     # Documentación y diagramas
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para Python
- **PostgreSQL**: Base de datos principal
- **Redis**: Caché y sessions
- **Celery**: Tareas asíncronas
- **JWT**: Autenticación
- **Pydantic**: Validación de datos

### Frontend
- **Streamlit**: Interfaz web interactiva
- **React**: Aplicación web (opcional)
- **Bootstrap**: Estilos y componentes

### DevOps
- **Docker**: Contenedorización
- **Docker Compose**: Orquestación local
- **pytest**: Testing
- **Black**: Formateo de código
- **Flake8**: Linting

## 🚀 Inicio Rápido

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd hotel-reservation-system
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Ejecutar con Docker Compose**
```bash
docker-compose up -d
```

4. **Acceder a la aplicación**
- API Gateway: http://localhost:8000
- Documentación API: http://localhost:8000/docs
- Frontend: http://localhost:8501

## 📊 Servicios y Puertos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| API Gateway | 8000 | Punto de entrada principal |
| Auth Service | 8001 | Autenticación y autorización |
| Booking Service | 8002 | Gestión de reservas |
| Inventory Service | 8003 | Gestión de inventario |
| Payment Service | 8004 | Procesamiento de pagos |
| Notification Service | 8005 | Envío de notificaciones |
| Frontend | 8501 | Interfaz de usuario |
| PostgreSQL | 5432 | Base de datos |
| Redis | 6379 | Caché y sessions |

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=backend

# Tests de un servicio específico
pytest backend/auth-service/tests/
```

## 📈 Monitoreo

- **Health Checks**: Endpoints `/health` en cada servicio
- **Métricas**: Prometheus integration
- **Logs**: Structured logging con loguru

## 🔧 Desarrollo

### Instalación local
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servicios individuales
cd backend/auth-service
uvicorn main:app --reload --port 8001
```

## 📋 Funcionalidades Implementadas

✅ **Autenticación y Autorización**
- Registro y login de usuarios
- JWT tokens
- Roles y permisos
- Password hashing

✅ **Gestión de Reservas**
- Búsqueda de habitaciones
- Creación de reservas
- Modificación y cancelación
- Estados de reserva

✅ **Inventario de Habitaciones**
- Gestión de disponibilidad
- Tipos de habitaciones
- Precios dinámicos
- Bloqueo temporal

✅ **Procesamiento de Pagos**
- Integración Stripe
- Integración PayPal
- Manejo de transacciones
- Reembolsos

✅ **Sistema de Notificaciones**
- Emails transaccionales
- SMS notifications
- Plantillas personalizadas
- Queue de mensajes

## 🏆 Próximas Características

- [ ] Integración con APIs externas (Booking.com, Expedia)
- [ ] Sistema de reviews y ratings
- [ ] Análisis y reportes
- [ ] App móvil nativa
- [ ] Inteligencia artificial para recomendaciones

## 📞 Soporte

Para soporte técnico o preguntas sobre el proyecto, por favor crear un issue en el repositorio.

---

**Desarrollado con ❤️ por el equipo de desarrollo**
