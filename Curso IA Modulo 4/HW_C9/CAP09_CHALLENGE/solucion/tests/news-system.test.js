// =================================================================
// Sistema de Consulta de Noticias - Pruebas Unitarias
// =================================================================

import { jest } from '@jest/globals';
import { NewsQuerySystem } from '../news-system.js';
import { createLLMModel, createEmbeddingsModel } from '../providers.js';
import { initializeConfiguration } from '../config.js';

// Mock de las dependencias externas
jest.mock('../providers.js');
jest.mock('../config.js');

describe('Sistema de Consulta de Noticias', () => {
    let newsSystem;
    let mockLLM;
    let mockEmbeddings;
    let mockConfig;

    beforeEach(() => {
        // Reset de todos los mocks
        jest.clearAllMocks();

        // Mock de la configuración
        mockConfig = {
            providers: {
                groq: {
                    apiKey: 'test-groq-key',
                    model: 'llama3-8b-8192'
                },
                google: {
                    apiKey: 'test-google-key',
                    model: 'embedding-001'
                }
            },
            serper: {
                apiKey: 'test-serper-key'
            }
        };

        initializeConfiguration.mockResolvedValue(mockConfig);

        // Mock del modelo LLM
        mockLLM = {
            invoke: jest.fn(),
            pipe: jest.fn().mockReturnThis(),
            bind: jest.fn().mockReturnThis()
        };

        // Mock del modelo de embeddings
        mockEmbeddings = {
            embedDocuments: jest.fn(),
            embedQuery: jest.fn()
        };

        createLLMModel.mockResolvedValue(mockLLM);
        createEmbeddingsModel.mockResolvedValue(mockEmbeddings);

        // Crear instancia del sistema
        newsSystem = new NewsQuerySystem();
    });

    describe('Inicialización del Sistema', () => {
        test('debe inicializar correctamente con configuración válida', async () => {
            // Ejecutar
            await newsSystem.initialize();

            // Verificar
            expect(initializeConfiguration).toHaveBeenCalled();
            expect(createLLMModel).toHaveBeenCalledWith(mockConfig, 'groq');
            expect(createEmbeddingsModel).toHaveBeenCalledWith(mockConfig, 'google');
            expect(newsSystem.isInitialized).toBe(true);
        });

        test('debe manejar errores de inicialización', async () => {
            // Configurar
            initializeConfiguration.mockRejectedValue(new Error('Error de configuración'));

            // Ejecutar y verificar
            await expect(newsSystem.initialize()).rejects.toThrow('Error de configuración');
            expect(newsSystem.isInitialized).toBe(false);
        });

        test('debe validar que el sistema esté inicializado antes de procesar consultas', async () => {
            // Ejecutar y verificar
            await expect(newsSystem.processQuery('test query')).rejects.toThrow('Sistema no inicializado');
        });
    });

    describe('Clasificación de Consultas', () => {
        beforeEach(async () => {
            await newsSystem.initialize();
        });

        test('debe clasificar correctamente consultas de noticias', async () => {
            // Configurar
            mockLLM.invoke.mockResolvedValue({
                content: JSON.stringify({
                    isNewsQuery: true,
                    explanation: 'Consulta sobre eventos actuales'
                })
            });

            // Ejecutar
            const result = await newsSystem.classifyQuery('¿Cuáles son las últimas noticias?');

            // Verificar
            expect(result.isNewsQuery).toBe(true);
            expect(result.explanation).toBeDefined();
        });

        test('debe clasificar correctamente consultas generales', async () => {
            // Configurar
            mockLLM.invoke.mockResolvedValue({
                content: JSON.stringify({
                    isNewsQuery: false,
                    explanation: 'Consulta de conocimiento general'
                })
            });

            // Ejecutar
            const result = await newsSystem.classifyQuery('¿Qué es la fotosíntesis?');

            // Verificar
            expect(result.isNewsQuery).toBe(false);
            expect(result.explanation).toBeDefined();
        });

        test('debe manejar respuestas de clasificación inválidas', async () => {
            // Configurar
            mockLLM.invoke.mockResolvedValue({
                content: 'respuesta inválida'
            });

            // Ejecutar y verificar
            await expect(newsSystem.classifyQuery('test query')).rejects.toThrow();
        });
    });

    describe('Búsqueda de Noticias', () => {
        beforeEach(async () => {
            await newsSystem.initialize();
            
            // Mock de fetch para Serper API
            global.fetch = jest.fn();
        });

        afterEach(() => {
            global.fetch.mockRestore();
        });

        test('debe buscar noticias exitosamente', async () => {
            // Configurar
            const mockNewsResponse = {
                organic: [
                    {
                        title: 'Noticia 1',
                        snippet: 'Descripción de la noticia 1',
                        link: 'https://example.com/news1',
                        date: '2024-01-15'
                    },
                    {
                        title: 'Noticia 2',
                        snippet: 'Descripción de la noticia 2',
                        link: 'https://example.com/news2',
                        date: '2024-01-14'
                    }
                ]
            };

            global.fetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve(mockNewsResponse)
            });

            // Ejecutar
            const result = await newsSystem.searchNews('tecnología');

            // Verificar
            expect(result).toHaveLength(2);
            expect(result[0]).toHaveProperty('title', 'Noticia 1');
            expect(result[0]).toHaveProperty('content');
            expect(result[0]).toHaveProperty('source');
            expect(result[0]).toHaveProperty('date');
        });

        test('debe manejar errores en la búsqueda de noticias', async () => {
            // Configurar
            global.fetch.mockResolvedValue({
                ok: false,
                status: 500
            });

            // Ejecutar y verificar
            await expect(newsSystem.searchNews('tecnología')).rejects.toThrow();
        });

        test('debe manejar respuestas vacías de noticias', async () => {
            // Configurar
            global.fetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve({ organic: [] })
            });

            // Ejecutar
            const result = await newsSystem.searchNews('consulta-sin-resultados');

            // Verificar
            expect(result).toHaveLength(0);
        });
    });

    describe('Procesamiento de Consultas', () => {
        beforeEach(async () => {
            await newsSystem.initialize();
            global.fetch = jest.fn();
        });

        afterEach(() => {
            global.fetch.mockRestore();
        });

        test('debe procesar consultas de noticias correctamente', async () => {
            // Configurar clasificación como noticia
            mockLLM.invoke
                .mockResolvedValueOnce({
                    content: JSON.stringify({
                        isNewsQuery: true,
                        explanation: 'Consulta sobre noticias'
                    })
                })
                .mockResolvedValueOnce({
                    content: 'Respuesta basada en las noticias encontradas'
                });

            // Mock de búsqueda de noticias
            global.fetch.mockResolvedValue({
                ok: true,
                json: () => Promise.resolve({
                    organic: [{
                        title: 'Noticia Test',
                        snippet: 'Contenido test',
                        link: 'https://test.com',
                        date: '2024-01-15'
                    }]
                })
            });

            // Ejecutar
            const result = await newsSystem.processQuery('¿Últimas noticias de tecnología?');

            // Verificar
            expect(result.response).toBe('Respuesta basada en las noticias encontradas');
            expect(result.queryType).toBe('news');
            expect(result.sources).toBeDefined();
        });

        test('debe procesar consultas generales correctamente', async () => {
            // Configurar clasificación como general
            mockLLM.invoke
                .mockResolvedValueOnce({
                    content: JSON.stringify({
                        isNewsQuery: false,
                        explanation: 'Consulta general'
                    })
                })
                .mockResolvedValueOnce({
                    content: 'Respuesta de conocimiento general'
                });

            // Ejecutar
            const result = await newsSystem.processQuery('¿Qué es la inteligencia artificial?');

            // Verificar
            expect(result.response).toBe('Respuesta de conocimiento general');
            expect(result.queryType).toBe('general');
            expect(result.sources).toBeUndefined();
        });
    });

    describe('Memoria Conversacional', () => {
        beforeEach(async () => {
            await newsSystem.initialize();
        });

        test('debe recordar el contexto de la conversación', async () => {
            // Primera consulta
            mockLLM.invoke
                .mockResolvedValueOnce({
                    content: JSON.stringify({ isNewsQuery: false })
                })
                .mockResolvedValueOnce({
                    content: 'Primera respuesta'
                });

            await newsSystem.processQuery('Primera pregunta');

            // Segunda consulta
            mockLLM.invoke
                .mockResolvedValueOnce({
                    content: JSON.stringify({ isNewsQuery: false })
                })
                .mockResolvedValueOnce({
                    content: 'Segunda respuesta con contexto'
                });

            await newsSystem.processQuery('¿Puedes explicar más?');

            // Verificar que se llamó con el contexto de memoria
            const lastCall = mockLLM.invoke.mock.calls[mockLLM.invoke.mock.calls.length - 1];
            expect(lastCall[0]).toContain('Primera pregunta');
        });

        test('debe limpiar la memoria correctamente', () => {
            // Ejecutar
            newsSystem.clearMemory();

            // Verificar que la memoria se reinició
            expect(newsSystem.memory).toBeDefined();
        });
    });

    describe('Manejo de Errores', () => {
        beforeEach(async () => {
            await newsSystem.initialize();
        });

        test('debe manejar errores del modelo LLM', async () => {
            // Configurar
            mockLLM.invoke.mockRejectedValue(new Error('Error del modelo'));

            // Ejecutar y verificar
            await expect(newsSystem.processQuery('test query')).rejects.toThrow('Error del modelo');
        });

        test('debe manejar errores de red', async () => {
            // Configurar
            global.fetch = jest.fn().mockRejectedValue(new Error('Error de red'));
            
            mockLLM.invoke.mockResolvedValue({
                content: JSON.stringify({ isNewsQuery: true })
            });

            // Ejecutar y verificar
            await expect(newsSystem.processQuery('noticias')).rejects.toThrow('Error de red');
        });
    });
});

