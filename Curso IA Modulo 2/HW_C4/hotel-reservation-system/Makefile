# Makefile para el Sistema de Reservas de Hotel
# Facilita la gestión del proyecto Docker

.PHONY: help build up down logs clean test migrate backup restore

# Variables
COMPOSE_FILE = docker-compose.yml
ENV_FILE = .env.docker
PROJECT_NAME = hotel-reservation-system

# Colores para output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Mostrar esta ayuda
	@echo "$(BLUE)Sistema de Reservas de Hotel - Comandos disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## Configuración inicial del proyecto
	@echo "$(YELLOW)Configurando el proyecto...$(NC)"
	@cp .env.example .env
	@echo "$(GREEN)✓ Archivo .env creado. Por favor configura las variables de entorno.$(NC)"
	@echo "$(YELLOW)Creando directorios necesarios...$(NC)"
	@mkdir -p logs uploads backups
	@echo "$(GREEN)✓ Directorios creados.$(NC)"

build: ## Construir todas las imágenes Docker
	@echo "$(YELLOW)Construyendo imágenes Docker...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) build
	@echo "$(GREEN)✓ Imágenes construidas exitosamente.$(NC)"

up: ## Levantar todos los servicios
	@echo "$(YELLOW)Iniciando servicios...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up -d
	@echo "$(GREEN)✓ Servicios iniciados.$(NC)"
	@echo "$(BLUE)Frontend disponible en: http://localhost:8501$(NC)"
	@echo "$(BLUE)API Gateway disponible en: http://localhost:8000$(NC)"
	@echo "$(BLUE)Nginx disponible en: http://localhost:80$(NC)"

up-build: ## Construir y levantar todos los servicios
	@echo "$(YELLOW)Construyendo y levantando servicios...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE) up -d --build
	@echo "$(GREEN)✓ Servicios construidos e iniciados.$(NC)"

down: ## Detener todos los servicios
	@echo "$(YELLOW)Deteniendo servicios...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✓ Servicios detenidos.$(NC)"

down-volumes: ## Detener servicios y eliminar volúmenes
	@echo "$(RED)⚠️  Esto eliminará todos los datos almacenados!$(NC)"
	@read -p "¿Estás seguro? (y/N): " confirm && [ "$$confirm" = "y" ]
	@docker-compose -f $(COMPOSE_FILE) down -v
	@echo "$(GREEN)✓ Servicios detenidos y volúmenes eliminados.$(NC)"

restart: ## Reiniciar todos los servicios
	@echo "$(YELLOW)Reiniciando servicios...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)✓ Servicios reiniciados.$(NC)"

logs: ## Ver logs de todos los servicios
	@docker-compose -f $(COMPOSE_FILE) logs -f

logs-service: ## Ver logs de un servicio específico (usar: make logs-service SERVICE=nombre)
	@docker-compose -f $(COMPOSE_FILE) logs -f $(SERVICE)

status: ## Ver estado de todos los servicios
	@echo "$(BLUE)Estado de los servicios:$(NC)"
	@docker-compose -f $(COMPOSE_FILE) ps

shell: ## Acceder al shell de un servicio (usar: make shell SERVICE=nombre)
	@docker-compose -f $(COMPOSE_FILE) exec $(SERVICE) /bin/bash

shell-db: ## Acceder al shell de PostgreSQL
	@docker-compose -f $(COMPOSE_FILE) exec postgres psql -U hotel_user -d hotel_reservations

migrate: ## Ejecutar migraciones de base de datos
	@echo "$(YELLOW)Ejecutando migraciones...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec auth-service alembic upgrade head
	@echo "$(GREEN)✓ Migraciones ejecutadas.$(NC)"

migrate-create: ## Crear nueva migración (usar: make migrate-create MESSAGE="descripción")
	@docker-compose -f $(COMPOSE_FILE) exec auth-service alembic revision --autogenerate -m "$(MESSAGE)"

test: ## Ejecutar tests
	@echo "$(YELLOW)Ejecutando tests...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec auth-service python -m pytest tests/ -v
	@docker-compose -f $(COMPOSE_FILE) exec booking-service python -m pytest tests/ -v
	@docker-compose -f $(COMPOSE_FILE) exec inventory-service python -m pytest tests/ -v
	@docker-compose -f $(COMPOSE_FILE) exec payment-service python -m pytest tests/ -v
	@docker-compose -f $(COMPOSE_FILE) exec notification-service python -m pytest tests/ -v
	@echo "$(GREEN)✓ Tests completados.$(NC)"

