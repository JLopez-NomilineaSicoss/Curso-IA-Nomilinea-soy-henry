#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas unitarias del sistema
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_section(title):
    """Imprime una sección formateada"""
    print(f"\n📋 {title}")
    print("-" * 40)

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔄 {description}")
    print(f"💻 Comando: {command}")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=os.getcwd()
        )
        end_time = time.time()
        
        if result.returncode == 0:
            print(f"✅ Éxito en {end_time - start_time:.2f}s")
            if result.stdout.strip():
                print("📤 Salida:")
                print(result.stdout.strip())
        else:
            print(f"❌ Falló en {end_time - start_time:.2f}s")
            print("📤 Salida estándar:")
            print(result.stdout.strip())
            print("📤 Salida de error:")
            print(result.stderr.strip())
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print_header("Verificación de Dependencias")
    
    dependencies = [
        ("pytest", "Framework de pruebas"),
        ("fastapi", "Framework web"),
        ("uvicorn", "Servidor ASGI"),
        ("aiohttp", "Cliente HTTP asíncrono"),
        ("python-dotenv", "Variables de entorno")
    ]
    
    missing_deps = []
    
    for dep, description in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✅ {dep}: {description}")
        except ImportError:
            print(f"❌ {dep}: {description} - NO INSTALADO")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n⚠️  Dependencias faltantes: {', '.join(missing_deps)}")
        print("💡 Instala con: pip install -r src/orchestrator/requirements.txt")
        return False
    
    return True

def run_unit_tests():
    """Ejecuta las pruebas unitarias individuales"""
    print_header("Pruebas Unitarias Individuales")
    
    test_files = [
        ("tests/test_serper_search.py", "Módulo de Búsqueda (Serper)"),
        ("tests/test_groq_client.py", "Cliente LLM (Groq)"),
        ("tests/test_conversation_memory.py", "Sistema de Memoria"),
        ("tests/test_source_formatter.py", "Formateo de Fuentes"),
        ("tests/test_user_preferences.py", "Preferencias del Usuario"),
        ("tests/test_web_api.py", "API Web"),
        ("tests/test_main.py", "Módulo Principal")
    ]
    
    results = {}
    
    for test_file, description in test_files:
        if os.path.exists(test_file):
            print_section(description)
            success = run_command(
                f"python -m pytest {test_file} -v",
                f"Ejecutando {test_file}"
            )
            results[test_file] = success
        else:
            print(f"⚠️  Archivo no encontrado: {test_file}")
            results[test_file] = False
    
    return results

def run_integration_tests():
    """Ejecuta las pruebas de integración"""
    print_header("Pruebas de Integración")
    
    if os.path.exists("tests/test_integration.py"):
        return run_command(
            "python -m pytest tests/test_integration.py -v",
            "Ejecutando pruebas de integración"
        )
    else:
        print("⚠️  Archivo de pruebas de integración no encontrado")
        return False

def run_all_tests():
    """Ejecuta todas las pruebas juntas"""
    print_header("Ejecutando Todas las Pruebas")
    
    return run_command(
        "python -m pytest tests/ -v --tb=short",
        "Ejecutando todas las pruebas del sistema"
    )

def generate_test_report(results):
    """Genera un reporte de las pruebas"""
    print_header("Reporte de Pruebas")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    failed_tests = total_tests - passed_tests
    
    print(f"📊 Total de módulos probados: {total_tests}")
    print(f"✅ Pruebas exitosas: {passed_tests}")
    print(f"❌ Pruebas fallidas: {failed_tests}")
    print(f"📈 Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ Módulos con problemas:")
        for test_file, success in results.items():
            if not success:
                print(f"   - {test_file}")
    
    return passed_tests == total_tests

def main():
    """Función principal"""
    print("🚀 Iniciando Suite de Pruebas del Chatbot")
    print("📁 Directorio de trabajo:", os.getcwd())
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("src") or not os.path.exists("tests"):
        print("❌ Error: Debes estar en el directorio 'solucion'")
        print("💡 Ejecuta: cd solucion")
        return 1
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ Dependencias faltantes. Instala antes de continuar.")
        return 1
    
    # Ejecutar pruebas unitarias
    unit_results = run_unit_tests()
    
    # Ejecutar pruebas de integración
    integration_success = run_integration_tests()
    
    # Ejecutar todas las pruebas juntas
    all_tests_success = run_all_tests()
    
    # Generar reporte
    all_results = {**unit_results, "integration": integration_success, "all_together": all_tests_success}
    overall_success = generate_test_report(all_results)
    
    # Resumen final
    print_header("Resumen Final")
    if overall_success:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("✅ El sistema está funcionando correctamente")
        print("\n🚀 Próximos pasos:")
        print("   1. Configura el entorno: python setup_env.py")
        print("   2. Ejecuta interfaz consola: python src/orchestrator/main.py")
        print("   3. Ejecuta interfaz web: python run_web.py")
    else:
        print("⚠️  Algunas pruebas fallaron")
        print("🔧 Revisa los errores y corrige los problemas")
        print("💡 Ejecuta pruebas individuales para más detalles")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
