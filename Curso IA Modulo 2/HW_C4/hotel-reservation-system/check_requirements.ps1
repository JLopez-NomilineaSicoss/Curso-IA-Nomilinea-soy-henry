# Script para verificar prerrequisitos del sistema
# Ejecutar en PowerShell: .\check_requirements.ps1

Write-Host "🔍 Verificando prerrequisitos del Sistema de Reservas de Hotel..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Verificar Docker
Write-Host "`n📦 Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker instalado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está instalado o no está en PATH" -ForegroundColor Red
    Write-Host "💡 Instalar desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Blue
}

# Verificar Docker Compose
Write-Host "`n🐳 Verificando Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose instalado: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose no está instalado" -ForegroundColor Red
    Write-Host "💡 Instalar con Docker Desktop o por separado" -ForegroundColor Blue
}

# Verificar que Docker esté ejecutándose
Write-Host "`n🔄 Verificando que Docker esté ejecutándose..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker daemon está ejecutándose" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker daemon no está ejecutándose" -ForegroundColor Red
        Write-Host "💡 Iniciar Docker Desktop" -ForegroundColor Blue
    }
} catch {
    Write-Host "❌ No se puede conectar al Docker daemon" -ForegroundColor Red
}

# Verificar Git
Write-Host "`n📂 Verificando Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git instalado: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git no está instalado" -ForegroundColor Red
    Write-Host "💡 Instalar desde: https://git-scm.com/download/win" -ForegroundColor Blue
}

# Verificar Python (opcional)
Write-Host "`n🐍 Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python instalado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Python no está instalado (opcional para desarrollo)" -ForegroundColor Orange
    Write-Host "💡 Instalar desde: https://www.python.org/downloads/" -ForegroundColor Blue
}

# Verificar Make (opcional)
Write-Host "`n🔨 Verificando Make..." -ForegroundColor Yellow
try {
    $makeVersion = make --version
    Write-Host "✅ Make instalado: $makeVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Make no está instalado (opcional, facilita comandos)" -ForegroundColor Orange
    Write-Host "💡 Instalar con: choco install make (requiere Chocolatey)" -ForegroundColor Blue
}

# Verificar puertos disponibles
Write-Host "`n🔌 Verificando puertos requeridos..." -ForegroundColor Yellow
$requiredPorts = @(80, 5432, 6379, 8000, 8001, 8002, 8003, 8004, 8005, 8501, 9090, 3000)
$portsInUse = @()

foreach ($port in $requiredPorts) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $portsInUse += $port
    }
}

if ($portsInUse.Count -eq 0) {
    Write-Host "✅ Todos los puertos requeridos están disponibles" -ForegroundColor Green
} else {
    Write-Host "⚠️ Los siguientes puertos están en uso: $($portsInUse -join ', ')" -ForegroundColor Orange
    Write-Host "💡 Detener servicios que usen estos puertos o cambiar configuración" -ForegroundColor Blue
}

# Verificar espacio en disco
Write-Host "`n💾 Verificando espacio en disco..." -ForegroundColor Yellow
$disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
$freeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 2)

if ($freeSpaceGB -gt 5) {
    Write-Host "✅ Espacio disponible: $freeSpaceGB GB" -ForegroundColor Green
} else {
    Write-Host "⚠️ Poco espacio disponible: $freeSpaceGB GB" -ForegroundColor Orange
    Write-Host "💡 Se recomienda al menos 5GB libres" -ForegroundColor Blue
}

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "🎯 Verificación completada" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