test-coverage: ## Ejecutar tests con coverage
	@echo "$(YELLOW)Ejecutando tests con coverage...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec auth-service python -m pytest tests/ --cov=. --cov-report=html
	@echo "$(GREEN)✓ Coverage generado en htmlcov/$(NC)"

lint: ## Ejecutar linting en el código
	@echo "$(YELLOW)Ejecutando linting...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec auth-service flake8 .
	@docker-compose -f $(COMPOSE_FILE) exec auth-service black --check .
	@echo "$(GREEN)✓ Linting completado.$(NC)"

format: ## Formatear código con black
	@echo "$(YELLOW)Formateando código...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec auth-service black .
	@docker-compose -f $(COMPOSE_FILE) exec booking-service black .
	@docker-compose -f $(COMPOSE_FILE) exec inventory-service black .
	@docker-compose -f $(COMPOSE_FILE) exec payment-service black .
	@docker-compose -f $(COMPOSE_FILE) exec notification-service black .
	@echo "$(GREEN)✓ Código formateado.$(NC)"

backup: ## Crear backup de la base de datos
	@echo "$(YELLOW)Creando backup...$(NC)"
	@mkdir -p backups
	@docker-compose -f $(COMPOSE_FILE) exec postgres pg_dump -U hotel_user hotel_reservations > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✓ Backup creado en backups/$(NC)"

restore: ## Restaurar backup (usar: make restore BACKUP=archivo.sql)
	@echo "$(RED)⚠️  Esto sobrescribirá la base de datos actual!$(NC)"
	@read -p "¿Estás seguro? (y/N): " confirm && [ "$$confirm" = "y" ]
	@docker-compose -f $(COMPOSE_FILE) exec -T postgres psql -U hotel_user -d hotel_reservations < backups/$(BACKUP)
	@echo "$(GREEN)✓ Backup restaurado.$(NC)"

monitoring: ## Abrir herramientas de monitoreo
	@echo "$(BLUE)Abriendo herramientas de monitoreo:$(NC)"
	@echo "$(BLUE)Prometheus: http://localhost:9090$(NC)"
	@echo "$(BLUE)Grafana: http://localhost:3000 (admin/admin)$(NC)"

clean: ## Limpiar contenedores, imágenes y volúmenes no utilizados
	@echo "$(YELLOW)Limpiando recursos Docker...$(NC)"
	@docker system prune -a -f
	@docker volume prune -f
	@echo "$(GREEN)✓ Limpieza completada.$(NC)"

clean-all: ## Limpiar todo (incluyendo volúmenes del proyecto)
	@echo "$(RED)⚠️  Esto eliminará TODOS los datos del proyecto!$(NC)"
	@read -p "¿Estás seguro? (y/N): " confirm && [ "$$confirm" = "y" ]
	@docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	@docker system prune -a -f
	@docker volume prune -f
	@echo "$(GREEN)✓ Limpieza completa realizada.$(NC)"

health: ## Verificar salud de todos los servicios
	@echo "$(BLUE)Verificando salud de los servicios:$(NC)"
	@curl -s http://localhost:8000/health | jq . || echo "API Gateway no disponible"
	@curl -s http://localhost:8001/health | jq . || echo "Auth Service no disponible"
	@curl -s http://localhost:8002/health | jq . || echo "Booking Service no disponible"
	@curl -s http://localhost:8003/health | jq . || echo "Inventory Service no disponible"
	@curl -s http://localhost:8004/health | jq . || echo "Payment Service no disponible"
	@curl -s http://localhost:8005/health | jq . || echo "Notification Service no disponible"

dev: ## Modo desarrollo (con hot reload)
	@echo "$(YELLOW)Iniciando en modo desarrollo...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) -f docker-compose.dev.yml --env-file $(ENV_FILE) up --build

prod: ## Modo producción
	@echo "$(YELLOW)Iniciando en modo producción...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) -f docker-compose.prod.yml --env-file .env up -d --build

install-deps: ## Instalar dependencias de desarrollo local
	@echo "$(YELLOW)Instalando dependencias locales...$(NC)"
	@pip install -r requirements-dev.txt
	@echo "$(GREEN)✓ Dependencias instaladas.$(NC)"

docs: ## Generar documentación
	@echo "$(YELLOW)Generando documentación...$(NC)"
	@docker-compose -f $(COMPOSE_FILE) exec auth-service python -m sphinx -b html docs docs/_build
	@echo "$(GREEN)✓ Documentación generada en docs/_build$(NC)"

scale: ## Escalar un servicio (usar: make scale SERVICE=nombre REPLICAS=3)
	@docker-compose -f $(COMPOSE_FILE) up -d --scale $(SERVICE)=$(REPLICAS)

# Comando por defecto
.DEFAULT_GOAL := help
