# Curso de Inteligencia Artificial - Proyectos

Este repositorio contiene tres proyectos desarrollados como parte de un curso de Inteligencia Artificial, cada uno enfocado en diferentes aspectos del desarrollo de software y la integración con IA.

## 📁 HW_C1 - Copilotos y APIs Básicas

**Descripción:** Proyecto introductorio que demuestra el uso de copilotos de código impulsados por IA para crear una API simple con FastAPI.

### Características principales:
- **Framework:** FastAPI con Python
- **Funcionalidades:** Algoritmos básicos (Bubble Sort, búsqueda binaria, filtros)
- **Autenticación:** Sistema JWT con tokens
- **Seguridad:** Cifrado de contraseñas con Passlib
- **Endpoints:** 5 endpoints matemáticos + registro/login

### Tecnologías:
- FastAPI
- Pydantic (validación de datos)
- PyJWT (tokens de autenticación)
- Passlib (cifrado de contraseñas)

### Objetivo de aprendizaje:
Demostrar cómo crear una API funcional con ayuda de copilotos de IA, incluso sin conocimiento profundo previo del framework.

---

## 📁 HW_C2 - Task Manager API

**Descripción:** API completa para gestión de tareas con funcionalidades CRUD, autenticación y pruebas automatizadas.

### Características principales:
- **Funcionalidad:** CRUD completo de tareas
- **Autenticación:** HTTP Basic Auth
- **Logging:** Sistema de registro de operaciones
- **Pruebas:** Suite completa de pruebas unitarias
- **Manejo de errores:** Respuestas personalizadas y uniformes

### Tecnologías:
- FastAPI
- Pydantic (modelos de datos)
- pytest (pruebas automatizadas)
- Logging integrado

### Objetivo de aprendizaje:
Desarrollar una API robusta con buenas prácticas de desarrollo, incluyendo autenticación, logging, manejo de errores y pruebas.

---

## 📁 HW_C3 - InternetWhisper (Chatbot IA)

**Descripción:** Chatbot conversacional avanzado que puede acceder a Internet en tiempo real para responder preguntas, inspirado en You.com y Google Bard.

### Características principales:
- **Interfaz:** Frontend con Streamlit
- **Backend:** API FastAPI (orchestrator)
- **Búsqueda:** Integración con Google Custom Search API
- **Cache:** Base de datos vectorial Redis
- **IA:** Integración con OpenAI GPT-3.5 Turbo
- **Web Scraping:** Extracción de contenido web
- **Contenedores:** Arquitectura microservicios con Docker

### Arquitectura:
```
Usuario → Frontend (Streamlit) → Orchestrator (FastAPI) → Redis Cache
                                                    ↓
                                              Google Search API
                                                    ↓
                                              Web Scraper
                                                    ↓
                                              OpenAI Embeddings
```

### Tecnologías:
- **Frontend:** Streamlit
- **Backend:** FastAPI
- **Base de datos:** Redis Vector DB
- **IA:** OpenAI API (GPT-3.5, embeddings)
- **Búsqueda:** Google Custom Search API
- **Scraping:** aiohttp, Playwright
- **Contenedores:** Docker Compose

### Objetivo de aprendizaje:
Crear un sistema de IA generativa complejo que integre múltiples servicios, APIs externas y tecnologías modernas para crear un chatbot inteligente con acceso a información en tiempo real.

---

## 🚀 Instalación y Uso

Cada proyecto tiene su propio README detallado con instrucciones específicas de instalación y ejecución. En general:

1. **HW_C1:** `uvicorn main:app --reload`
2. **HW_C2:** `uvicorn app.main:app --reload`
3. **HW_C3:** `docker-compose up`

## 📚 Progresión de Complejidad

- **HW_C1:** Introducción a APIs y copilotos de IA
- **HW_C2:** APIs robustas con buenas prácticas
- **HW_C3:** Sistema complejo de IA con múltiples servicios

Cada proyecto construye sobre los conocimientos adquiridos en el anterior, creando una progresión natural de aprendizaje desde conceptos básicos hasta sistemas avanzados de IA.

---

## 🔧 Requisitos Generales

- Python 3.7+
- pip
- Docker (solo para HW_C3)
- APIs externas (Google Search, OpenAI - solo para HW_C3)

## 📝 Notas

- Todos los proyectos incluyen documentación detallada en sus respectivas carpetas
- HW_C1 y HW_C2 usan bases de datos simuladas en memoria
- HW_C3 requiere configuración de variables de entorno para las APIs externas
- Cada proyecto incluye pruebas automatizadas donde corresponde 