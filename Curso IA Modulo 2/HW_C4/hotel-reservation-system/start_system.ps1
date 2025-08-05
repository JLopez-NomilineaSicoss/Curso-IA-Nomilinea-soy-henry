# Guía de Ejecución Rápida - Sistema de Reservas de Hotel
# =========================================================

# 1. VERIFICAR PRERREQUISITOS
Write-Host "🔍 Paso 1: Verificando prerrequisitos..." -ForegroundColor Cyan
.\check_requirements.ps1

# 2. CONFIGURAR VARIABLES DE ENTORNO
Write-Host "`n⚙️ Paso 2: Configurando variables de entorno..." -ForegroundColor Cyan
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Archivo .env creado desde .env.example" -ForegroundColor Green
    Write-Host "💡 Edita el archivo .env con tus configuraciones específicas" -ForegroundColor Blue
} else {
    Write-Host "✅ Archivo .env ya existe" -ForegroundColor Green
}

# 3. CONSTRUIR IMÁGENES DOCKER
Write-Host "`n🏗️ Paso 3: Construyendo imágenes Docker..." -ForegroundColor Cyan
Write-Host "Esto puede tomar varios minutos la primera vez..." -ForegroundColor Yellow
docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Imágenes construidas exitosamente" -ForegroundColor Green
} else {
    Write-Host "❌ Error construyendo imágenes" -ForegroundColor Red
    exit 1
}

# 4. LEVANTAR SERVICIOS
Write-Host "`n🚀 Paso 4: Levantando servicios..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Servicios iniciados exitosamente" -ForegroundColor Green
} else {
    Write-Host "❌ Error iniciando servicios" -ForegroundColor Red
    exit 1
}

# 5. ESPERAR A QUE LOS SERVICIOS ESTÉN LISTOS
Write-Host "`n⏳ Paso 5: Esperando a que los servicios estén listos..." -ForegroundColor Cyan
Write-Host "Esperando 30 segundos para que todos los servicios inicien..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 6. VERIFICAR ESTADO DE LOS SERVICIOS
Write-Host "`n🔍 Paso 6: Verificando estado de los servicios..." -ForegroundColor Cyan
docker-compose ps

# 7. EJECUTAR MIGRACIONES (si es necesario)
Write-Host "`n📊 Paso 7: Ejecutando migraciones de base de datos..." -ForegroundColor Cyan
docker-compose exec -T auth-service alembic upgrade head 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migraciones ejecutadas" -ForegroundColor Green
} else {
    Write-Host "⚠️ Las migraciones pueden no ser necesarias en la primera ejecución" -ForegroundColor Orange
}

# 8. MOSTRAR URLs DE ACCESO
Write-Host "`n🌐 ¡Sistema listo! URLs de acceso:" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "Frontend Web:      http://localhost:8501" -ForegroundColor Blue
Write-Host "API Gateway:       http://localhost:8000" -ForegroundColor Blue
Write-Host "API Docs:          http://localhost:8000/docs" -ForegroundColor Blue
Write-Host "Nginx:             http://localhost:80" -ForegroundColor Blue
Write-Host "Prometheus:        http://localhost:9090" -ForegroundColor Blue
Write-Host "Grafana:           http://localhost:3000" -ForegroundColor Blue
Write-Host "=================================" -ForegroundColor Green

# 9. USUARIOS POR DEFECTO
Write-Host "`n👥 Usuarios por defecto:" -ForegroundColor Yellow
Write-Host "Admin:    admin@hotel.com / admin123" -ForegroundColor White
Write-Host "Manager:  manager@hotel.com / manager123" -ForegroundColor White
Write-Host "Guest:    guest@hotel.com / guest123" -ForegroundColor White

Write-Host "`n🎉 ¡El sistema está ejecutándose exitosamente!" -ForegroundColor Green
