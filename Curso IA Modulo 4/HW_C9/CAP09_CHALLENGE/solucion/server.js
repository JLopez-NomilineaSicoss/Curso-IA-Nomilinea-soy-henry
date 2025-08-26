/**
 * Servidor Web Simple para el Sistema de Consulta de Noticias
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

// Variables globales
let newsSystem = null;
let isSystemReady = false;

// ========================================================================
// RUTAS HTTP
// ========================================================================

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/api/status', (req, res) => {
    res.json({
        ready: isSystemReady,
        timestamp: new Date().toISOString()
    });
});

// ========================================================================
// WEBSOCKET CON SOCKET.IO
// ========================================================================

io.on('connection', async (socket) => {
    console.log(`👤 Usuario conectado: ${socket.id}`);
    
    // Inicializar sistema si no está listo
    if (!newsSystem) {
        try {
            console.log('🚀 Inicializando sistema de noticias...');
            newsSystem = new NewsQuerySystem();
            await newsSystem.initialize();
            isSystemReady = true;
            console.log('✅ Sistema listo');
        } catch (error) {
            console.error('❌ Error:', error.message);
            socket.emit('systemError', { message: error.message });
            return;
        }
    }
    
    // Enviar estado del sistema
    socket.emit('systemReady', {
        message: 'Sistema listo',
        config: {
            llmProvider: 'Groq (Llama3)',
            embeddingProvider: 'Google AI'
        }
    });
    
    // Manejar consultas
    socket.on('query', async (data) => {
        try {
            console.log(`📝 Consulta recibida: ${data.text}`);
            const result = await newsSystem.processQuery(data.text);
            console.log(`✅ Respuesta enviada`);
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
        if (newsSystem) {
            newsSystem.clearMemory();
            socket.emit('memoryCleared');
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
============================================================
🌐 SERVIDOR WEB INICIADO
============================================================
🔗 URL: http://localhost:${PORT}
🤖 Sistema: GROQ + GOOGLE
💰 Costo: GRATUITO (APIs sin costo)
============================================================

🚀 Abre tu navegador y ve a: http://localhost:${PORT}
    `);
});

// Manejo de errores
process.on('uncaughtException', (error) => {
    console.error('❌ Error no capturado:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Promesa rechazada:', reason);
});

process.on('SIGINT', () => {
    console.log('\n👋 Cerrando servidor...');
    server.close(() => {
        process.exit(0);
    });
});
        if (!newsSystem) {
            return res.status(503).json({ error: 'Sistema no inicializado' });
        }
        
        const stats = await newsSystem.getStats();
        res.json(stats);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

/**
 * API para limpiar memoria conversacional
 */
app.post('/api/clear-memory', async (req, res) => {
    try {
        if (!newsSystem) {
            return res.status(503).json({ error: 'Sistema no inicializado' });
        }
        
        await newsSystem.clearMemory();
        res.json({ success: true, message: 'Memoria limpiada' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ========================================================================
// SOCKET.IO - COMUNICACIÓN EN TIEMPO REAL
// ========================================================================

io.on('connection', (socket) => {
    console.log('👤 Usuario conectado:', socket.id);
    
    // Enviar estado del sistema al conectarse
    socket.emit('system-status', {
        ready: isSystemReady,
        config: {
            llmProvider: CONFIG.llm.provider,
            embeddingProvider: CONFIG.embeddings.provider
        }
    });
    
    /**
     * Manejar mensajes del chat
     */
    socket.on('chat-message', async (data) => {
        const { message, timestamp } = data;
        const startTime = Date.now();
        
        try {
            // Validar que el sistema esté listo
            if (!isSystemReady || !newsSystem) {
                socket.emit('chat-response', {
                    error: true,
                    message: 'El sistema aún se está inicializando. Por favor, espera un momento.',
                    timestamp: new Date().toISOString()
                });
                return;
            }
            
            // Validar la pregunta
            const validation = validateQuestion(message);
            if (!validation.isValid) {
                socket.emit('chat-response', {
                    error: true,
                    message: `⚠️ ${validation.reason}`,
                    timestamp: new Date().toISOString()
                });
                return;
            }
            
            // Indicar que está procesando
            socket.emit('typing', true);
            
            // Procesar la pregunta
            const response = await newsSystem.processQuery(message);
            const processingTime = Date.now() - startTime;
            
            // Enviar respuesta
            socket.emit('chat-response', {
                message: response.content,
                queryType: response.queryType,
                processingTime,
                timestamp: new Date().toISOString(),
                error: false
            });
            
            // Log métricas
            logMetrics(response.queryType, processingTime, true);
            
        } catch (error) {
            const processingTime = Date.now() - startTime;
            const errorMessage = handleSystemError(error, 'procesamiento de pregunta');
            
            socket.emit('chat-response', {
                error: true,
                message: errorMessage,
                timestamp: new Date().toISOString()
            });
            
            logMetrics('error', processingTime, false);
        } finally {
            socket.emit('typing', false);
        }
    });
    
    /**
     * Manejar comando de limpiar memoria
     */
    socket.on('clear-memory', async () => {
        try {
            if (newsSystem) {
                await newsSystem.clearMemory();
                socket.emit('memory-cleared', {
                    success: true,
                    message: '🧹 Memoria de conversación limpiada'
                });
            }
        } catch (error) {
            socket.emit('memory-cleared', {
                success: false,
                message: 'Error limpiando memoria'
            });
        }
    });
    
    /**
     * Manejar solicitud de estadísticas
     */
    socket.on('get-stats', async () => {
        try {
            if (newsSystem) {
                const stats = await newsSystem.getStats();
                socket.emit('stats-update', stats);
            }
        } catch (error) {
            socket.emit('stats-error', { message: error.message });
        }
    });
    
    /**
     * Manejar desconexión
     */
    socket.on('disconnect', () => {
        console.log('👤 Usuario desconectado:', socket.id);
    });
});

// ========================================================================
// MANEJO DE ERRORES Y ARRANQUE DEL SERVIDOR
// ========================================================================

const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
    console.log('\n' + '='.repeat(60));
    console.log('🌐 SERVIDOR WEB INICIADO');
    console.log('='.repeat(60));
    console.log(`🔗 URL: http://localhost:${PORT}`);
    console.log(`🤖 Sistema: ${CONFIG.llm.provider.toUpperCase()} + ${CONFIG.embeddings.provider.toUpperCase()}`);
    console.log(`💰 Costo: GRATUITO (APIs sin costo)`);
    console.log('='.repeat(60));
    console.log('');
    console.log('🚀 Abre tu navegador y ve a: http://localhost:3000');
    console.log('');
});

// Manejo de cierre graceful
process.on('SIGINT', () => {
    console.log('\n👋 Cerrando servidor...');
    server.close(() => {
        console.log('✅ Servidor cerrado');
        process.exit(0);
    });
});

export default app;