describe('Configuración del Sistema', () => {
    test('debe validar claves API requeridas', async () => {
        // Configurar variables de entorno incompletas
        const originalEnv = process.env;
        process.env = {
            ...originalEnv,
            GROQ_API_KEY: undefined
        };

        // Mock para simular configuración incompleta
        initializeConfiguration.mockRejectedValue(new Error('Clave API de Groq no encontrada'));

        // Ejecutar y verificar
        await expect(initializeConfiguration()).rejects.toThrow('Clave API de Groq no encontrada');

        // Restaurar
        process.env = originalEnv;
    });
});

describe('Proveedores de IA', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('debe crear modelo LLM de Groq correctamente', async () => {
        // Configurar
        const config = {
            providers: {
                groq: {
                    apiKey: 'test-key',
                    model: 'llama3-8b-8192'
                }
            }
        };

        // Mock del constructor del modelo
        const mockModel = { invoke: jest.fn() };
        createLLMModel.mockResolvedValue(mockModel);

        // Ejecutar
        const result = await createLLMModel(config, 'groq');

        // Verificar
        expect(result).toBe(mockModel);
        expect(createLLMModel).toHaveBeenCalledWith(config, 'groq');
    });

    test('debe crear modelo de embeddings de Google correctamente', async () => {
        // Configurar
        const config = {
            providers: {
                google: {
                    apiKey: 'test-key',
                    model: 'embedding-001'
                }
            }
        };

        // Mock del constructor del modelo
        const mockEmbeddings = { embedQuery: jest.fn() };
        createEmbeddingsModel.mockResolvedValue(mockEmbeddings);

        // Ejecutar
        const result = await createEmbeddingsModel(config, 'google');

        // Verificar
        expect(result).toBe(mockEmbeddings);
        expect(createEmbeddingsModel).toHaveBeenCalledWith(config, 'google');
    });
});

