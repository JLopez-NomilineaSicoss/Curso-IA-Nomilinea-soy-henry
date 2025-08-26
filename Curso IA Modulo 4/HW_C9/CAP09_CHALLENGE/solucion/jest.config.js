// =================================================================
// Configuración de Jest para el proyecto
// =================================================================

export default {
    // Tipo de módulo
    preset: null,
    
    // Entorno de pruebas
    testEnvironment: 'node',
    
    // Soporte para ES modules
    extensionsToTreatAsEsm: ['.js'],
    
    // Transformaciones
    transform: {},
    
    // Configuración de módulos
    moduleNameMapping: {
        '^(\\.{1,2}/.*)\\.js$': '$1'
    },
    
    // Directorio de pruebas
    testMatch: [
        '**/tests/**/*.test.js',
        '**/?(*.)+(spec|test).js'
    ],
    
    // Archivos a ignorar
    testPathIgnorePatterns: [
        '/node_modules/',
        '/public/'
    ],
    
    // Configuración de cobertura
    collectCoverageFrom: [
        '*.js',
        '!main.js',
        '!server.js',
        '!jest.config.js',
        '!coverage/**',
        '!tests/**',
        '!public/**',
        '!node_modules/**'
    ],
    
    // Directorio de reportes de cobertura
    coverageDirectory: 'coverage',
    
    // Reportes de cobertura
    coverageReporters: [
        'text',
        'text-summary',
        'html',
        'lcov'
    ],
    
    // Umbrales de cobertura
    coverageThreshold: {
        global: {
            branches: 70,
            functions: 75,
            lines: 80,
            statements: 80
        }
    },
    
    // Setup antes de las pruebas
    setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
    
    // Configuración para mocks
    clearMocks: true,
    restoreMocks: true,
    
    // Timeout para pruebas
    testTimeout: 30000,
    
    // Configuración verbose
    verbose: true,
    
    // Configuración para ES modules con Node.js
    globals: {
        'NODE_OPTIONS': '--experimental-vm-modules'
    }
};
