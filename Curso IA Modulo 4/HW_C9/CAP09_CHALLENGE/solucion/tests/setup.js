// =================================================================
// Setup para Jest - Configuración global de pruebas
// =================================================================

import { jest } from '@jest/globals';

// Configuración global antes de todas las pruebas
beforeAll(() => {
    console.log('🧪 Iniciando suite de pruebas del Sistema de Consulta de Noticias');
    
    // Configurar timeout global
    jest.setTimeout(30000);
    
    // Mock de console.log para reducir ruido en tests
    global.console = {
        ...global.console,
        log: jest.fn(),
        debug: jest.fn(),
        info: jest.fn(),
        warn: jest.fn(),
        error: jest.fn()
    };
});

// Configuración antes de cada prueba
beforeEach(() => {
    // Limpiar todas las variables de entorno mock
    jest.clearAllMocks();
    
    // Configurar variables de entorno por defecto para pruebas
    process.env.NODE_ENV = 'test';
    process.env.GROQ_API_KEY = 'test-groq-key';
    process.env.GOOGLE_AI_API_KEY = 'test-google-key';
    process.env.SERPER_API_KEY = 'test-serper-key';
    process.env.PORT = '3001';
});

// Configuración después de cada prueba
afterEach(() => {
    // Limpiar mocks
    jest.clearAllMocks();
    
    // Limpiar timers si existen
    if (jest.getTimerCount() > 0) {
        jest.clearAllTimers();
    }
});

// Configuración después de todas las pruebas
afterAll(() => {
    console.log('✅ Suite de pruebas completada');
    
    // Restaurar console original
    global.console = require('console');
});

// Mock global de fetch para todas las pruebas
global.fetch = jest.fn();

// Mock global de setTimeout y setInterval
global.setTimeout = jest.fn((cb) => cb());
global.setInterval = jest.fn((cb) => cb());
global.clearTimeout = jest.fn();
global.clearInterval = jest.fn();

// Utilidades de prueba personalizadas
global.testUtils = {
    // Crear configuración mock
    createMockConfig: (overrides = {}) => ({
        providers: {
            groq: {
                apiKey: 'test-groq-key',
                model: 'llama3-8b-8192',
                ...overrides.groq
            },
            google: {
                apiKey: 'test-google-key', 
                model: 'embedding-001',
                ...overrides.google
            },
            openai: {
                apiKey: 'test-openai-key',
                model: 'gpt-3.5-turbo',
                ...overrides.openai
            }
        },
        serper: {
            apiKey: 'test-serper-key',
            ...overrides.serper
        },
        ...overrides.global
    }),
    
    // Crear respuesta mock de noticias
    createMockNewsResponse: (count = 2) => ({
        organic: Array.from({ length: count }, (_, i) => ({
            title: `Noticia ${i + 1}`,
            snippet: `Descripción de la noticia ${i + 1}`,
            link: `https://example.com/news${i + 1}`,
            date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
        }))
    }),
    
    // Crear respuesta mock del LLM
    createMockLLMResponse: (content) => ({
        content: typeof content === 'string' ? content : JSON.stringify(content)
    }),
    
    // Esperar por un tiempo determinado (para pruebas asíncronas)
    delay: (ms) => new Promise(resolve => setTimeout(resolve, ms)),
    
    // Verificar que un objeto tenga las propiedades esperadas
    expectToHaveProperties: (obj, properties) => {
        properties.forEach(prop => {
            expect(obj).toHaveProperty(prop);
        });
    },
    
    // Crear mock de Socket.IO cliente
    createMockSocketClient: () => ({
        emit: jest.fn(),
        on: jest.fn(),
        off: jest.fn(),
        connect: jest.fn(),
        disconnect: jest.fn(),
        close: jest.fn()
    })
};

// Manejo de errores no capturados en pruebas
process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Promesa rechazada no manejada en pruebas:', reason);
});

process.on('uncaughtException', (error) => {
    console.error('❌ Excepción no capturada en pruebas:', error);
});

// Configuración de matchers personalizados para Jest
expect.extend({
    // Verificar que una respuesta tenga el formato correcto
    toBeValidQueryResponse(received) {
        const pass = received &&
            typeof received.response === 'string' &&
            ['news', 'general'].includes(received.queryType) &&
            received.timestamp &&
            (received.sources === undefined || Array.isArray(received.sources));

        if (pass) {
            return {
                message: () => `Se esperaba que ${JSON.stringify(received)} NO fuera una respuesta válida`,
                pass: true
            };
        } else {
            return {
                message: () => `Se esperaba que ${JSON.stringify(received)} fuera una respuesta válida con formato: {response: string, queryType: 'news'|'general', timestamp: string, sources?: array}`,
                pass: false
            };
        }
    },
    
    // Verificar que una configuración tenga las claves API necesarias
    toHaveValidAPIKeys(received) {
        const pass = received &&
            received.providers &&
            received.providers.groq &&
            received.providers.groq.apiKey &&
            received.providers.google &&
            received.providers.google.apiKey &&
            received.serper &&
            received.serper.apiKey;

        if (pass) {
            return {
                message: () => `Se esperaba que la configuración NO tuviera claves API válidas`,
                pass: true
            };
        } else {
            return {
                message: () => `Se esperaba que la configuración tuviera claves API válidas para Groq, Google y Serper`,
                pass: false
            };
        }
    }
});
