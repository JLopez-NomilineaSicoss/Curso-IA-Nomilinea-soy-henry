// =================================================================
// Servidor Web Optimizado - Sin cuelgues en inicialización
// =================================================================

import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Configuración de rutas
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Cargar variables de entorno desde el directorio correcto
dotenv.config({ path: path.join(__dirname, '.env') });

// Verificar que las variables de entorno se cargaron
console.log('🔧 Verificando variables de entorno...');
console.log('GROQ_API_KEY:', process.env.GROQ_API_KEY ? '✅ Configurado' : '❌ No encontrado');
console.log('GOOGLE_API_KEY:', process.env.GOOGLE_API_KEY ? '✅ Configurado' : '❌ No encontrado');

// Crear aplicación Express
const app = express();
const server = createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// Variable global para el sistema
let newsSystem = null;
let isSystemInitialized = false;
let initializationPromise = null;

// Servir archivos estáticos
app.use(express.static(path.join(__dirname, 'public')));

// Ruta principal
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Función de inicialización del sistema con timeout
async function initializeNewsSystem() {
    if (isSystemInitialized && newsSystem && typeof newsSystem.query === 'function') {
        console.log('🔄 Sistema ya inicializado, reutilizando...');
        return newsSystem;
    }
    
    if (initializationPromise) {
        return initializationPromise;
    }
    
    initializationPromise = new Promise(async (resolve, reject) => {
        const timeoutId = setTimeout(() => {
            console.log('⚠️ Inicialización con timeout - modo simple activado');
            const fallbackSystem = createSimpleSystem();
            newsSystem = fallbackSystem;
            isSystemInitialized = true;
            resolve(fallbackSystem);
        }, 10000); // 10 segundos timeout
        
        try {
            console.log('🚀 Inicializando sistema de noticias...');
            
            // Importar dinámicamente para evitar cuelgues
            const { NewsQuerySystem } = await import('./news-system.js');
            
            console.log('🤖 Creando instancia del sistema...');
            const system = new NewsQuerySystem();
            
            console.log('⚡ Inicialización rápida...');
            await system.quickInitialize();
            
            clearTimeout(timeoutId);
            
            // Verificar que el sistema tenga el método query
            console.log('🔍 Verificando métodos disponibles:', Object.getOwnPropertyNames(Object.getPrototypeOf(system)));
            console.log('🔍 Tipo de query:', typeof system.query);
            
            if (typeof system.query === 'function') {
                newsSystem = system;
                isSystemInitialized = true;
                console.log('✅ Sistema inicializado correctamente con método query');
                resolve(system);
            } else {
                console.log('⚠️ Sistema sin método query, usando fallback...');
                const fallbackSystem = createSimpleSystem();
                newsSystem = fallbackSystem;
                isSystemInitialized = true;
                resolve(fallbackSystem);
            }
            
        } catch (error) {
            clearTimeout(timeoutId);
            console.error('❌ Error en inicialización:', error.message);
            console.log('🔄 Activando modo simple...');
            const fallbackSystem = createSimpleSystem();
            newsSystem = fallbackSystem;
            isSystemInitialized = true;
            resolve(fallbackSystem);
        }
    });
    
    return initializationPromise;
}

// Sistema simple como fallback
function createSimpleSystem() {
    return {
        async query(text) {
            const isNews = text.toLowerCase().includes('noticia') || 
                          text.toLowerCase().includes('news') ||
                          text.toLowerCase().includes('actualidad');
            
            if (isNews) {
                return {
                    response: `📰 **Consulta de Noticias**: ${text}
                    
Lo siento, el sistema de noticias está en modo simplificado. Para consultas de noticias reales, necesito:

1. ✅ **Conexión a APIs** de noticias
2. ✅ **Configuración completa** del sistema LangChain
3. ✅ **Acceso a internet** para búsquedas

**Modo actual**: Sistema básico funcionando
**Sugerencia**: Verifica la configuración de APIs y conexión a internet.`,
                    queryType: 'news'
                };
            } else {
                return {
                    response: `🤖 **Consulta General**: ${text}
                    
¡Hola! El sistema está funcionando en **modo simplificado**. 

**Tu consulta**: "${text}"

**Respuesta básica**: Esta es una respuesta de ejemplo del sistema. Para respuestas completas con IA, el sistema necesita:
- ✅ Conexión a APIs de LLM (Groq)
- ✅ Configuración completa de LangChain
- ✅ Acceso a servicios de embedding

**Estado actual**: Sistema web funcional con interfaz completa.`,
                    queryType: 'general'
                };
            }
        },
        
        clearMemory() {
            console.log('🧹 Memoria limpiada (modo simple)');
            return { success: true };
        }
    };
}

