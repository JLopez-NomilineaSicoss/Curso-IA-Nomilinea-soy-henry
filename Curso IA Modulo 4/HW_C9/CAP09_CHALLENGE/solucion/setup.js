/**
 * Script de Configuración Inicial
 * 
 * Este script ayuda a configurar el entorno del sistema por primera vez.
 * Verifica dependencias, crea archivos de configuración y valida el setup.
 */

import fs from 'fs';
import path from 'path';
import readline from 'readline';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Función para hacer preguntas al usuario
function question(prompt) {
    return new Promise((resolve) => {
        rl.question(prompt, resolve);
    });
}

console.log('🚀 CONFIGURACIÓN INICIAL DEL SISTEMA DE CONSULTA DE NOTICIAS');
console.log('=' .repeat(60));

async function setupEnvironment() {
    try {
        console.log('\n📋 Verificando configuración...');
        
        // Verificar si existe .env
        const envExists = fs.existsSync('.env');
        
        if (!envExists) {
            console.log('⚠️  Archivo .env no encontrado');
            const createEnv = await question('¿Deseas crear un archivo .env? (y/n): ');
            
            if (createEnv.toLowerCase() === 'y' || createEnv.toLowerCase() === 'yes') {
                console.log('\n🤖 Configurando APIs...');
                console.log('💡 Recomendamos usar Groq (gratuito) + Google Embeddings (gratuito)');
                
                // Configuración de Groq (recomendado - gratuito)
                const useGroq = await question('¿Usar Groq como LLM principal? (Recomendado - GRATUITO) (y/n): ');
                let groqKey = '';
                if (useGroq.toLowerCase() === 'y' || useGroq.toLowerCase() === 'yes') {
                    groqKey = await question('Clave API de Groq (ya tienes una): ') || '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';
                }
                
                // Configuración de Google (recomendado para embeddings - gratuito)
                const useGoogle = await question('¿Usar Google AI para embeddings? (Recomendado - GRATUITO) (y/n): ');
                let googleKey = '';
                if (useGoogle.toLowerCase() === 'y' || useGoogle.toLowerCase() === 'yes') {
                    googleKey = await question('Clave API de Google AI (ya tienes una): ') || 'AIzaSyBmWgK0Nas0ONpR20d6wEvStp-iSMyWTEI';
                }
                
                // Configuración opcional de OpenAI
                const useOpenAI = await question('¿Configurar OpenAI también? (OPCIONAL - PAGADO) (y/n): ');
                let openaiKey = '';
                if (useOpenAI.toLowerCase() === 'y' || useOpenAI.toLowerCase() === 'yes') {
                    openaiKey = await question('Clave API de OpenAI: ') || '';
                }
                
                // APIs adicionales opcionales
                const serperKey = await question('Clave API de Serper (opcional): ') || '82b26df9fd2c480881ed0b5cae7485c52d6d2859';
                const searchApiKey = await question('Clave API de SearchAPI (opcional): ') || 'mkokY9te6D1xzNCoBqdXZ6Rh';
                
                // Crear archivo .env
                const envContent = `# Configuración del Sistema de Consulta de Noticias
# =============================================================================
# CONFIGURACIÓN DE APIS PRINCIPALES (Priorizando opciones GRATUITAS)
# =============================================================================

# Groq Cloud API (GRATUITA - Recomendada)
GROQ_API_KEY=${groqKey}

# Google AI Studio (GRATUITA - Para embeddings)
GOOGLE_API_KEY=${googleKey}

# Serper.dev (GRATUITA - Para búsquedas web adicionales)
SERPER_API_KEY=${serperKey}

# SearchAPI (Para búsquedas alternativas)
SEARCH_API_KEY=${searchApiKey}

# OpenAI (OPCIONAL - Solo si quieres usar GPT)
OPENAI_API_KEY=${openaiKey}

# =============================================================================
# CONFIGURACIÓN DE MODELOS (Priorizando opciones gratuitas)
# =============================================================================

# Modelo LLM principal (Groq es GRATUITO y muy rápido)
LLM_PROVIDER=groq
GROQ_MODEL=llama3-8b-8192

# Modelo de embeddings (Google es GRATUITO)
EMBEDDING_PROVIDER=google
GOOGLE_EMBEDDING_MODEL=models/embedding-001

# Configuración de temperatura del modelo (0.0 - 1.0)
MODEL_TEMPERATURE=0.7

# Configuración de memoria conversacional
MAX_MEMORY_TOKENS=1000

# Configuración de búsqueda vectorial
RETRIEVER_K=4
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# URLs de fuentes de noticias (modificables)
CNN_URL=https://cnnespanol.cnn.com/lite/
CBC_URL=https://www.cbc.ca/lite/news?sort=latest

# Configuración de crawling
MAX_DEPTH=2
`;
                
                fs.writeFileSync('.env', envContent);
                console.log('✅ Archivo .env creado exitosamente');
                console.log('💰 Configuración optimizada para usar APIs GRATUITAS');
            }
        } else {
            console.log('✅ Archivo .env encontrado');
        }
        
        // Verificar dependencias
        console.log('\n📦 Verificando dependencias...');
        const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
        const dependencies = Object.keys(packageJson.dependencies || {});
        
        console.log(`📊 Dependencias definidas: ${dependencies.length}`);
        dependencies.forEach(dep => console.log(`   - ${dep}`));
        
        // Verificar node_modules
        if (!fs.existsSync('node_modules')) {
            console.log('⚠️  Directorio node_modules no encontrado');
            console.log('💡 Ejecuta: npm install');
        } else {
            console.log('✅ Dependencias instaladas');
        }
        
        console.log('\n🎯 CONFIGURACIÓN COMPLETADA');
        console.log('=' .repeat(40));
        console.log('Siguiente paso: npm run start');
        
    } catch (error) {
        console.error('❌ Error durante la configuración:', error.message);
        process.exit(1);
    } finally {
        rl.close();
    }
}

setupEnvironment();
