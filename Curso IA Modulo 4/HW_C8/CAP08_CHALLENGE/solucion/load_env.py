#!/usr/bin/env python3
"""
Script alternativo para cargar variables de entorno desde env_example.txt
Útil cuando no se puede crear el archivo .env
"""

import os
import re
from pathlib import Path

def load_env_from_example():
    """Carga variables de entorno desde env_example.txt"""
    
    print("🔧 Cargando variables de entorno desde env_example.txt...")
    
    # Verificar que existe env_example.txt
    env_file = Path("env_example.txt")
    if not env_file.exists():
        print("❌ Error: No se encontró env_example.txt")
        return False
    
    try:
        # Leer y parsear env_example.txt
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer variables de entorno
        env_vars = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
        
        # Cargar variables en el entorno
        for key, value in env_vars.items():
            if not os.getenv(key):  # Solo si no está ya definida
                os.environ[key] = value
                print(f"   ✅ {key} = {value[:20]}{'...' if len(value) > 20 else ''}")
        
        print(f"\n✅ {len(env_vars)} variables de entorno cargadas")
        return True
        
    except Exception as e:
        print(f"❌ Error cargando variables: {e}")
        return False

def verify_required_vars():
    """Verifica que las variables requeridas estén configuradas"""
    
    required_vars = [
        "SERPER_API_KEY",
        "GROQ_API_KEY"
    ]
    
    print("\n🔍 Verificando variables requeridas...")
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"   ✅ {var}: Configurada")
    
    if missing_vars:
        print(f"   ❌ Variables faltantes: {', '.join(missing_vars)}")
        return False
    
    print("   ✅ Todas las variables requeridas están configuradas")
    return True

def main():
    """Función principal"""
    
    print("🚀 Configurando entorno para el chatbot...")
    print("📁 Directorio de trabajo:", os.getcwd())
    
    # Cargar variables desde env_example.txt
    if not load_env_from_example():
        return 1
    
    # Verificar variables requeridas
    if not verify_required_vars():
        print("\n❌ Configuración incompleta")
        print("💡 Asegúrate de que env_example.txt contenga todas las variables necesarias")
        return 1
    
    print("\n🎉 Entorno configurado exitosamente!")
    print("\n🚀 Ahora puedes ejecutar:")
    print("   - Interfaz de consola: python src/orchestrator/main.py")
    print("   - Interfaz web: python run_web.py")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
