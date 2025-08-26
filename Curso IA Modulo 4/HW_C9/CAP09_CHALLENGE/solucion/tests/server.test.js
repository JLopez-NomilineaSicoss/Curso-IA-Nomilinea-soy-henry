// =================================================================
// Pruebas del Servidor Web - Express + Socket.IO
// =================================================================

import { jest } from '@jest/globals';
import request from 'supertest';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { io as Client } from 'socket.io-client';
import express from 'express';
import { NewsQuerySystem } from '../news-system.js';

// Mock del sistema de noticias
jest.mock('../news-system.js');

describe('Servidor Web - API REST', () => {
    let app;
    let server;

    beforeEach(() => {
        // Crear aplicación Express para testing
        app = express();
        app.use(express.json());
        
        // Mock del sistema de noticias
        const mockNewsSystem = {
            isInitialized: true,
            processQuery: jest.fn(),
            clearMemory: jest.fn()
        };

        NewsQuerySystem.mockImplementation(() => mockNewsSystem);

        // Configurar rutas básicas
        app.get('/api/health', (req, res) => {
            res.json({ status: 'ok', timestamp: new Date().toISOString() });
        });

        app.get('/api/config', (req, res) => {
            res.json({
                llmProvider: 'Groq (Llama3)',
                embeddingProvider: 'Google AI',
                version: '1.0.0'
            });
        });

        app.post('/api/query', async (req, res) => {
            try {
                const { text } = req.body;
                
                if (!text || text.trim().length === 0) {
                    return res.status(400).json({ error: 'Consulta requerida' });
                }

                const result = await mockNewsSystem.processQuery(text);
                res.json(result);
            } catch (error) {
                res.status(500).json({ error: error.message });
            }
        });

        app.delete('/api/memory', (req, res) => {
            mockNewsSystem.clearMemory();
            res.json({ message: 'Memoria limpiada' });
        });
    });

    describe('Endpoints de Estado', () => {
        test('GET /api/health debe retornar estado ok', async () => {
            const response = await request(app)
                .get('/api/health')
                .expect(200);

            expect(response.body).toHaveProperty('status', 'ok');
            expect(response.body).toHaveProperty('timestamp');
        });

        test('GET /api/config debe retornar configuración', async () => {
            const response = await request(app)
                .get('/api/config')
                .expect(200);

            expect(response.body).toHaveProperty('llmProvider');
            expect(response.body).toHaveProperty('embeddingProvider');
            expect(response.body).toHaveProperty('version');
        });
    });

    describe('Endpoint de Consultas', () => {
        test('POST /api/query debe procesar consulta válida', async () => {
            // Configurar mock
            const mockResponse = {
                response: 'Respuesta de prueba',
                queryType: 'general',
                timestamp: new Date().toISOString()
            };

            const mockNewsSystem = NewsQuerySystem.mock.results[0].value;
            mockNewsSystem.processQuery.mockResolvedValue(mockResponse);

            // Ejecutar
            const response = await request(app)
                .post('/api/query')
                .send({ text: '¿Qué es la IA?' })
                .expect(200);

            // Verificar
            expect(response.body).toEqual(mockResponse);
            expect(mockNewsSystem.processQuery).toHaveBeenCalledWith('¿Qué es la IA?');
        });

        test('POST /api/query debe retornar error 400 para consulta vacía', async () => {
            const response = await request(app)
                .post('/api/query')
                .send({ text: '' })
                .expect(400);

            expect(response.body).toHaveProperty('error', 'Consulta requerida');
        });

        test('POST /api/query debe retornar error 400 para consulta faltante', async () => {
            const response = await request(app)
                .post('/api/query')
                .send({})
                .expect(400);

            expect(response.body).toHaveProperty('error', 'Consulta requerida');
        });

        test('POST /api/query debe manejar errores del sistema', async () => {
            // Configurar mock para fallar
            const mockNewsSystem = NewsQuerySystem.mock.results[0].value;
            mockNewsSystem.processQuery.mockRejectedValue(new Error('Error de procesamiento'));

            // Ejecutar
            const response = await request(app)
                .post('/api/query')
                .send({ text: 'consulta de prueba' })
                .expect(500);

            // Verificar
            expect(response.body).toHaveProperty('error', 'Error de procesamiento');
        });
    });

    describe('Endpoint de Memoria', () => {
        test('DELETE /api/memory debe limpiar memoria', async () => {
            const mockNewsSystem = NewsQuerySystem.mock.results[0].value;

            const response = await request(app)
                .delete('/api/memory')
                .expect(200);

            expect(response.body).toHaveProperty('message', 'Memoria limpiada');
            expect(mockNewsSystem.clearMemory).toHaveBeenCalled();
        });
    });
});

