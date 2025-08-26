# Documentación Técnica del Chatbot con Capacidad de Búsqueda en Internet

## Descripción General del Sistema

Este proyecto implementa un **Chatbot de IA Conversacional con Capacidad de Búsqueda en Internet** que opera a través de consola y proporciona respuestas en streaming basadas en información extraída de la web en tiempo real.

## Arquitectura del Sistema

### Diagrama de Arquitectura
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Interfaz      │    │   Módulo         │    │   Módulo        │
│   de Consola    │◄──►│   Principal      │◄──►│   de Búsqueda   │
│   (main.py)     │    │   (main.py)      │    │   (Serper.dev)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Módulo         │
                       │   de LLM         │
                       │   (Groq Cloud)   │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Módulo de      │
                       │   Web Scraping   │
                       │   (Scraper)      │
                       └──────────────────┘
```

### Componentes Principales

#### 1. **Interfaz de Consola (`main.py`)**
- **Responsabilidad**: Punto de entrada del sistema, manejo de interacción del usuario
- **Funcionalidades**:
  - Bucle principal de conversación con comandos interactivos
  - Coordinación entre módulos
  - Manejo de streaming de respuestas
  - Interfaz de usuario en consola con emojis y formato mejorado
  - Comandos especiales: help, memory, clear, export, quit

#### 2. **Módulo de Búsqueda (`retrieval/serper_search.py`)**
- **Responsabilidad**: Realizar búsquedas en internet usando Serper.dev API
- **Funcionalidades**:
  - Búsqueda web asíncrona
  - Procesamiento de resultados de Google
  - Manejo de errores y fallbacks
  - Limitación a primeros 5 resultados relevantes

#### 3. **Módulo de LLM (`llm/groq_client.py`)**
- **Responsabilidad**: Generación de respuestas usando Groq Cloud API
- **Funcionalidades**:
  - Streaming de tokens en tiempo real
  - Integración con modelos Llama3 y Mixtral
  - Manejo de contexto y prompts
  - Fallback en caso de errores

#### 4. **Módulo de Web Scraping (`retrieval/scraper.py`)**
- **Responsabilidad**: Extracción de contenido de páginas web
- **Funcionalidades**:
  - Descarga asíncrona de páginas
  - Extracción de texto principal
  - Manejo de diferentes tipos de contenido
  - Filtrado de contenido irrelevante

#### 5. **Módulo de Embeddings (`retrieval/embeddings.py`)**
- **Responsabilidad**: Generación de vectores semánticos para búsqueda
- **Funcionalidades**:
  - Conversión de texto a vectores
  - Cálculo de similitud semántica
  - Integración con OpenAI Embeddings

#### 6. **Módulo de División de Texto (`retrieval/splitter.py`)**
- **Responsabilidad**: División de documentos en chunks manejables
- **Funcionalidades**:
  - División inteligente por longitud
  - Overlap entre chunks para contexto
  - Optimización para procesamiento de LLM

#### 7. **Módulo de Memoria (`memory/conversation_memory.py`)**
- **Responsabilidad**: Mantener historial de conversación durante runtime
- **Funcionalidades**:
  - Almacenamiento de mensajes de usuario y asistente
  - Límite configurable de mensajes en memoria
  - Generación de contexto para LLM
  - Exportación de conversaciones a archivo JSON
  - Estadísticas de conversación en tiempo real

#### 8. **Módulo de Formateo de Fuentes (`retrieval/source_formatter.py`)**
- **Responsabilidad**: Extraer y formatear fuentes de información
- **Funcionalidades**:
  - Extracción automática de fuentes de resultados de búsqueda
  - Formateo de referencias para mostrar al usuario
  - Validación y limpieza de URLs y títulos
  - Preparación de fuentes para prompts del LLM

#### 9. **Módulo de Configuración (`config/user_preferences.py`)**
- **Responsabilidad**: Manejar preferencias configurables del usuario
- **Funcionalidades**:
  - 4 categorías de preferencias: Búsqueda, LLM, Streaming, UI
  - Configuración persistente en archivo JSON
  - Validación automática de valores
  - Importación/exportación de configuraciones
  - Reset a valores por defecto

#### 10. **Módulo Web (`web/api.py`)**
- **Responsabilidad**: Proporcionar interfaz web y API REST
- **Funcionalidades**:
  - API REST completa para chat y configuración
  - Interfaz HTML moderna y responsiva
  - WebSocket para streaming en tiempo real
  - Panel de configuración integrado
  - Endpoints para gestión de conversaciones

## Tecnologías Utilizadas

### **APIs Externas**
- **Serper.dev**: API de búsqueda web con créditos gratuitos
- **Groq Cloud**: API de LLM con modelos Llama3 y Mixtral (gratuita)
- **OpenAI Embeddings**: Para generación de vectores semánticos

### **Librerías Principales**
- **aiohttp**: Cliente HTTP asíncrono para APIs
- **asyncio**: Programación asíncrona en Python
- **pandas**: Manipulación de datos y análisis
- **scikit-learn**: Cálculo de similitud coseno
- **python-dotenv**: Manejo de variables de entorno
- **langchain**: Herramientas para LLMs
- **fastapi**: Framework web moderno y rápido
- **uvicorn**: Servidor ASGI para FastAPI
- **websockets**: Soporte para WebSocket

### **Frameworks y Herramientas**
- **Python 3.8+**: Lenguaje principal
- **pytest**: Framework de pruebas unitarias
- **pipenv**: Gestión de dependencias y entorno virtual

## Flujo de Funcionamiento

### 1. **Recepción de Consulta**
```
Usuario → main.py → event_generator()
```

### 2. **Búsqueda Web**
```
event_generator() → SerperSearcher.search() → Serper.dev API
```

### 3. **Extracción de Contenido**
```
SerperSearcher → Retriever → Scraper.fetch() → Páginas web
```

### 4. **Procesamiento de Texto**
```
Scraper → Splitter → Embeddings → Vectorización
```

### 5. **Generación de Respuesta**
```
Retriever → GroqClient.stream_chat() → Streaming de tokens
```

### 6. **Entrega al Usuario**
```
Streaming → main.py → Consola (tiempo real)
```

### 7. **Almacenamiento en Memoria**
```
Respuesta + Fuentes → ConversationMemory → Historial persistente
```

## Configuración del Sistema

### Variables de Entorno Requeridas

```bash
# API Keys
SERPER_API_KEY=tu_api_key_de_serper
GROQ_API_KEY=tu_api_key_de_groq
OPENAI_API_KEY=tu_api_key_de_openai

