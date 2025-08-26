# 📰 Sistema de Consulta de Noticias con IA

## 🚀 Descripción

Sistema inteligente de consulta de noticias que utiliza **LangChain**, **inteligencia artificial** y **APIs gratuitas** para proporcionar respuestas precisas sobre eventos actuales y consultas generales. El sistema incluye tanto una **interfaz de línea de comandos** como una **interfaz web moderna** con comunicación en tiempo real.

### ✨ Características Principales

- **🤖 Clasificación Inteligente**: Diferencia automáticamente entre consultas de noticias y generales
- **📡 APIs Gratuitas**: Utiliza Groq (Llama3), Google AI y Serper.dev - **sin costos**
- **🧠 Memoria Conversacional**: Mantiene el contexto de la conversación
- **🌐 Interfaz Web**: Aplicación web moderna con comunicación en tiempo real
- **💻 CLI Interactivo**: Interfaz de línea de comandos para uso técnico
- **🔍 Búsqueda Avanzada**: Búsqueda de noticias con procesamiento de documentos
- **⚡ Tiempo Real**: WebSocket para comunicación instantánea
- **🧪 Pruebas Completas**: Suite completa de pruebas unitarias
- **📱 Responsive**: Diseño adaptable a dispositivos móviles

## 🏗️ Arquitectura del Sistema

```
Sistema de Consulta de Noticias
├── 🧠 Núcleo del Sistema
│   ├── main.js                 # Aplicación CLI principal
│   ├── news-system.js         # Sistema modular de noticias
│   ├── config.js              # Gestión de configuración
│   ├── providers.js           # Abstracción de proveedores IA
│   └── utils.js               # Utilidades comunes
├── 🌐 Interfaz Web
│   ├── server.js              # Servidor Express + Socket.IO
│   └── public/
│       ├── index.html         # Interfaz de usuario
│       ├── styles.css         # Estilos modernos
│       └── script.js          # Lógica del cliente
├── 🧪 Pruebas
│   ├── tests/
│   │   ├── news-system.test.js # Pruebas del sistema principal
│   │   ├── server.test.js      # Pruebas del servidor web
│   │   └── setup.js           # Configuración de pruebas
│   └── jest.config.js         # Configuración de Jest
└── 📄 Documentación
    ├── README.md              # Este archivo
    └── package.json           # Configuración del proyecto
```

## 🛠️ Tecnologías Utilizadas

### Inteligencia Artificial
- **LangChain v0.2.3**: Framework para aplicaciones LLM
- **Groq Cloud**: LLM gratuito (Llama3-8B) - [🆓 Gratis]
- **Google AI Studio**: Embeddings gratuitos - [🆓 Gratis]  
- **Serper.dev**: API de búsqueda gratuita - [🆓 Gratis]

### Backend & Web
- **Node.js 18+**: Runtime de JavaScript
- **Express.js**: Framework web minimalista
- **Socket.IO**: Comunicación en tiempo real
- **CORS**: Manejo de recursos cruzados

### Frontend
- **HTML5**: Estructura moderna y semántica
- **CSS3**: Diseño responsive y animaciones
- **JavaScript ES6+**: Lógica del cliente moderna
- **Font Awesome**: Iconografía profesional

### Testing & Desarrollo
- **Jest**: Framework de pruebas unitarias
- **Supertest**: Pruebas de APIs HTTP
- **Socket.IO Client**: Pruebas WebSocket
- **Nodemon**: Desarrollo con recarga automática

## 📋 Requisitos Previos

- **Node.js 18.0.0 o superior**
- **npm** (incluido con Node.js)
- **Conexión a internet** (para APIs)

## ⚙️ Instalación y Configuración

### 1. Clonar y configurar el proyecto

```bash
# Instalar dependencias
npm install

# O usar el script personalizado
npm run install:deps
```

### 2. Obtener claves API gratuitas

