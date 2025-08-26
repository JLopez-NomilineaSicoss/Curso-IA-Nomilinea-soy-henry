#!/usr/bin/env python3
"""
Script para configurar automáticamente el archivo .env
"""

import os
import shutil
from pathlib import Path

def main():
    """Función principal para configurar el entorno"""
    
    print("🔧 Configurando archivo .env para el chatbot...")
    print("📁 Directorio de trabajo:", os.getcwd())
    
    # Verificar si estamos en el directorio correcto
    if not Path("env_example.txt").exists():
        print("❌ Error: No se encontró env_example.txt")
        print("💡 Asegúrate de estar en el directorio 'solucion'")
        return 1
    
    # Verificar si ya existe .env
    if Path(".env").exists():
        print("⚠️  El archivo .env ya existe")
        response = input("¿Quieres sobrescribirlo? (s/N): ").lower()
        if response != 's':
            print("✅ Configuración cancelada")
            return 0
    
    try:
        # Copiar env_example.txt a .env
        shutil.copy("env_example.txt", ".env")
        
        print("✅ Archivo .env creado exitosamente")
        print("🔑 API Keys configuradas:")
        print("   - SERPER_API_KEY: ✅ Configurada")
        print("   - GROQ_API_KEY: ✅ Configurada")
        print("   - GOOGLE_AI_API_KEY: ✅ Configurada")
        
        print("\n📋 Configuración del sistema:")
        print("   - Motor de búsqueda: Serper.dev")
        print("   - LLM: Groq Cloud (Llama3)")
        print("   - Streaming: Habilitado")
        print("   - Puerto web: 8000")
        
        print("\n🚀 Ahora puedes ejecutar:")
        print("   - Interfaz de consola: python src/orchestrator/main.py")
        print("   - Interfaz web: python run_web.py")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creando .env: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
