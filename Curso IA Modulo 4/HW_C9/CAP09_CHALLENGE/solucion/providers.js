/**
 * Módulo de Proveedores de IA
 * 
 * Este módulo maneja la configuración y creación de diferentes proveedores
 * de LLM y embeddings, priorizando opciones gratuitas.
 */

import { ChatGroq } from "@langchain/groq";
import { ChatOpenAI, OpenAIEmbeddings } from "@langchain/openai";
import { GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { CONFIG } from './config.js';

/**
 * Crea el modelo LLM según la configuración
 * @returns {ChatGroq|ChatOpenAI} Instancia del modelo configurado
 */
export function createLLMModel() {
    const provider = CONFIG.llm.provider;
    
    console.log(`🤖 Inicializando modelo LLM: ${provider.toUpperCase()}`);
    
    switch (provider) {
        case 'groq':
            return new ChatGroq({
                apiKey: CONFIG.llm.groq.apiKey,
                model: CONFIG.llm.groq.model,
                temperature: CONFIG.llm.groq.temperature,
            });
            
        case 'openai':
            return new ChatOpenAI({
                apiKey: CONFIG.llm.openai.apiKey,
                model: CONFIG.llm.openai.model,
                temperature: CONFIG.llm.openai.temperature,
            });
            
        case 'google':
            return new ChatGoogleGenerativeAI({
                apiKey: CONFIG.embeddings.google.apiKey,
                model: "gemini-pro",
                temperature: CONFIG.llm.groq.temperature,
            });
            
        default:
            console.warn(`⚠️  Proveedor LLM desconocido: ${provider}, usando Groq por defecto`);
            return new ChatGroq({
                apiKey: CONFIG.llm.groq.apiKey,
                model: CONFIG.llm.groq.model,
                temperature: CONFIG.llm.groq.temperature,
            });
    }
}

/**
 * Crea el modelo de embeddings según la configuración
 * @returns {GoogleGenerativeAIEmbeddings|OpenAIEmbeddings} Instancia del modelo de embeddings
 */
export function createEmbeddingsModel() {
    const provider = CONFIG.embeddings.provider;
    
    console.log(`🔍 Inicializando embeddings: ${provider.toUpperCase()}`);
    
    switch (provider) {
        case 'google':
            return new GoogleGenerativeAIEmbeddings({
                apiKey: CONFIG.embeddings.google.apiKey,
                model: CONFIG.embeddings.google.model,
            });
            
        case 'openai':
            return new OpenAIEmbeddings({
                apiKey: CONFIG.embeddings.openai.apiKey,
                model: CONFIG.embeddings.openai.model,
            });
            
        default:
            console.warn(`⚠️  Proveedor de embeddings desconocido: ${provider}, usando Google por defecto`);
            return new GoogleGenerativeAIEmbeddings({
                apiKey: CONFIG.embeddings.google.apiKey,
                model: CONFIG.embeddings.google.model,
            });
    }
}

/**
 * Verifica la disponibilidad de los proveedores configurados
 * @returns {Object} Estado de disponibilidad de cada proveedor
 */
export function checkProviderAvailability() {
    const availability = {
        groq: !!CONFIG.llm.groq.apiKey,
        openai: !!CONFIG.llm.openai.apiKey,
        google: !!CONFIG.embeddings.google.apiKey,
    };
    
    console.log('📊 Disponibilidad de proveedores:');
    Object.entries(availability).forEach(([provider, available]) => {
        const status = available ? '✅ Disponible' : '❌ No configurado';
        const cost = provider === 'groq' || provider === 'google' ? '(GRATUITO)' : '(PAGADO)';
        console.log(`   - ${provider.toUpperCase()}: ${status} ${cost}`);
    });
    
    return availability;
}

/**
 * Obtiene recomendaciones de configuración optimizada
 * @returns {Object} Configuración recomendada
 */
export function getOptimalConfiguration() {
    const availability = checkProviderAvailability();
    
    const recommendations = {
        llm: 'groq', // Groq es gratuito y muy rápido
        embeddings: 'google', // Google embeddings son gratuitos
        fallback: {
            llm: availability.openai ? 'openai' : null,
            embeddings: availability.openai ? 'openai' : null,
        }
    };
    
    console.log('\n💡 Configuración recomendada (priorizando opciones gratuitas):');
    console.log(`   - LLM: ${recommendations.llm.toUpperCase()} (Llama3 - muy rápido y gratuito)`);
    console.log(`   - Embeddings: ${recommendations.embeddings.toUpperCase()} (Google - gratuito)`);
    
    if (recommendations.fallback.llm) {
        console.log(`   - Fallback LLM: ${recommendations.fallback.llm.toUpperCase()}`);
    }
    
    return recommendations;
}

export default {
    createLLMModel,
    createEmbeddingsModel,
    checkProviderAvailability,
    getOptimalConfiguration
};
