# 🏨 Sistema de Reservas de Hotel - Microservicios

Un sistema completo de reservas de hotel construido con arquitectura de microservicios usando Python, FastAPI, PostgreSQL, Redis y Streamlit.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Tecnologías](#-tecnologías)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [API Endpoints](#-api-endpoints)
- [Testing](#-testing)
- [Monitoreo](#-monitoreo)

## ✨ Características

### 🔐 Autenticación y Autorización
- Registro y login de usuarios
- Autenticación JWT
- Roles de usuario (admin, manager, guest)
- Gestión de sesiones con Redis

### 🏨 Gestión de Inventario
- Administración de hoteles
- Gestión de habitaciones
- Control de disponibilidad
- Búsqueda y filtrado avanzado

### 📅 Sistema de Reservas
- Creación de reservas
- Modificación y cancelación
- Validación de disponibilidad
- Cálculo automático de precios

### 💳 Procesamiento de Pagos
- Integración con Stripe
- Integración con PayPal
- Gestión de reembolsos
- Historial de transacciones

### 📧 Sistema de Notificaciones
- Notificaciones por email
- Notificaciones SMS (Twilio)
- Notificaciones push
- Templates personalizables

### 🌐 Frontend Web
- Interfaz de usuario con Streamlit
- Dashboard administrativo
- Panel de usuario
- Reportes y analíticas

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │     Nginx       │
│   (Streamlit)   │◄──►│   (FastAPI)     │◄──►│ (Load Balancer) │
│   Port: 8501    │    │   Port: 8000    │    │   Port: 80      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
     ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
     │ Auth Service    │ │Booking Service  │ │Inventory Service│
     │   Port: 8001    │ │   Port: 8002    │ │   Port: 8003    │
     └─────────────────┘ └─────────────────┘ └─────────────────┘
                │               │               │
     ┌─────────────────┐ ┌─────────────────┐         │
     │Payment Service  │ │Notification Svc │         │
     │   Port: 8004    │ │   Port: 8005    │         │
     └─────────────────┘ └─────────────────┘         │
                │               │                     │
        ┌───────────────────────┼─────────────────────┘
        │                       │
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │
│   Port: 5432    │    │   Port: 6379    │
└─────────────────┘    └─────────────────┘
```

## 🛠️ Tecnologías

### Backend
- **Python 3.11+**
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para bases de datos
- **Pydantic** - Validación de datos
- **PostgreSQL** - Base de datos principal
- **Redis** - Cache y gestión de sesiones
- **JWT** - Autenticación basada en tokens

### Frontend
- **Streamlit** - Framework para aplicaciones web
- **Plotly** - Visualización de datos
- **Pandas** - Manipulación de datos

### DevOps & Monitoreo
- **Docker & Docker Compose** - Containerización
- **Nginx** - Load balancer y proxy reverso
- **Prometheus** - Monitoreo y métricas
- **Grafana** - Visualización de métricas

## 🚀 Instalación

### Prerrequisitos
- Docker y Docker Compose
- Git
- Make (opcional, para comandos simplificados)

### Instalación Rápida

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

3. **Construir y levantar servicios**
```bash
make up-build
# O sin Make:
docker-compose up -d --build
```

4. **Ejecutar migraciones**
```bash
make migrate
# O sin Make:
docker-compose exec auth-service alembic upgrade head
```

## 🎯 Uso

### Acceso a la Aplicación

- **Frontend Web**: http://localhost:8501
- **API Gateway**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Nginx**: http://localhost:80

### Usuarios por Defecto

```
Admin:
- Email: admin@hotel.com
- Password: admin123

Manager:
- Email: manager@hotel.com
- Password: manager123

Guest:
- Email: guest@hotel.com
- Password: guest123
```

## 📚 API Endpoints

### Auth Service (Port: 8001)
```
POST   /auth/register     - Registrar usuario
POST   /auth/login        - Iniciar sesión
POST   /auth/refresh      - Renovar token
GET    /auth/profile      - Obtener perfil
PUT    /auth/profile      - Actualizar perfil
```

### Inventory Service (Port: 8003)
```
GET    /hotels            - Listar hoteles
POST   /hotels            - Crear hotel
GET    /hotels/{id}       - Obtener hotel
PUT    /hotels/{id}       - Actualizar hotel
DELETE /hotels/{id}       - Eliminar hotel

GET    /rooms             - Listar habitaciones
POST   /rooms             - Crear habitación
GET    /rooms/{id}        - Obtener habitación
PUT    /rooms/{id}        - Actualizar habitación
DELETE /rooms/{id}        - Eliminar habitación
GET    /rooms/search      - Buscar habitaciones disponibles
```

### Booking Service (Port: 8002)
```
GET    /reservations      - Listar reservas
POST   /reservations      - Crear reserva
GET    /reservations/{id} - Obtener reserva
PUT    /reservations/{id} - Actualizar reserva
DELETE /reservations/{id} - Cancelar reserva
```

### Payment Service (Port: 8004)
```
POST   /payments          - Procesar pago
GET    /payments/{id}     - Obtener pago
POST   /payments/{id}/refund - Reembolsar pago
GET    /payments/history  - Historial de pagos
```

### Notification Service (Port: 8005)
```
POST   /notifications/email - Enviar email
POST   /notifications/sms   - Enviar SMS
POST   /notifications/push  - Enviar push notification
GET    /notifications       - Listar notificaciones
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
make test

# Tests con coverage
make test-coverage

# Tests de un servicio específico
docker-compose exec auth-service python -m pytest tests/ -v
```

## 📊 Monitoreo

### Herramientas de Monitoreo

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### Health Checks

```bash
# Verificar salud de todos los servicios
make health

# Health checks individuales
curl http://localhost:8000/health  # API Gateway
curl http://localhost:8001/health  # Auth Service
curl http://localhost:8002/health  # Booking Service
curl http://localhost:8003/health  # Inventory Service
curl http://localhost:8004/health  # Payment Service
curl http://localhost:8005/health  # Notification Service
```

## 🔧 Comandos Make Útiles

```bash
# Ver todos los comandos disponibles
make help

# Levantar servicios
make up

# Ver logs
make logs

# Ejecutar tests
make test

# Crear backup
make backup

# Ver estado de servicios
make status

# Acceder al shell de un servicio
make shell SERVICE=auth-service

# Acceder a PostgreSQL
make shell-db
```

---

⭐ Sistema completo de microservicios para reservas de hotel con Docker, FastAPI y Streamlit!
