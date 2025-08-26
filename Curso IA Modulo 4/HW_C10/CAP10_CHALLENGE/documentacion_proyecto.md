# 📚 Documentación del Proyecto - Sistema de Atención al Cliente Automatizado

## 🎯 Descripción General

Este proyecto implementa un sistema de atención al cliente automatizado utilizando **LangChain** que puede procesar diferentes tipos de consultas y enrutarlas al método más apropiado de respuesta. El sistema utiliza inteligencia artificial para proporcionar respuestas precisas y relevantes.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
Sistema de Atención al Cliente
├── 🤖 Agente LangChain (Coordinador central)
├── 🛠️ Herramientas Especializadas
│   ├── 💰 Consulta de Balances (CSV)
│   ├── 🏦 Base de Conocimientos (FAISS)
│   └── 💬 Respuestas Generales (LLM)
├── 🖥️ Interfaz Streamlit
└── 🧪 Suite de Pruebas Automatizadas
```

### Flujo de Datos

1. **Entrada del Usuario** → Interfaz Streamlit o CLI
2. **Procesamiento** → Agente LangChain analiza la consulta
3. **Enrutamiento** → Selecciona la herramienta apropiada:
   - **Balance**: Consulta directa al CSV
   - **Info Bancaria**: Búsqueda vectorial en FAISS
   - **General**: Respuesta del LLM
4. **Respuesta** → Resultado formateado al usuario

## 🔧 Tecnologías Utilizadas

### Core del Sistema
- **LangChain**: Framework principal para orquestación de IA
- **GROQ**: Modelo de lenguaje (Llama3-70B)
- **FAISS**: Base de datos vectorial para búsquedas semánticas
- **HuggingFace Sentence Transformers**: Generación de embeddings

### Procesamiento de Datos
- **Pandas**: Manipulación de datos CSV
- **NumPy**: Operaciones numéricas

### Interfaz de Usuario
- **Streamlit**: Interfaz web interactiva

### Testing y Calidad
- **Unittest**: Pruebas automatizadas
- **Pytest**: Framework de testing alternativo

## 📁 Estructura del Proyecto

```
CAP10_CHALLENGE/
├── 📄 challenge.md                 # Especificaciones originales
├── 📄 documentacion_proyecto.md    # Esta documentación
├── 📄 app.py                       # Interfaz Streamlit
├── 📄 .env.example                 # Plantilla de variables de entorno
├── 📄 saldos.csv                   # Base de datos de balances
├── 📁 solution/                    # Código principal
│   ├── 📄 main.py                  # Lógica principal del agente
│   ├── 📄 indexer.py               # Indexación de conocimientos
│   ├── 📄 requirements.txt         # Dependencias
│   └── 📁 index/                   # Índices FAISS
├── 📁 knowledge_base/              # Base de conocimientos
│   ├── 📄 nueva_cuenta.txt
│   ├── 📄 tarjeta_credito.txt
│   └── 📄 transferencia.txt
└── 📁 tests/                       # Suite de pruebas
    ├── 📄 test_balance_tool.py
    ├── 📄 test_knowledge_tool.py
    ├── 📄 test_agent_integration.py
    └── 📄 run_tests.py
```

## ⚙️ Instalación y Configuración

### 1. Prerequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### 2. Instalación de Dependencias

```bash
# Navegar al directorio del proyecto
cd CAP10_CHALLENGE

# Instalar dependencias
pip install -r solution/requirements.txt
```

### 3. Configuración de Variables de Entorno

```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env con tu API key de GROQ
GROQ_API_KEY=tu_groq_api_key_aqui
```

### 4. Indexación de la Base de Conocimientos (Opcional)

Si necesitas reindexar la base de conocimientos:

```bash
python solution/indexer.py
```

## 🚀 Ejecución del Sistema

### Opción 1: Interfaz Web (Recomendado)

```bash
streamlit run app.py
```

La aplicación estará disponible en: `http://localhost:8501`

### Opción 2: Línea de Comandos

```bash
python solution/main.py
```

## 🧪 Ejecución de Pruebas

### Ejecutar Todas las Pruebas

```bash
# Desde el directorio principal
python tests/run_tests.py

# O usando unittest
python -m unittest discover tests/
```

### Ejecutar Pruebas Específicas

```bash
# Pruebas de balance
python -m unittest tests.test_balance_tool

# Pruebas de conocimientos
python -m unittest tests.test_knowledge_tool

# Pruebas de integración
python -m unittest tests.test_agent_integration
```

## 💻 Uso del Sistema

### Ejemplos de Consultas

#### 1. Consulta de Balance
```
Usuario: "¿Cuál es el balance de la cédula V-91827364?"
Sistema: "El balance de la cuenta V-91827364 es: $2,580.00"
```

#### 2. Información Bancaria
```
Usuario: "¿Cómo abro una cuenta de ahorros?"
Sistema: "Para abrir una cuenta en BANCO HENRY, sigue estos pasos:
1. Visita la página web..."
```