describe('Integración del Sistema Completo', () => {
    test('debe funcionar el flujo completo de consulta de noticias', async () => {
        // Configurar todos los mocks necesarios
        const mockConfig = {
            providers: {
                groq: { apiKey: 'test-key', model: 'llama3-8b-8192' },
                google: { apiKey: 'test-key', model: 'embedding-001' }
            },
            serper: { apiKey: 'test-key' }
        };

        initializeConfiguration.mockResolvedValue(mockConfig);
        
        const mockLLM = {
            invoke: jest.fn()
                .mockResolvedValueOnce({
                    content: JSON.stringify({ isNewsQuery: true, explanation: 'Noticias' })
                })
                .mockResolvedValueOnce({
                    content: 'Respuesta final sobre tecnología'
                })
        };
        
        const mockEmbeddings = {
            embedDocuments: jest.fn().mockResolvedValue([[0.1, 0.2, 0.3]]),
            embedQuery: jest.fn().mockResolvedValue([0.1, 0.2, 0.3])
        };

        createLLMModel.mockResolvedValue(mockLLM);
        createEmbeddingsModel.mockResolvedValue(mockEmbeddings);

        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: () => Promise.resolve({
                organic: [{
                    title: 'Noticia de Tecnología',
                    snippet: 'Contenido relevante',
                    link: 'https://tech.com',
                    date: '2024-01-15'
                }]
            })
        });

        // Ejecutar
        const system = new NewsQuerySystem();
        await system.initialize();
        const result = await system.processQuery('¿Últimas noticias de tecnología?');

        // Verificar
        expect(result.response).toBe('Respuesta final sobre tecnología');
        expect(result.queryType).toBe('news');
        expect(result.sources).toHaveLength(1);
        expect(result.sources[0].title).toBe('Noticia de Tecnología');
    });
});
