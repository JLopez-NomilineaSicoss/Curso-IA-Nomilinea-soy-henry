/**
 * Script de Pruebas del Sistema
 * 
 * Ejecuta pruebas básicas para verificar que el sistema funciona correctamente.
 */

import { CONFIG, initializeConfig } from './config.js';
import { checkProviderAvailability, getOptimalConfiguration } from './providers.js';
import { validateQuestion, generateDocumentStats, formatDocumentsAsString } from './utils.js';

console.log('🧪 EJECUTANDO PRUEBAS DEL SISTEMA');
console.log('=' .repeat(50));

async function runTests() {
    let passed = 0;
    let failed = 0;
    
    // Test 1: Configuración
    console.log('\n📋 Test 1: Configuración del sistema');
    try {
        initializeConfig();
        console.log('✅ Configuración cargada correctamente');
        passed++;
    } catch (error) {
        console.log('❌ Error en configuración:', error.message);
        failed++;
    }
    
    // Test 2: Verificación de proveedores
    console.log('\n📋 Test 2: Verificación de proveedores');
    try {
        const availability = checkProviderAvailability();
        const hasGroq = availability.groq;
        const hasGoogle = availability.google;
        
        if (hasGroq && hasGoogle) {
            console.log('✅ Configuración óptima detectada (Groq + Google)');
            passed++;
        } else if (availability.openai) {
            console.log('✅ Configuración OpenAI detectada (funcional pero pagada)');
            passed++;
        } else {
            console.log('❌ No se detectaron proveedores válidos');
            failed++;
        }
    } catch (error) {
        console.log('❌ Error verificando proveedores:', error.message);
        failed++;
    }
    
    // Test 3: Configuración óptima
    console.log('\n📋 Test 3: Recomendaciones de configuración');
    try {
        const optimal = getOptimalConfiguration();
        if (optimal.llm && optimal.embeddings) {
            console.log('✅ Recomendaciones generadas correctamente');
            passed++;
        } else {
            console.log('❌ Error generando recomendaciones');
            failed++;
        }
    } catch (error) {
        console.log('❌ Error en recomendaciones:', error.message);
        failed++;
    }
    
    // Test 4: Validación de preguntas
    console.log('\n📋 Test 4: Validación de preguntas');
    const testCases = [
        { input: '', expected: false },
        { input: 'a', expected: false },
        { input: '¿Cuáles son las noticias de hoy?', expected: true },
        { input: 'a'.repeat(600), expected: false }
    ];
    
    let validationPassed = true;
    for (const testCase of testCases) {
        const result = validateQuestion(testCase.input);
        if (result.isValid !== testCase.expected) {
            console.log(`❌ Falló validación para: "${testCase.input.substring(0, 50)}..."`);
            validationPassed = false;
        }
    }
    
    if (validationPassed) {
        console.log('✅ Validación de preguntas funcionando');
        passed++;
    } else {
        failed++;
    }
    
    // Test 5: Formateo de documentos
    console.log('\n📋 Test 5: Formateo de documentos');
    try {
        const mockDocs = [
            { pageContent: 'Contenido 1', metadata: { source: 'test1.com' } },
            { pageContent: 'Contenido 2', metadata: { source: 'test2.com' } }
        ];
        
        const formatted = formatDocumentsAsString(mockDocs);
        if (formatted.includes('Fuente 1') && formatted.includes('Contenido 1')) {
            console.log('✅ Formateo de documentos funcionando');
            passed++;
        } else {
            console.log('❌ Error en formateo de documentos');
            failed++;
        }
    } catch (error) {
        console.log('❌ Error en formateo:', error.message);
        failed++;
    }
    
    // Test 6: Estadísticas de documentos
    console.log('\n📋 Test 6: Estadísticas de documentos');
    try {
        const mockDocs = [
            { pageContent: 'Test content', metadata: { source: 'https://test.com/page1' } }
        ];
        
        const stats = generateDocumentStats(mockDocs);
        if (stats.total === 1 && stats.sources.includes('test.com')) {
            console.log('✅ Estadísticas de documentos funcionando');
            passed++;
        } else {
            console.log('❌ Error en estadísticas de documentos');
            failed++;
        }
    } catch (error) {
        console.log('❌ Error en estadísticas:', error.message);
        failed++;
    }
    
    // Resumen de pruebas
    console.log('\n' + '=' .repeat(50));
    console.log('📊 RESUMEN DE PRUEBAS:');
    console.log(`✅ Pasaron: ${passed}`);
    console.log(`❌ Fallaron: ${failed}`);
    console.log(`📊 Total: ${passed + failed}`);
    
    if (failed === 0) {
        console.log('\n🎉 ¡Todas las pruebas pasaron exitosamente!');
        process.exit(0);
    } else {
        console.log('\n⚠️  Algunas pruebas fallaron. Revisa la configuración.');
        process.exit(1);
    }
}

runTests();