#### 3. Consulta General
```
Usuario: "¿Qué es la inteligencia artificial?"
Sistema: "La inteligencia artificial es una rama de la informática..."
```

### Interfaz Streamlit

La interfaz web incluye:
- **Chat interactivo** con historial
- **Botones de prueba rápida** para cada funcionalidad
- **Sidebar informativo** con ejemplos
- **Manejo de errores** visual

## 🔧 Detalles Técnicos

### Herramientas del Agente

#### 1. `get_balance_by_id`
- **Función**: Consulta balances en CSV
- **Entrada**: ID de cédula (string)
- **Salida**: Balance formateado o mensaje de error
- **Manejo de errores**: Cédula no encontrada, archivo no accesible

#### 2. `get_bank_information`
- **Función**: Búsqueda en base de conocimientos
- **Entrada**: Pregunta sobre servicios bancarios
- **Salida**: Información relevante del banco
- **Tecnología**: RAG (Retrieval Augmented Generation) con FAISS

### Embeddings y Vectorización

- **Modelo**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensión**: 384 dimensiones
- **Base de datos**: FAISS (Facebook AI Similarity Search)
- **Estrategia**: Búsqueda de similitud coseno

### Configuración del LLM

- **Proveedor**: GROQ
- **Modelo**: Llama3-70B-8192
- **Temperatura**: 0 (respuestas determinísticas)
- **Tokens máximos**: Configurado automáticamente

## 📊 Casos de Prueba

### Pruebas Unitarias

#### Balance Tool
- ✅ Consulta exitosa de balance existente
- ✅ Manejo de cédula no encontrada
- ✅ Formato correcto de respuesta
- ✅ Validación de entrada vacía

#### Knowledge Tool
- ✅ Consulta exitosa de información bancaria
- ✅ Manejo de errores de conexión
- ✅ Respuesta a preguntas específicas
- ✅ Validación de herramienta

#### Integración
- ✅ Inicialización correcta del agente
- ✅ Formato de respuesta del agente
- ✅ Disponibilidad de herramientas
- ✅ Existencia de archivos críticos

## 🔍 Solución de Problemas

### Errores Comunes

#### 1. Error de API Key
```
Error: API key no configurada
Solución: Verificar archivo .env con GROQ_API_KEY
```

#### 2. Archivo CSV no encontrado
```
Error: FileNotFoundError: saldos.csv
Solución: Verificar que saldos.csv esté en el directorio raíz
```

#### 3. Índice FAISS no encontrado
```
Error: No se puede cargar el índice
Solución: Ejecutar python solution/indexer.py
```

#### 4. Dependencias faltantes
```
Error: ModuleNotFoundError
Solución: pip install -r solution/requirements.txt
```

### Logs y Debugging

El sistema incluye manejo de errores en:
- Consultas a la base de datos CSV
- Búsquedas en la base de conocimientos
- Comunicación con el LLM
- Carga de índices FAISS

## 📈 Métricas y Rendimiento

### Tiempo de Respuesta Esperado
- **Consulta de balance**: < 100ms
- **Información bancaria**: 1-3 segundos
- **Respuesta general**: 2-5 segundos

### Precisión
- **Balance**: 100% (consulta directa)
- **Información bancaria**: 85-95% (dependiente del contenido)
- **Respuestas generales**: 80-90% (dependiente del modelo)

## 🔄 Mantenimiento

### Actualización de la Base de Conocimientos

1. Editar archivos en `knowledge_base/`
2. Ejecutar: `python solution/indexer.py`
3. Reiniciar la aplicación

### Actualización de Datos de Balance

1. Editar `saldos.csv`
2. Mantener formato: `ID_Cedula,Nombre,Balance`
3. No requiere reindexación

## 🎓 Objetivos de Aprendizaje Cumplidos

✅ **Desarrollo con LangChain**: Implementación completa de agente con herramientas múltiples

✅ **IA para consultas**: Sistema robusto para bases de datos y conocimientos

✅ **Embeddings y NLP**: Uso eficiente de sentence-transformers y FAISS

✅ **Sistema de respuesta automatizada**: Enrutamiento inteligente basado en contenido

✅ **Pruebas automatizadas**: Suite completa de testing

## 🔮 Extensiones Futuras

### Posibles Mejoras
- **Autenticación de usuarios**
- **Logging avanzado**
- **Caché de respuestas**
- **API REST**
- **Base de datos relacional**
- **Análisis de sentimientos**
- **Respuestas multimodales**

### Escalabilidad
- **Despliegue en contenedores Docker**
- **Balanceador de carga**
- **Base de datos distribuida**
- **Monitoreo en tiempo real**

---

## 📞 Soporte

Para problemas técnicos o preguntas sobre la implementación, consulta:
- El código fuente en `solution/main.py`
- Las pruebas en `tests/`
- Los logs de error del sistema

**Proyecto desarrollado como parte del Curso de IA - Módulo 4 - Challenge 10**
