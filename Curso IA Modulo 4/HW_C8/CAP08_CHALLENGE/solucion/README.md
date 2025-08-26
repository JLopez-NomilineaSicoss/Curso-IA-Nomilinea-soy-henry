# Chatbot de IA Conversacional con Capacidad de Búsqueda en Internet

## Descripción del Proyecto

Este proyecto implementa un **Chatbot de IA Conversacional con Capacidad de Búsqueda en Internet** que opera a través de consola y proporciona respuestas en streaming basadas en información extraída de la web en tiempo real.

### **Características Principales**
- 🔍 **Búsqueda Web en Tiempo Real**: Usa Serper.dev API para búsquedas de Google
- 🤖 **LLM Gratuito**: Integra Groq Cloud con modelos Llama3 y Mixtral
- 📡 **Streaming de Respuestas**: Tokens se muestran conforme se generan
- 🌐 **Web Scraping Inteligente**: Extrae contenido de hasta 5 páginas relevantes
- 📚 **Citación de Fuentes**: Incluye referencias automáticas al final de cada respuesta
- 🚀 **Arquitectura Modular**: Fácil extensión y mantenimiento

### **APIs Utilizadas**
- **Serper.dev**: Búsqueda web gratuita (con créditos incluidos)
- **Groq Cloud**: LLM gratuito con modelos de alta calidad
- **OpenAI Embeddings**: Para similitud semántica

## Primeros Pasos

Sigue estos pasos para ejecutar el chatbot localmente en tu máquina:

1. **Configura tu Entorno**:

    - **Opción A: Automática (recomendada)**
      ```bash
      python setup_env.py
      ```
    
    - **Opción B: Carga directa**
      ```bash
      python load_env.py
      ```
    
    - **Opción C: Manual**
      - Crea un archivo `.env` copiando `env_example.txt`
      - Las API keys ya están configuradas en el ejemplo
    
    - **Instalar dependencias:**
      ```bash
      pipenv shell
      pip install -r src/orchestrator/requirements.txt
      ```

2. **Construye y Ejecuta la Aplicación**:

    - **Interfaz de Consola:**
      ```bash
      python src/orchestrator/main.py
      ```
    
    - **Interfaz Web:**
      ```bash
      python run_web.py
      ```
      Luego abre tu navegador en: http://localhost:8000
    
    - **Comienza a chatear** usando cualquiera de las dos interfaces

## **Ejemplo de Uso**

```
> Enter your question: ¿Cómo puedo plantar un árbol de manzanas?

** Búsqueda en internet **
Link: https://gardeningknowhow.com/apple-tree
Link: https://wikihow.com/plant-apple-trees
Link: https://plantingtutorial.com/apple-trees

Según la información encontrada, el mejor momento para plantar árboles de manzana es al inicio de la primavera...

Referencias:
- [GardeningKnowHow](https://gardeningknowhow.com/apple-tree)
- [WikiHow](https://wikihow.com/plant-apple-trees)
- [PlantingTutorial](https://plantingtutorial.com/apple-trees)
```

## **Características del Sistema**

- **🔍 Búsqueda Web Inteligente**: Usa Serper.dev para búsquedas de Google
- **🤖 LLM Gratuito**: Groq Cloud con modelos Llama3 y Mixtral
- **📡 Streaming en Tiempo Real**: Respuestas token por token
- **🌐 Web Scraping**: Extrae contenido de hasta 5 páginas relevantes
- **📚 Citación Automática**: Incluye referencias al final de cada respuesta
- **🚀 Arquitectura Modular**: Fácil extensión y mantenimiento
- **💾 Memoria de Conversación**: Mantiene contexto entre mensajes
- **⚙️ Preferencias Configurables**: Ajusta búsqueda, LLM y streaming
- **🌐 Interfaz Web Moderna**: Chat en tiempo real con FastAPI
- **📱 Diseño Responsive**: Funciona en móviles y desktop

## **Documentación Técnica**

Para información detallada sobre la arquitectura, tecnologías y operación del sistema, consulta:
- [DOCUMENTACION_TECNICA.md](DOCUMENTACION_TECNICA.md) - Documentación técnica completa
- [challenge.md](../challenge.md) - Requerimientos y progreso del proyecto
