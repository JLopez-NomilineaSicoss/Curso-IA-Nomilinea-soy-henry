// =================================================================
// Configuración simplificada de Jest para el proyecto
// =================================================================

export default {
    // Entorno de pruebas
    testEnvironment: 'node',
    
    // Directorio de pruebas
    testMatch: [
        '**/tests/**/*.test.js',
        '**/tests/**/*.spec.js'
    ],
    
    // Coverage
    collectCoverage: true,
    coverageDirectory: 'coverage',
    coverageReporters: ['text', 'html'],
    
    // Archivos a incluir en cobertura
    collectCoverageFrom: [
        'news-system.js',
        'config.js',
        'providers.js',
        'utils.js'
    ],
    
    // Configuración de timeouts
    testTimeout: 30000,
    
    // Verbose output
    verbose: true,
    
    // Clear mocks
    clearMocks: true
};
