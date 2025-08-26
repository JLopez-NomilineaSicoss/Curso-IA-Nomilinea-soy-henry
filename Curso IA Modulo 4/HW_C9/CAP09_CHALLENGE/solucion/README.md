# 🚀 Sistema de Consulta de Noticias con LangChain

Un sistema inteligente de consulta de noticias que utiliza **LangChain**, **APIs gratuitas** y ofrece tanto **interfaz web en tiempo real** como **consola interactiva**.

## ✨ Características Principales

### 🤖 Inteligencia Artificial
- **LLM Gratuito**: Groq Cloud (Llama3-8B) para respuestas inteligentes
- **Embeddings Gratuitos**: Google AI Studio para búsqueda semántica
- **Memoria Conversacional**: Mantiene contexto durante la conversación
- **Clasificación Automática**: Distingue entre consultas de noticias y generales

### 🌐 Interfaz Web Moderna
- **Chat en Tiempo Real**: Socket.IO para comunicación bidireccional
- **Diseño Responsivo**: Funciona en desktop, tablet y móvil
- **Indicadores Visuales**: Estados de conexión, typing indicators, notificaciones
- **Estadísticas**: Contador de consultas, tiempo de sesión, tipos de consulta
- **Exportar Chat**: Descarga conversaciones en formato texto

### 📰 Búsqueda de Noticias
- **API Gratuita**: Serper.dev para noticias actuales
- **Búsqueda Inteligente**: Procesamiento de consultas en lenguaje natural
- **Fuentes Verificadas**: Información de sitios de noticias confiables
- **Contexto Relevante**: Respuestas basadas en eventos actuales

### 🧪 Testing Completo
- **Jest Framework**: Suite completa de pruebas unitarias
- **Mocking**: APIs mockeadas para testing sin dependencias externas
- **Cobertura**: Validación de componentes críticos del sistema

## 🛠️ Tecnologías Utilizadas

### Backend
- **Node.js**: Runtime de JavaScript
- **Express.js**: Framework web minimalista
- **Socket.IO**: Comunicación en tiempo real
- **LangChain**: Framework para aplicaciones LLM

### Frontend
- **HTML5/CSS3**: Estructura y estilos modernos
- **JavaScript ES6+**: Programación asíncrona y orientada a objetos
- **Socket.IO Client**: Cliente para comunicación en tiempo real

### APIs y Servicios
- **Groq Cloud**: LLM Llama3-8B (Gratuito)
- **Google AI Studio**: Embeddings text-embedding-004 (Gratuito)
- **Serper.dev**: API de búsqueda de noticias (Gratuito)

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias
```bash
npm install
```

### 2. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```env
# Groq Cloud API (https://console.groq.com/)
GROQ_API_KEY=tu_groq_api_key_aqui

# Google AI Studio (https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=tu_google_api_key_aqui

# Serper.dev (https://serper.dev/dashboard)
SERPER_API_KEY=tu_serper_api_key_aqui

# Configuración del servidor (opcional)
PORT=3000
```

### 3. Obtener las API Keys Gratuitas

#### Groq Cloud (LLM)
1. Visita: https://console.groq.com/
2. Crea una cuenta gratuita
3. Ve a "API Keys" y genera una nueva key
4. Copia la key en tu archivo `.env`

#### Google AI Studio (Embeddings)
1. Visita: https://makersuite.google.com/app/apikey
2. Inicia sesión con tu cuenta de Google
3. Crea una nueva API key
4. Copia la key en tu archivo `.env`

#### Serper.dev (Noticias)
1. Visita: https://serper.dev/dashboard
2. Crea una cuenta gratuita
3. Obtén tu API key del dashboard
4. Copia la key en tu archivo `.env`

## 🎮 Uso del Sistema

### Interfaz Web (Recomendado)
```bash
# Iniciar servidor web
npm run web
# o
npm run server
```
Luego abre: http://localhost:3000

### Consola Interactiva
```bash
# Modo consola
npm run console
# o
npm start
```

### Comandos Disponibles
```bash
# Desarrollo con auto-reload
npm run dev:web     # Servidor web con watch mode
npm run dev         # Consola con watch mode

# Testing
npm test            # Ejecutar todas las pruebas
npm run test:watch  # Pruebas en modo watch
npm run test:coverage # Pruebas con cobertura