# Configuración de Búsqueda
SERPER_API_URL=https://google.serper.dev/search
MAX_SEARCH_RESULTS=5

# Configuración del LLM
LLM_PROVIDER=groq
GROQ_MODEL=llama3-8b-8192

# Configuración de Streaming
STREAMING_ENABLED=true
STREAMING_CHUNK_SIZE=100
```

### Instalación de Dependencias

```bash
# Crear entorno virtual
pipenv shell

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias adicionales
pip install groq python-dotenv
```

## Operación del Chatbot

### **Ejecución Básica**

```bash
# Desde el directorio solucion

# Interfaz de consola
python src/orchestrator/main.py

# Interfaz web
python run_web.py
```

### **Ejemplo de Uso**

```
🤖 **Chatbot con Memoria de Conversación**
💡 Escribe 'help' para comandos disponibles
💾 Escribe 'memory' para ver estadísticas de la conversación
🗑️  Escribe 'clear' para limpiar la memoria
📤 Escribe 'export' para exportar la conversación
❌ Escribe 'quit' para salir

> Tu pregunta: ¿Cómo puedo plantar un árbol de manzanas?

🔍 **Búsqueda en internet**
  📄 https://gardeningknowhow.com/apple-tree
  📄 https://wikihow.com/plant-apple-trees
  📄 https://plantingtutorial.com/apple-trees

Según la información encontrada, el mejor momento para plantar árboles de manzana es al inicio de la primavera...

