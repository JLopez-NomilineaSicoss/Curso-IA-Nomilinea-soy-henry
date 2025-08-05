# GUÍA DE EJECUCIÓN MANUAL - Sistema de Reservas de Hotel
# =========================================================

Write-Host "🏨 Sistema de Reservas de Hotel - Guía de Ejecución" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Verificar Docker
Write-Host "`n1️⃣ Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
    
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose: $composeVersion" -ForegroundColor Green
    
    # Verificar que Docker esté ejecutándose
    docker info | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker daemon ejecutándose" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker daemon no está ejecutándose. Inicia Docker Desktop." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Docker no está instalado o no está en PATH" -ForegroundColor Red
    Write-Host "💡 Instalar Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Blue
    exit 1
}

# 2. Verificar directorio
Write-Host "`n2️⃣ Verificando directorio del proyecto..." -ForegroundColor Yellow
if (Test-Path "docker-compose.yml") {
    Write-Host "✅ Directorio correcto encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ No estás en el directorio del proyecto" -ForegroundColor Red
    Write-Host "💡 Navega a: C:\Users\JoséEmmanuelLópezJim\Downloads\HW_C4\hotel-reservation-system" -ForegroundColor Blue
    exit 1
}

# 3. Configurar archivo .env
Write-Host "`n3️⃣ Configurando archivo .env..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Archivo .env creado desde .env.example" -ForegroundColor Green
    } else {
        Write-Host "❌ Archivo .env.example no encontrado" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Archivo .env ya existe" -ForegroundColor Green
}

# 4. Construir imágenes
Write-Host "`n4️⃣ Construyendo imágenes Docker..." -ForegroundColor Yellow
Write-Host "⏳ Esto puede tomar varios minutos la primera vez..." -ForegroundColor Cyan
docker-compose build
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Imágenes construidas exitosamente" -ForegroundColor Green
} else {
    Write-Host "❌ Error construyendo imágenes" -ForegroundColor Red
    exit 1
}

# 5. Levantar servicios
Write-Host "`n5️⃣ Levantando servicios..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Servicios iniciados" -ForegroundColor Green
} else {
    Write-Host "❌ Error iniciando servicios" -ForegroundColor Red
    Write-Host "💡 Verifica que los puertos no estén ocupados" -ForegroundColor Blue
    exit 1
}

# 6. Esperar servicios
Write-Host "`n6️⃣ Esperando que los servicios estén listos..." -ForegroundColor Yellow
Write-Host "⏳ Esperando 30 segundos..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# 7. Verificar estado
Write-Host "`n7️⃣ Verificando estado de servicios..." -ForegroundColor Yellow
docker-compose ps

# 8. Mostrar URLs
Write-Host "`n🎉 ¡Sistema listo! URLs de acceso:" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "🌐 Frontend Web:    http://localhost:8501" -ForegroundColor Blue
Write-Host "🔧 API Gateway:     http://localhost:8000" -ForegroundColor Blue
Write-Host "📚 API Docs:        http://localhost:8000/docs" -ForegroundColor Blue
Write-Host "⚖️ Load Balancer:   http://localhost:80" -ForegroundColor Blue
Write-Host "📊 Prometheus:      http://localhost:9090" -ForegroundColor Blue
Write-Host "📈 Grafana:         http://localhost:3000" -ForegroundColor Blue
Write-Host "======================================" -ForegroundColor Green

# 9. Usuarios de prueba
Write-Host "`n👥 Usuarios de prueba:" -ForegroundColor Yellow
Write-Host "Admin:     admin@hotel.com / admin123" -ForegroundColor White
Write-Host "Manager:   manager@hotel.com / manager123" -ForegroundColor White
Write-Host "Guest:     guest@hotel.com / guest123" -ForegroundColor White

Write-Host "`n✨ El sistema está ejecutándose exitosamente!" -ForegroundColor Green
Write-Host "💡 Para detener: docker-compose down" -ForegroundColor Blue
