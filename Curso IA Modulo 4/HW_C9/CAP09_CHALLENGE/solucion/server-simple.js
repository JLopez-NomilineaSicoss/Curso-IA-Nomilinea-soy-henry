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