# Utilidades
npm run setup       # Script de configuración inicial
npm run install:deps # Reinstalar dependencias
```

## 💬 Ejemplos de Uso

### Consultas de Noticias 📰
- "¿Cuáles son las últimas noticias de tecnología?"
- "Noticias sobre inteligencia artificial hoy"
- "¿Qué está pasando en el mundo del deporte?"
- "Noticias recientes sobre cambio climático"

### Consultas Generales 🤔
- "¿Qué es la inteligencia artificial?"
- "Explícame cómo funciona blockchain"
- "¿Cuáles son los beneficios del ejercicio?"
- "Historia de la computación"

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   APIs/LLM      │
│                 │    │                 │    │                 │
│ • HTML/CSS/JS   │◄──►│ • Express.js    │◄──►│ • Groq Cloud    │
│ • Socket.IO     │    │ • Socket.IO     │    │ • Google AI     │
│ • Chat Interface│    │ • LangChain     │    │ • Serper.dev    │
│ • Real-time UI  │    │ • News System   │    │ • News APIs     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Componentes Principales

#### `news-system.js`
- **Core del sistema**: Maneja la lógica principal de LangChain
- **Clasificación**: Determina tipo de consulta (noticias vs general)
- **Memory Management**: Mantiene historial conversacional
- **API Integration**: Conecta con todas las APIs externas

#### `server-final.js`
- **Servidor Web**: Express.js con Socket.IO
- **Real-time**: Comunicación bidireccional con clientes
- **Error Handling**: Manejo robusto de errores y reconexiones
- **Static Files**: Sirve archivos estáticos de la interfaz web

#### `script-final.js`
- **Cliente JavaScript**: Interfaz interactiva del navegador
- **UI Management**: Estados, notificaciones, estadísticas
- **Socket Management**: Conexión y reconexión automática
- **UX Features**: Typing indicators, exportar chat, etc.

## 🧪 Testing

### Ejecutar Pruebas
```bash
# Todas las pruebas
npm test

# Modo watch (desarrollo)
npm run test:watch

# Con cobertura
npm run test:coverage
```

### Cobertura de Pruebas
- ✅ **Inicialización del sistema**
- ✅ **Clasificación de consultas**
- ✅ **Integración con APIs**
- ✅ **Manejo de errores**
- ✅ **Respuestas del sistema**
- ✅ **Servidor web y Socket.IO**

## 📊 Funcionalidades Web

### Dashboard de la Interfaz Web
- **Estado de Conexión**: Tiempo real
- **Total de Consultas**: Contador global
- **Consultas por Tipo**: Noticias vs General
- **Tiempo de Sesión**: Cronómetro automático
- **Configuración Activa**: Proveedores de IA utilizados

### Características UX
- ✅ **Chat en tiempo real** con Socket.IO
- ✅ **Interfaz responsive** para todos los dispositivos
- ✅ **Estadísticas en vivo** de uso y consultas
- ✅ **Exportar conversaciones** a archivo de texto
- ✅ **Indicadores visuales** de estado y conexión
- ✅ **Notificaciones** y feedback del sistema
- ✅ **Typing indicators** durante procesamiento
- ✅ **Memoria conversacional** persistente

## 🔧 Solución de Problemas

### Error: "API Key no configurada"
```bash
# Verificar archivo .env
cat .env
# Debe contener todas las keys necesarias
```

### Error: "Puerto ya en uso"
```bash
# Cambiar puerto en .env
echo "PORT=3001" >> .env
```

### Error: "Módulos no encontrados"
```bash
# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

### Problemas de conexión Socket.IO
1. Verificar que el servidor esté ejecutándose
2. Comprobar firewall/antivirus
3. Probar en navegador incógnito
4. Verificar consola del navegador para errores

## 🛡️ Seguridad y Mejores Prácticas

### Variables de Entorno
- ✅ Las API keys nunca se hardcodean
- ✅ Archivo `.env` en `.gitignore`
- ✅ Validación de keys al inicio

### Manejo de Errores
- ✅ Try-catch en todas las operaciones críticas
- ✅ Fallbacks para APIs no disponibles
- ✅ Logs detallados para debugging

### Límites y Rate Limiting
- ✅ Respeto a límites de APIs gratuitas
- ✅ Timeouts configurados apropiadamente
- ✅ Manejo de errores de quota excedida

---

**¡Disfruta explorando el mundo de las noticias con inteligencia artificial! 🚀📰🤖**