describe('Servidor WebSocket - Socket.IO', () => {
    let httpServer;
    let io;
    let clientSocket;
    let mockNewsSystem;

    beforeEach((done) => {
        // Crear servidor HTTP
        const app = express();
        httpServer = createServer(app);
        
        // Configurar Socket.IO
        io = new Server(httpServer, {
            cors: {
                origin: "*",
                methods: ["GET", "POST"]
            }
        });

        // Mock del sistema de noticias
        mockNewsSystem = {
            initialize: jest.fn().mockResolvedValue(),
            processQuery: jest.fn(),
            clearMemory: jest.fn(),
            isInitialized: false
        };

        NewsQuerySystem.mockImplementation(() => mockNewsSystem);

        // Configurar eventos Socket.IO
        io.on('connection', (socket) => {
            console.log('Cliente conectado:', socket.id);

            // Inicializar sistema si no está listo
            if (!mockNewsSystem.isInitialized) {
                mockNewsSystem.initialize()
                    .then(() => {
                        mockNewsSystem.isInitialized = true;
                        socket.emit('systemReady', {
                            message: 'Sistema inicializado',
                            config: {
                                llmProvider: 'Groq (Llama3)',
                                embeddingProvider: 'Google AI'
                            }
                        });
                    })
                    .catch((error) => {
                        socket.emit('systemError', {
                            message: error.message
                        });
                    });
            } else {
                socket.emit('systemReady', {
                    message: 'Sistema ya inicializado',
                    config: {
                        llmProvider: 'Groq (Llama3)',
                        embeddingProvider: 'Google AI'
                    }
                });
            }

            socket.on('query', async (data) => {
                try {
                    const result = await mockNewsSystem.processQuery(data.text);
                    socket.emit('queryResponse', result);
                } catch (error) {
                    socket.emit('queryError', {
                        message: error.message,
                        query: data.text
                    });
                }
            });

            socket.on('clearMemory', () => {
                mockNewsSystem.clearMemory();
                socket.emit('memoryCleared');
            });

            socket.on('disconnect', () => {
                console.log('Cliente desconectado:', socket.id);
            });
        });

        // Iniciar servidor
        httpServer.listen(() => {
            const port = httpServer.address().port;
            
            // Crear cliente de prueba
            clientSocket = Client(`http://localhost:${port}`);
            clientSocket.on('connect', done);
        });
    });

    afterEach(() => {
        if (clientSocket) {
            clientSocket.close();
        }
        if (httpServer) {
            httpServer.close();
        }
    });

    test('debe conectar cliente y emitir systemReady', (done) => {
        clientSocket.on('systemReady', (data) => {
            expect(data).toHaveProperty('message');
            expect(data).toHaveProperty('config');
            expect(data.config).toHaveProperty('llmProvider');
            expect(data.config).toHaveProperty('embeddingProvider');
            done();
        });
    });

    test('debe procesar consulta y responder', (done) => {
        // Configurar mock
        const mockResponse = {
            response: 'Respuesta de prueba WebSocket',
            queryType: 'general',
            timestamp: new Date().toISOString()
        };

        mockNewsSystem.processQuery.mockResolvedValue(mockResponse);

        // Configurar listener
        clientSocket.on('queryResponse', (data) => {
            expect(data).toEqual(mockResponse);
            expect(mockNewsSystem.processQuery).toHaveBeenCalledWith('¿Cómo funciona WebSocket?');
            done();
        });

        // Enviar consulta
        clientSocket.emit('query', { text: '¿Cómo funciona WebSocket?' });
    });

    test('debe manejar errores en consultas', (done) => {
        // Configurar mock para fallar
        mockNewsSystem.processQuery.mockRejectedValue(new Error('Error WebSocket'));

        // Configurar listener
        clientSocket.on('queryError', (data) => {
            expect(data).toHaveProperty('message', 'Error WebSocket');
            expect(data).toHaveProperty('query', 'consulta con error');
            done();
        });

        // Enviar consulta que fallará
        clientSocket.emit('query', { text: 'consulta con error' });
    });

    test('debe limpiar memoria cuando se solicite', (done) => {
        // Configurar listener
        clientSocket.on('memoryCleared', () => {
            expect(mockNewsSystem.clearMemory).toHaveBeenCalled();
            done();
        });

        // Solicitar limpieza de memoria
        clientSocket.emit('clearMemory');
    });

    test('debe manejar múltiples clientes simultáneamente', (done) => {
        // Crear segundo cliente
        const secondClient = Client(`http://localhost:${httpServer.address().port}`);
        
        let readyCount = 0;
        const checkBothReady = () => {
            readyCount++;
            if (readyCount === 2) {
                secondClient.close();
                done();
            }
        };

        clientSocket.on('systemReady', checkBothReady);
        secondClient.on('systemReady', checkBothReady);
    });

    test('debe emitir systemError si falla la inicialización', (done) => {
        // Crear nuevo servidor que falle en la inicialización
        const failingServer = createServer();
        const failingIO = new Server(failingServer);
        
        const failingNewsSystem = {
            initialize: jest.fn().mockRejectedValue(new Error('Fallo de inicialización')),
            isInitialized: false
        };

        failingIO.on('connection', (socket) => {
            failingNewsSystem.initialize()
                .catch((error) => {
                    socket.emit('systemError', {
                        message: error.message
                    });
                });
        });

        failingServer.listen(() => {
            const failingClient = Client(`http://localhost:${failingServer.address().port}`);
            
            failingClient.on('systemError', (data) => {
                expect(data).toHaveProperty('message', 'Fallo de inicialización');
                failingClient.close();
                failingServer.close();
                done();
            });
        });
    });
});

