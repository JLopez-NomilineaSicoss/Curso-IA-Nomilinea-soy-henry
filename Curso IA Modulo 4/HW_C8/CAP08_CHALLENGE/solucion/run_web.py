#!/usr/bin/env python3
"""
Script para ejecutar la interfaz web del chatbot
"""

import os
import sys
import uvicorn
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Función principal para ejecutar la interfaz web"""
    
    print("🚀 Iniciando Chatbot Web...")
    print("📁 Directorio de trabajo:", os.getcwd())
    print("🔧 Verificando dependencias...")
    
    try:
        # Verificar que existan las variables de entorno necesarias
        required_vars = ["SERPER_API_KEY", "GROQ_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
            print("💡 Asegúrate de tener un archivo .env con las API keys necesarias")
            print("📋 Ejecuta 'python setup_env.py' para crear el archivo .env")
            return 1
        
        print("✅ Variables de entorno verificadas")
        
        # Verificar que existan los módulos necesarios
        try:
            from web.api import app
            print("✅ Módulos web cargados correctamente")
        except ImportError as e:
            print(f"❌ Error importando módulos web: {e}")
            print("💡 Asegúrate de estar en el directorio correcto")
            return 1
        
        # Configurar y ejecutar el servidor
        host = os.getenv("WEB_HOST", "0.0.0.0")
        port = int(os.getenv("WEB_PORT", "8000"))
        
        print(f"🌐 Iniciando servidor en http://{host}:{port}")
        print("📱 Abre tu navegador y ve a la URL mostrada arriba")
        print("🛑 Presiona Ctrl+C para detener el servidor")
        print()
        
        # Ejecutar el servidor
        uvicorn.run(
            "web.api:app",
            host=host,
            port=port,
            reload=True,  # Recargar automáticamente en desarrollo
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido por el usuario")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error ejecutando la interfaz web: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