// Manejar conexiones Socket.IO
io.on('connection', (socket) => {
    console.log(`👤 Usuario conectado: ${socket.id}`);
    
    // Enviar estado del sistema
    socket.emit('systemStatus', { 
        message: 'Conectando al sistema...' 
    });
    
    // Inicializar sistema para este usuario
    initializeNewsSystem()
        .then((system) => {
            socket.emit('systemReady', {
                message: 'Sistema listo para consultas',
                config: {
                    llmProvider: 'Groq Cloud',
                    embeddingProvider: 'Google AI'
                }
            });
        })
        .catch((error) => {
            console.error('❌ Error inicializando para usuario:', error);
            socket.emit('systemError', {
                message: 'Error en inicialización - modo simple activado'
            });
        });
    
    // Manejar consultas
    socket.on('query', async (data) => {
        try {
            console.log(`📝 Consulta recibida: "${data.text}"`);
            
            if (!newsSystem) {
                socket.emit('systemStatus', { 
                    message: 'Inicializando sistema...' 
                });
                
                newsSystem = await initializeNewsSystem();
            }
            
            // Verificar que el sistema tenga el método query
            console.log('🔍 Verificando sistema antes de consulta...');
            console.log('🔍 newsSystem existe:', !!newsSystem);
            console.log('🔍 Tipo de newsSystem.query:', typeof newsSystem?.query);
            
            if (!newsSystem || typeof newsSystem.query !== 'function') {
                console.log('⚠️ Sistema sin método query, activando fallback...');
                newsSystem = createSimpleSystem();
            }
            
            console.log('🚀 Ejecutando consulta...');
            const result = await newsSystem.query(data.text);
            console.log('✅ Resultado obtenido:', result?.queryType || 'unknown');
            
            socket.emit('queryResponse', {
                response: result.response,
                queryType: result.queryType || 'general'
            });
            
        } catch (error) {
            console.error('❌ Error procesando consulta:', error);
            
            // Si hay error, crear un sistema simple para responder
            const fallbackSystem = createSimpleSystem();
            const fallbackResult = await fallbackSystem.query(data.text);
            
            socket.emit('queryResponse', {
                response: `⚠️ **Sistema en Modo de Recuperación**

${fallbackResult.response}

**Nota**: Hubo un problema temporal con el sistema principal. La funcionalidad básica está disponible.`,
                queryType: 'error'
            });
        }
    });
    
    // Limpiar memoria
    socket.on('clearMemory', async () => {
        try {
            if (newsSystem && newsSystem.clearMemory) {
                await newsSystem.clearMemory();
            }
            socket.emit('memoryCleared', { 
                message: 'Memoria limpiada correctamente' 
            });
        } catch (error) {
            console.error('❌ Error limpiando memoria:', error);
        }
    });
    
    // Desconexión
    socket.on('disconnect', () => {
        console.log(`👤 Usuario desconectado: ${socket.id}`);
    });
});

// Configuración del puerto
const PORT = process.env.PORT || 3000;

// Iniciar servidor
server.listen(PORT, () => {
    console.log(`
════════════════════════════════════════════════════════
🌐 SERVIDOR WEB OPTIMIZADO INICIADO
════════════════════════════════════════════════════════
🔗 URL: http://localhost:${PORT}
🤖 Sistema: Modo inteligente con fallback
💰 Costo: 100% GRATUITO
📱 Interfaz: Web moderna + responsive
💬 Chat: Tiempo real con Socket.IO
⚡ Optimización: Sin cuelgues de inicialización
════════════════════════════════════════════════════════

🚀 Abre tu navegador en: http://localhost:${PORT}
📝 El sistema se inicializa automáticamente al conectar
✨ ¡Interfaz lista para usar inmediatamente!
    `);
});

// Manejo de errores del servidor
server.on('error', (error) => {
    if (error.code === 'EADDRINUSE') {
        console.error(`❌ Puerto ${PORT} ya está en uso`);
        console.log('💡 Intenta con: npm run web -- --port 3001');
    } else {
        console.error('❌ Error del servidor:', error);
    }
});

// Manejo de señales del sistema
process.on('SIGINT', () => {
    console.log('\n🛑 Cerrando servidor...');
    server.close(() => {
        console.log('✅ Servidor cerrado correctamente');
        process.exit(0);
    });
});

export default app;
