/**
 * Servidor Web Final - Sistema de Consulta de Noticias
 * Versión simplificada y funcional sin bucles infinitos
 */

import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import { NewsQuerySystem } from './news-system.js';

// Configuración ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Crear aplicación Express
const app = express();
const server = createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// Middlewares
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Sistema global - una sola instancia
let globalNewsSystem = null;
let isSystemInitialized = false;
let isInitializing = false;

// Función para inicializar el sistema una sola vez
async function initializeSystemOnce() {
    if (isSystemInitialized || isInitializing) {
        return globalNewsSystem;
    }
    
    isInitializing = true;
    
    try {
        console.log('🚀 Inicializando sistema de noticias (una sola vez)...');
        globalNewsSystem = new NewsQuerySystem();
        await globalNewsSystem.initialize();
        isSystemInitialized = true;
        isInitializing = false;
        console.log('✅ Sistema inicializado correctamente');
        return globalNewsSystem;
    } catch (error) {
        isInitializing = false;
        console.error('❌ Error inicializando sistema:', error.message);
        throw error;
    }
}

// ========================================================================
// RUTAS HTTP
// ========================================================================

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/api/status', (req, res) => {
    res.json({
        ready: isSystemInitialized,
        initializing: isInitializing,
        timestamp: new Date().toISOString()
    });
});

app.post('/api/query', async (req, res) => {
    try {
        if (!isSystemInitialized) {
            await initializeSystemOnce();
        }
        
        const { text } = req.body;
        if (!text) {
            return res.status(400).json({ error: 'Texto requerido' });
        }
        
        const result = await globalNewsSystem.processQuery(text);
        res.json(result);
    } catch (error) {
        console.error('❌ Error en API query:', error.message);
        res.status(500).json({ error: error.message });
    }
});

// ========================================================================
// WEBSOCKET CON SOCKET.IO
// ========================================================================

io.on('connection', async (socket) => {
    console.log(`👤 Usuario conectado: ${socket.id}`);
    
    try {
        // Inicializar sistema si no está listo (solo una vez globalmente)
        if (!isSystemInitialized && !isInitializing) {
            socket.emit('systemStatus', { message: 'Inicializando sistema...', status: 'initializing' });
            await initializeSystemOnce();
        }
        
        // Enviar estado del sistema
        if (isSystemInitialized) {
            socket.emit('systemReady', {
                message: 'Sistema listo para consultas',
                config: {
                    llmProvider: 'Groq (Llama3)',
                    embeddingProvider: 'Google AI'
                }
            });
        } else if (isInitializing) {
            socket.emit('systemStatus', { message: 'Sistema inicializándose...', status: 'initializing' });
        }
        
    } catch (error) {
        console.error('❌ Error en conexión:', error.message);
        socket.emit('systemError', { message: 'Error inicializando el sistema: ' + error.message });
    }
    
    // Manejar consultas
    socket.on('query', async (data) => {
        try {
            if (!isSystemInitialized) {
                socket.emit('queryError', {
                    message: 'Sistema no está listo. Por favor espera.',
                    query: data.text
                });
                return;
            }
            
            console.log(`📝 Procesando consulta: "${data.text}"`);
            const result = await globalNewsSystem.processQuery(data.text);
            console.log(`✅ Respuesta enviada para: "${data.text}"`);
            socket.emit('queryResponse', result);
            
        } catch (error) {
            console.error('❌ Error procesando consulta:', error.message);
            socket.emit('queryError', {
                message: error.message,
                query: data.text
            });
        }
    });
    
    // Limpiar memoria
    socket.on('clearMemory', () => {
        try {
            if (globalNewsSystem) {
                globalNewsSystem.clearMemory();
                console.log('🧹 Memoria limpiada');
                socket.emit('memoryCleared', { message: 'Memoria limpiada correctamente' });
            }
        } catch (error) {
            console.error('❌ Error limpiando memoria:', error.message);
            socket.emit('queryError', { message: 'Error limpiando memoria: ' + error.message });
        }
    });
    
    // Desconexión
    socket.on('disconnect', () => {
        console.log(`👤 Usuario desconectado: ${socket.id}`);
    });
});

// ========================================================================
// INICIAR SERVIDOR
// ========================================================================

const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
    console.log(`
════════════════════════════════════════════════════════
🌐 SERVIDOR WEB INICIADO CORRECTAMENTE
════════════════════════════════════════════════════════
🔗 URL: http://localhost:${PORT}
🤖 Sistema: Groq (LLM) + Google AI (Embeddings)
💰 Costo: 100% GRATUITO
📱 Interfaz: Web moderna + responsive
💬 Chat: Tiempo real con Socket.IO
════════════════════════════════════════════════════════

🚀 Abre tu navegador en: http://localhost:${PORT}
📝 Escribe consultas de noticias o preguntas generales
✨ ¡Sistema listo para usar!
    `);
});

// ========================================================================
// MANEJO DE ERRORES Y CIERRE LIMPIO
// ========================================================================

process.on('uncaughtException', (error) => {
    console.error('❌ Error no capturado:', error.message);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Promesa rechazada:', reason);
});

process.on('SIGINT', () => {
    console.log('\n👋 Cerrando servidor...');
    server.close(() => {
        console.log('✅ Servidor cerrado correctamente');
        process.exit(0);
    });
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Terminando servidor...');
    server.close(() => {
        console.log('✅ Servidor terminado correctamente');
        process.exit(0);
    });
});
