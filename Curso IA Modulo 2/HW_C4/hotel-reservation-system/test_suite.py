#!/usr/bin/env python3
"""
Script de pruebas completas para el Sistema de Reservas de Hotel
Ejecuta tests de todos los microservicios y genera reportes
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, Any, List

# Configuración de pruebas
BASE_URL = "http://localhost:8000"
SERVICES = {
    "auth": "http://localhost:8001",
    "booking": "http://localhost:8002", 
    "inventory": "http://localhost:8003",
    "payment": "http://localhost:8004",
    "notification": "http://localhost:8005",
    "gateway": "http://localhost:8000"
}

class TestRunner:
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_service_health(self, service_name: str, url: str) -> bool:
        """Prueba el health check de un servicio"""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                self.log(f"✅ {service_name} service health check passed")
                return True
            else:
                self.log(f"❌ {service_name} service health check failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ {service_name} service health check failed: {str(e)}", "ERROR")
            return False
            
    def test_all_health_checks(self):
        """Ejecuta health checks para todos los servicios"""
        self.log("🔍 Ejecutando health checks para todos los servicios...")
        health_results = {}
        
        for service_name, url in SERVICES.items():
            health_results[service_name] = self.test_service_health(service_name, url)
            time.sleep(1)  # Esperar entre requests
            
        self.results["health_checks"] = health_results
        return all(health_results.values())
        
    def test_auth_flow(self) -> bool:
        """Prueba el flujo completo de autenticación"""
        self.log("🔐 Probando flujo de autenticación...")
        
        try:
            # 1. Registro de usuario
            register_data = {
                "email": f"test_{int(time.time())}@test.com",
                "password": "testpassword123",
                "first_name": "Test",
                "last_name": "User",
                "phone": "+1234567890"
            }
            
            register_response = requests.post(
                f"{SERVICES['auth']}/auth/register",
                json=register_data,
                timeout=10
            )
            
            if register_response.status_code != 201:
                self.log(f"❌ Registro falló: {register_response.status_code}", "ERROR")
                return False
                
            # 2. Login
            login_data = {
                "email": register_data["email"],
                "password": register_data["password"]
            }
            
            login_response = requests.post(
                f"{SERVICES['auth']}/auth/login",
                data=login_data,  # Form data para login
                timeout=10
            )
            
            if login_response.status_code != 200:
                self.log(f"❌ Login falló: {login_response.status_code}", "ERROR")
                return False
                
            login_result = login_response.json()
            access_token = login_result.get("access_token")
            
            if not access_token:
                self.log("❌ No se recibió access token", "ERROR")
                return False
                
            # 3. Verificar perfil
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(
                f"{SERVICES['auth']}/auth/profile",
                headers=headers,
                timeout=10
            )
            
            if profile_response.status_code != 200:
                self.log(f"❌ Obtener perfil falló: {profile_response.status_code}", "ERROR")
                return False
                
            self.log("✅ Flujo de autenticación exitoso")
            self.results["auth_token"] = access_token
            return True
            
        except Exception as e:
            self.log(f"❌ Error en flujo de autenticación: {str(e)}", "ERROR")
            return False
            
    def test_inventory_operations(self) -> bool:
        """Prueba operaciones del servicio de inventario"""
        self.log("🏨 Probando operaciones de inventario...")
        
        try:
            # Obtener token de auth
            auth_token = self.results.get("auth_token")
            if not auth_token:
                self.log("❌ Token de autenticación no disponible", "ERROR")
                return False
                
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            # 1. Crear hotel
            hotel_data = {
                "name": f"Test Hotel {int(time.time())}",
                "description": "Hotel de prueba",
                "address": "123 Test Street",
                "city": "Test City",
                "country": "Test Country",
                "phone": "+1234567890",
                "email": "test@testhotel.com",
                "amenities": ["wifi", "parking", "pool"]
            }
            
            hotel_response = requests.post(
                f"{SERVICES['inventory']}/hotels",
                json=hotel_data,
                headers=headers,
                timeout=10
            )
            
            if hotel_response.status_code != 201:
                self.log(f"❌ Crear hotel falló: {hotel_response.status_code}", "ERROR")
                return False
                
            hotel_result = hotel_response.json()
            hotel_id = hotel_result.get("id")
            
            # 2. Crear habitación
            room_data = {
                "hotel_id": hotel_id,
                "room_number": "101",
                "room_type": "deluxe",
                "capacity": 2,
                "price_per_night": 150.0,
                "description": "Habitación de prueba",
                "amenities": ["tv", "minibar", "balcony"]
            }
            
            room_response = requests.post(
                f"{SERVICES['inventory']}/rooms",
                json=room_data,
                headers=headers,
                timeout=10
            )
            
            if room_response.status_code != 201:
                self.log(f"❌ Crear habitación falló: {room_response.status_code}", "ERROR")
                return False
                
            # 3. Buscar habitaciones
            search_response = requests.get(
                f"{SERVICES['inventory']}/rooms/search?city=Test City&capacity=2",
                headers=headers,
                timeout=10
            )
            
            if search_response.status_code != 200:
                self.log(f"❌ Buscar habitaciones falló: {search_response.status_code}", "ERROR")
                return False
                
            self.log("✅ Operaciones de inventario exitosas")
            self.results["test_hotel_id"] = hotel_id
            return True
            
        except Exception as e:
            self.log(f"❌ Error en operaciones de inventario: {str(e)}", "ERROR")
            return False
            
    def test_booking_flow(self) -> bool:
        """Prueba el flujo completo de reservas"""
        self.log("📅 Probando flujo de reservas...")
        
        try:
            auth_token = self.results.get("auth_token")
            hotel_id = self.results.get("test_hotel_id")
            
            if not auth_token or not hotel_id:
                self.log("❌ Prerequisitos no disponibles para test de reservas", "ERROR")
                return False
                
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            # 1. Crear reserva
            booking_data = {
                "hotel_id": hotel_id,
                "room_type": "deluxe",
                "check_in": "2024-06-01",
                "check_out": "2024-06-05",
                "guests": 2,
                "special_requests": "Vista al mar"
            }
            
            booking_response = requests.post(
                f"{SERVICES['booking']}/reservations",
                json=booking_data,
                headers=headers,
                timeout=10
            )
            
            if booking_response.status_code != 201:
                self.log(f"❌ Crear reserva falló: {booking_response.status_code}", "ERROR")
                return False
                
            booking_result = booking_response.json()
            reservation_id = booking_result.get("id")
            
            # 2. Obtener reserva
            get_response = requests.get(
                f"{SERVICES['booking']}/reservations/{reservation_id}",
                headers=headers,
                timeout=10
            )
            
            if get_response.status_code != 200:
                self.log(f"❌ Obtener reserva falló: {get_response.status_code}", "ERROR")
                return False
                
            self.log("✅ Flujo de reservas exitoso")
            self.results["test_reservation_id"] = reservation_id
            return True
            
        except Exception as e:
            self.log(f"❌ Error en flujo de reservas: {str(e)}", "ERROR")
            return False
            
    def test_payment_simulation(self) -> bool:
        """Prueba simulación de pagos"""
        self.log("💳 Probando simulación de pagos...")
        
        try:
            auth_token = self.results.get("auth_token")
            reservation_id = self.results.get("test_reservation_id")
            
            if not auth_token or not reservation_id:
                self.log("❌ Prerequisitos no disponibles para test de pagos", "ERROR")
                return False
                
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            # Simular pago
            payment_data = {
                "reservation_id": reservation_id,
                "amount": 600.0,
                "payment_method": "stripe",
                "payment_details": {
                    "card_number": "4242424242424242",
                    "exp_month": "12",
                    "exp_year": "2025",
                    "cvc": "123"
                }
            }
            
            payment_response = requests.post(
                f"{SERVICES['payment']}/payments",
                json=payment_data,
                headers=headers,
                timeout=10
            )
            
            if payment_response.status_code != 201:
                self.log(f"❌ Procesar pago falló: {payment_response.status_code}", "ERROR")
                return False
                
            self.log("✅ Simulación de pagos exitosa")
            return True
            
        except Exception as e:
            self.log(f"❌ Error en simulación de pagos: {str(e)}", "ERROR")
            return False
            
    def test_notification_service(self) -> bool:
        """Prueba el servicio de notificaciones"""
        self.log("📧 Probando servicio de notificaciones...")
        
        try:
            auth_token = self.results.get("auth_token")
            if not auth_token:
                self.log("❌ Token de autenticación no disponible", "ERROR")
                return False
                
            headers = {"Authorization": f"Bearer {auth_token}"}
            
            # Enviar notificación de prueba
            notification_data = {
                "type": "email",
                "recipient": "test@example.com",
                "subject": "Prueba de Sistema",
                "message": "Este es un mensaje de prueba del sistema de notificaciones"
            }
            
            notification_response = requests.post(
                f"{SERVICES['notification']}/notifications/email",
                json=notification_data,
                headers=headers,
                timeout=10
            )
            
            # Nota: Puede fallar si no están configuradas las credenciales SMTP
            # Pero el servicio debe responder
            if notification_response.status_code in [200, 201, 422]:  # 422 por credenciales faltantes
                self.log("✅ Servicio de notificaciones responde correctamente")
                return True
            else:
                self.log(f"❌ Servicio de notificaciones falló: {notification_response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error en servicio de notificaciones: {str(e)}", "ERROR")
            return False
            
    def run_docker_tests(self) -> bool:
        """Ejecuta tests unitarios dentro de los contenedores"""
        self.log("🐳 Ejecutando tests unitarios en contenedores...")
        
        services_to_test = ["auth-service", "booking-service", "inventory-service"]
        all_passed = True
        
        for service in services_to_test:
            try:
                self.log(f"Ejecutando tests para {service}...")
                result = subprocess.run(
                    ["docker-compose", "exec", "-T", service, "python", "-m", "pytest", "tests/", "-v"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    self.log(f"✅ Tests de {service} pasaron")
                else:
                    self.log(f"❌ Tests de {service} fallaron", "ERROR")
                    all_passed = False
                    
            except subprocess.TimeoutExpired:
                self.log(f"❌ Tests de {service} timeout", "ERROR")
                all_passed = False
            except Exception as e:
                self.log(f"❌ Error ejecutando tests de {service}: {str(e)}", "ERROR")
                all_passed = False
                
        return all_passed
        
    def generate_report(self):
        """Genera reporte de resultados de tests"""
        self.log("📊 Generando reporte de tests...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": round((self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0, 2)
            },
            "results": self.results
        }
        
        # Guardar reporte en archivo
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        self.log(f"📄 Reporte guardado en test_report.json")
        
        # Mostrar resumen
        print("\n" + "="*50)
        print("📊 RESUMEN DE TESTS")
        print("="*50)
        print(f"Total de tests: {self.total_tests}")
        print(f"Tests exitosos: {self.passed_tests}")
        print(f"Tests fallidos: {self.failed_tests}")
        print(f"Tasa de éxito: {report['summary']['success_rate']}%")
        print("="*50)
        
    def run_all_tests(self):
        """Ejecuta todos los tests del sistema"""
        self.log("🚀 Iniciando suite completa de tests...")
        
        tests = [
            ("Health Checks", self.test_all_health_checks),
            ("Auth Flow", self.test_auth_flow),
            ("Inventory Operations", self.test_inventory_operations),
            ("Booking Flow", self.test_booking_flow),
            ("Payment Simulation", self.test_payment_simulation),
            ("Notification Service", self.test_notification_service),
            ("Docker Unit Tests", self.run_docker_tests)
        ]
        
        for test_name, test_func in tests:
            self.total_tests += 1
            self.log(f"🔄 Ejecutando: {test_name}")
            
            try:
                if test_func():
                    self.passed_tests += 1
                    self.log(f"✅ {test_name} - EXITOSO")
                else:
                    self.failed_tests += 1
                    self.log(f"❌ {test_name} - FALLIDO", "ERROR")
            except Exception as e:
                self.failed_tests += 1
                self.log(f"❌ {test_name} - ERROR: {str(e)}", "ERROR")
                
            time.sleep(2)  # Pausa entre tests
            
        self.generate_report()

if __name__ == "__main__":
    print("🏨 Sistema de Reservas de Hotel - Test Suite")
    print("=" * 50)
    
    # Verificar que Docker Compose esté ejecutándose
    try:
        result = subprocess.run(["docker-compose", "ps"], capture_output=True, text=True)
        if "Up" not in result.stdout:
            print("❌ Error: Los servicios Docker no están ejecutándose.")
            print("💡 Ejecuta: docker-compose up -d")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error verificando Docker: {str(e)}")
        sys.exit(1)
        
    # Esperar a que los servicios estén listos
    print("⏳ Esperando a que los servicios estén listos...")
    time.sleep(10)
    
    # Ejecutar tests
    runner = TestRunner()
    runner.run_all_tests()
    
    # Exit code basado en los resultados
    if runner.failed_tests == 0:
        print("🎉 ¡Todos los tests pasaron exitosamente!")
        sys.exit(0)
    else:
        print(f"💥 {runner.failed_tests} tests fallaron.")
        sys.exit(1)