describe('Integración Completa del Servidor', () => {
    let app;
    let httpServer;
    let io;
    let clientSocket;

    beforeEach((done) => {
        // Crear aplicación completa
        app = express();
        app.use(express.json());
        app.use(express.static('public'));

        httpServer = createServer(app);
        io = new Server(httpServer);

        // Mock del sistema
        const mockNewsSystem = {
            initialize: jest.fn().mockResolvedValue(),
            processQuery: jest.fn(),
            clearMemory: jest.fn(),
            isInitialized: true
        };

        NewsQuerySystem.mockImplementation(() => mockNewsSystem);

        // Configurar rutas
        app.get('/api/health', (req, res) => {
            res.json({ status: 'ok' });
        });

        // Configurar Socket.IO
        io.on('connection', (socket) => {
            socket.emit('systemReady', {
                config: {
                    llmProvider: 'Groq',
                    embeddingProvider: 'Google'
                }
            });
        });

        // Iniciar servidor
        httpServer.listen(() => {
            const port = httpServer.address().port;
            clientSocket = Client(`http://localhost:${port}`);
            clientSocket.on('connect', done);
        });
    });

    afterEach(() => {
        if (clientSocket) {
            clientSocket.close();
        }
        if (httpServer) {
            httpServer.close();
        }
    });

    test('debe servir API REST y WebSocket simultáneamente', async () => {
        // Probar API REST
        const restResponse = await request(app)
            .get('/api/health')
            .expect(200);

        expect(restResponse.body).toHaveProperty('status', 'ok');

        // Probar WebSocket
        return new Promise((resolve) => {
            clientSocket.on('systemReady', (data) => {
                expect(data).toHaveProperty('config');
                resolve();
            });
        });
    });
});