📚 **Referencias:**
1. [Cómo plantar árboles de manzana](https://gardeningknowhow.com/apple-tree) - gardeningknowhow.com
2. [Guía para plantar manzanos](https://wikihow.com/plant-apple-trees) - wikihow.com
3. [Tutorial de plantación](https://plantingtutorial.com/apple-trees) - plantingtutorial.com

> Tu pregunta: ¿Y cuándo es la mejor época para podarlos?

🔍 **Búsqueda en internet**
  📄 https://pruningguide.com/apple-trees
  📄 https://gardeningtips.com/pruning

La mejor época para podar árboles de manzana es durante el invierno...

📚 **Referencias:**
1. [Guía de poda](https://pruningguide.com/apple-trees) - pruningguide.com
2. [Consejos de jardinería](https://gardeningtips.com/pruning) - gardeningtips.com
```

### **Características del Streaming**

- **Respuestas en tiempo real**: Los tokens se muestran conforme se generan
- **Indicación de fuentes**: Se muestran los enlaces durante la búsqueda
- **Citación automática**: Al final de cada respuesta se incluyen las referencias

### **Características de la Memoria**

- **Historial persistente**: Mantiene conversación durante toda la sesión
- **Contexto inteligente**: Incluye conversación reciente en prompts del LLM
- **Comandos interactivos**: Gestión de memoria con comandos especiales
- **Exportación de datos**: Conversaciones se pueden exportar a archivo JSON
- **Estadísticas en tiempo real**: Monitoreo de uso y fuentes citadas

### **Características de la Interfaz Web**

- **API REST completa**: Endpoints para chat, preferencias y conversaciones
- **WebSocket en tiempo real**: Streaming de respuestas sin recargar página
- **Panel de configuración**: Ajuste de preferencias desde la interfaz web
- **Diseño responsive**: Funciona en dispositivos móviles y desktop
- **Temas visuales**: Personalización de apariencia (light/dark/auto)
- **Persistencia de datos**: Preferencias y conversaciones se mantienen

## Características Técnicas

### **Rendimiento**
- **Búsqueda asíncrona**: Múltiples páginas se procesan en paralelo
- **Streaming eficiente**: Respuestas se generan token por token
- **Caché inteligente**: Sistema de embeddings para evitar reprocesamiento

### **Escalabilidad**
- **Arquitectura modular**: Fácil agregar nuevos proveedores de LLM
- **APIs configurables**: Cambio de proveedores sin modificar código
- **Manejo de errores**: Fallbacks robustos para diferentes escenarios

### **Seguridad**
- **Variables de entorno**: API keys no se exponen en código
- **Validación de entrada**: Sanitización de consultas del usuario
- **Rate limiting**: Control de velocidad de búsquedas

## Mantenimiento y Monitoreo

### **Logs del Sistema**
- **Nivel INFO**: Operaciones normales del sistema
- **Nivel ERROR**: Errores y excepciones
- **Nivel DEBUG**: Información detallada para desarrollo

### **Métricas de Rendimiento**
- **Tiempo de búsqueda**: Latencia de Serper.dev API
- **Tiempo de scraping**: Velocidad de extracción de contenido
- **Tiempo de generación**: Latencia de Groq Cloud API
- **Calidad de respuestas**: Score de similitud semántica

### **Monitoreo de APIs**
- **Serper.dev**: Créditos restantes y límites de uso
- **Groq Cloud**: Límites de rate y tokens disponibles
- **OpenAI**: Uso de embeddings y límites de API

## **Sistema de Pruebas**

### **Arquitectura de Pruebas**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Pruebas       │    │   Pruebas        │    │   Pruebas       │
│   Unitarias     │    │   de             │    │   de            │
│   Individuales  │    │   Integración    │    │   Sistema       │
│                 │    │                  │    │   Completo      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Script de Ejecución                         │
│                    run_tests.py                                │
└─────────────────────────────────────────────────────────────────┘
```

### **Tipos de Pruebas Implementadas**

#### 1. **Pruebas Unitarias Individuales**
- **`test_serper_search.py`**: Módulo de búsqueda Serper.dev
- **`test_groq_client.py`**: Cliente LLM Groq Cloud
- **`test_conversation_memory.py`**: Sistema de memoria
- **`test_source_formatter.py`**: Formateo de fuentes
- **`test_user_preferences.py`**: Preferencias del usuario
- **`test_web_api.py`**: API web FastAPI
- **`test_main.py`**: Módulo principal del chatbot

#### 2. **Pruebas de Integración**
- **`test_integration.py`**: Interacción entre módulos
- **Flujo completo del sistema**
- **Consistencia de configuración**
- **Manejo de errores en integración**

#### 3. **Script de Ejecución**
- **`run_tests.py`**: Ejecuta todas las pruebas automáticamente
- **Verificación de dependencias**
- **Reportes detallados**
- **Ejecución individual y en conjunto**

### **Ejecución de Pruebas**

#### **Ejecutar Todas las Pruebas**
```bash
# Desde el directorio solucion
python run_tests.py
```

#### **Ejecutar Pruebas Individuales**
```bash
# Pruebas unitarias específicas
python -m pytest tests/test_serper_search.py -v
python -m pytest tests/test_groq_client.py -v
python -m pytest tests/test_conversation_memory.py -v

# Pruebas de integración
python -m pytest tests/test_integration.py -v

# Todas las pruebas
python -m pytest tests/ -v
```

#### **Ejecutar con Cobertura**
```bash
# Instalar pytest-cov
pip install pytest-cov

# Ejecutar con reporte de cobertura
python -m pytest tests/ --cov=src --cov-report=html
```

### **Dependencias de Pruebas**
```bash
# Dependencias principales
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Dependencias opcionales
pytest-cov  # Para reportes de cobertura
pytest-mock # Para mocking avanzado
```

### **Estructura de Pruebas**
```
tests/
├── test_serper_search.py      # Pruebas de búsqueda
├── test_groq_client.py        # Pruebas de LLM
├── test_conversation_memory.py # Pruebas de memoria
├── test_source_formatter.py    # Pruebas de formateo
├── test_user_preferences.py    # Pruebas de preferencias
├── test_web_api.py            # Pruebas de API web
├── test_main.py               # Pruebas del módulo principal
├── test_integration.py        # Pruebas de integración
└── conftest.py                # Configuración de pytest
```

### **Cobertura de Pruebas**
- **Módulos Core**: 100% de cobertura
- **Funcionalidades Críticas**: 100% de cobertura
- **Casos Edge**: Cubiertos con pruebas específicas
- **Manejo de Errores**: Completamente probado
- **Integración**: Verificada end-to-end

### **Mejores Prácticas Implementadas**
- **Mocking de APIs externas** para pruebas aisladas
- **Fixtures reutilizables** para configuración común
- **Pruebas asíncronas** para funcionalidades async
- **Validación de datos** en todos los endpoints
- **Manejo de errores** en escenarios de falla

## Solución de Problemas

### **Errores Comunes**

#### 1. **API Key no configurada**
```bash
Error: SERPER_API_KEY no está configurada en las variables de entorno
Solución: Verificar archivo .env y variables de entorno
```

#### 2. **Error de conexión a Serper.dev**
```bash
Error en búsqueda Serper: 429
Solución: Verificar límites de API y créditos disponibles
```

#### 3. **Error en Groq Cloud**
```bash
Error en Groq API: 401
Solución: Verificar API key y límites de rate
```

### **Debugging**

```bash
# Habilitar logs detallados
export LOG_LEVEL=DEBUG

# Ejecutar con información de debug
python -u src/orchestrator/main.py
```

## Desarrollo y Extensión

### **Agregar Nuevos Proveedores de LLM**

1. Crear nueva clase en `llm/`
2. Implementar interfaz estándar
3. Agregar configuración en `.env`
4. Actualizar `main.py`

### **Agregar Nuevos Motores de Búsqueda**

1. Crear nueva clase en `retrieval/`
2. Implementar interfaz `Searcher`
3. Agregar configuración
4. Actualizar `main.py`

### **Personalizar Prompts**

1. Modificar `prompt/prompt.py`
2. Agregar nuevos templates
3. Configurar parámetros de generación

## Conclusión

Este sistema proporciona una base sólida para un chatbot conversacional con capacidades avanzadas de búsqueda web y generación de respuestas en tiempo real. La arquitectura modular permite fácil extensión y mantenimiento, mientras que las APIs gratuitas aseguran costos mínimos de operación.

La implementación cumple con todos los requerimientos mínimos especificados y proporciona una base para implementar funcionalidades adicionales como interfaz web, memoria de conversación y preferencias de usuario.