#### 🤖 Groq Cloud (LLM - GRATIS)
1. Visita [console.groq.com](https://console.groq.com)
2. Crea una cuenta gratuita
3. Genera una API key gratuita
4. Límites: 30 requests/minuto, 6000 tokens/minuto

#### 🧠 Google AI Studio (Embeddings - GRATIS)  
1. Visita [makersuite.google.com](https://makersuite.google.com)
2. Inicia sesión con tu cuenta Google
3. Genera una API key gratuita
4. Límites: 60 requests/minuto

#### 🔍 Serper.dev (Búsqueda - GRATIS)
1. Visita [serper.dev](https://serper.dev)
2. Regístrate con Google
3. Obtienes 2500 búsquedas gratuitas
4. Límites: 2500 búsquedas/mes gratis

### 3. Configurar variables de entorno

Crea un archivo `.env` en el directorio raíz:

```bash
# API Keys Gratuitas
GROQ_API_KEY=tu_clave_groq_aqui
GOOGLE_AI_API_KEY=tu_clave_google_ai_aqui  
SERPER_API_KEY=tu_clave_serper_aqui

# Configuración del Servidor (Opcional)
PORT=3000
NODE_ENV=development
```

## 🚀 Uso del Sistema

### 💻 Interfaz de Línea de Comandos (CLI)

```bash
# Ejecutar la aplicación CLI
npm start

# O con recarga automática para desarrollo
npm run dev
```

**Comandos disponibles en CLI:**
- Escribe tu consulta y presiona Enter
- `salir` o `exit` - Termina la aplicación
- `limpiar` o `clear` - Limpia la memoria conversacional

### 🌐 Interfaz Web

```bash
# Iniciar el servidor web
npm run server

# O con recarga automática para desarrollo  
npm run dev:server
```

**Acceder a la aplicación:**
- Abre tu navegador en: `http://localhost:3000`
- Interfaz moderna con chat en tiempo real
- Sidebar con estadísticas y configuración
- Soporte para dispositivos móviles

## 🧪 Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
npm test

# Ejecutar pruebas en modo watch
npm run test:watch

# Generar reporte de cobertura
npm run test:coverage
```

**Cobertura de pruebas:**
- ✅ Sistema de noticias (clasificación, búsqueda, memoria)
- ✅ Servidor web (API REST + WebSocket)
- ✅ Configuración y proveedores
- ✅ Manejo de errores
- ✅ Integración completa

## 📖 Ejemplos de Uso

### Consultas de Noticias
```
Usuario: "¿Cuáles son las últimas noticias sobre inteligencia artificial?"
Sistema: [Busca noticias actuales y proporciona resumen detallado con fuentes]

Usuario: "¿Qué está pasando con el cambio climático?"
Sistema: [Retorna noticias recientes sobre el tema con enlaces]
```

### Consultas Generales  
```
Usuario: "¿Qué es la fotosíntesis?"
Sistema: [Responde con conocimiento general sin buscar noticias]

Usuario: "Explícame cómo funciona el machine learning"
Sistema: [Proporciona explicación educativa detallada]
```

### Memoria Conversacional
```
Usuario: "Háblame sobre Python"
Sistema: "Python es un lenguaje de programación..."

Usuario: "¿Cuáles son sus ventajas?"
Sistema: [Recuerda el contexto de Python y responde específicamente]
```

## 🔧 Configuración Avanzada

### Personalizar Modelos IA

Edita `config.js` para modificar los modelos:

```javascript
const config = {
    providers: {
        groq: {
            model: 'llama3-8b-8192',  // Cambiar modelo
            temperature: 0.1          // Ajustar creatividad
        },
        google: {
            model: 'embedding-001'    // Modelo de embeddings
        }
    }
};
```

### Configurar Puerto del Servidor

```bash
# En .env
PORT=8080

# O al ejecutar
PORT=8080 npm run server
```

## 🏭 Despliegue en Producción

### Variables de Entorno para Producción

```bash
NODE_ENV=production
PORT=80
GROQ_API_KEY=tu_clave_produccion
GOOGLE_AI_API_KEY=tu_clave_produccion
SERPER_API_KEY=tu_clave_produccion
```

### Ejemplo con PM2

```bash
# Instalar PM2
npm install -g pm2

# Ejecutar en producción
pm2 start server.js --name "news-system"

# Monitorear
pm2 monit
```

## 🐛 Resolución de Problemas

### Error: "API key no válida"
```bash
# Verificar variables de entorno
echo $GROQ_API_KEY
echo $GOOGLE_AI_API_KEY  
echo $SERPER_API_KEY

# Regenerar claves en las consolas respectivas
```

### Error: "Sistema no inicializado"
```bash
# Verificar conexión a internet
# Verificar claves API
# Revisar logs del servidor
```

### Error: "Puerto en uso"
```bash
# Cambiar puerto
PORT=3001 npm run server

# O terminar proceso existente
lsof -ti:3000 | xargs kill -9
```

## 📊 Métricas y Monitoreo

### Estadísticas en Tiempo Real
- Total de consultas procesadas
- Consultas de noticias vs generales  
- Tiempo de sesión
- Estado de conexión

### Logs del Sistema
- Clasificación de consultas
- Tiempo de respuesta de APIs
- Errores y recuperación automática
- Métricas de uso de memoria

## 🤝 Contribución

### Estructura para Nuevas Características

1. **Backend**: Modificar `news-system.js` o `server.js`
2. **Frontend**: Actualizar `public/script.js` y `public/styles.css`
3. **Pruebas**: Agregar tests en directorio `tests/`
4. **Documentación**: Actualizar este README

### Guías de Desarrollo

```bash
# Configurar entorno de desarrollo
npm run dev:server        # Servidor con recarga automática
npm run test:watch        # Pruebas en modo watch
npm run test:coverage     # Verificar cobertura
```

## 📄 Licencia

Este proyecto está licenciado bajo **MIT License** - consulta el archivo LICENSE para detalles.

## 🙏 Agradecimientos

- **LangChain** - Framework de LLM excepcional
- **Groq** - LLM gratuito de alto rendimiento  
- **Google AI Studio** - Embeddings gratuitos de calidad
- **Serper.dev** - API de búsqueda gratuita
- **Comunidad de desarrolladores** - Por las herramientas open source

---

⭐ **¡Si este proyecto te resulta útil, considera darle una estrella en GitHub!**

🚀 **Sistema completamente funcional con APIs 100% gratuitas**
