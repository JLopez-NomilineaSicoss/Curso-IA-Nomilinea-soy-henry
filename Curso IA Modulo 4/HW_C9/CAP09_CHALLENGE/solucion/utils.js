/**
 * Utilidades para el Sistema de Consulta de Noticias
 * 
 * Este módulo contiene funciones de utilidad para el manejo de datos,
 * formateo de respuestas y validaciones del sistema.
 */

/**
 * Formatea los documentos recuperados como string legible
 * @param {Array} documents - Array de documentos recuperados del vector store
 * @returns {string} Documentos formateados con índices y separadores
 */
export function formatDocumentsAsString(documents) {
    if (!documents || documents.length === 0) {
        return "No se encontraron documentos relevantes.";
    }
    
    return documents.map((document, index) => {
        const source = document.metadata?.source || 'Fuente desconocida';
        const content = document.pageContent.trim();
        
        return `[Fuente ${index + 1} - ${source}]:\n${content}`;
    }).join("\n\n" + "=".repeat(50) + "\n\n");
}

/**
 * Valida si una pregunta es válida para procesamiento
 * @param {string} question - La pregunta del usuario
 * @returns {Object} Objeto con isValid y reason
 */
export function validateQuestion(question) {
    if (!question || typeof question !== 'string') {
        return { isValid: false, reason: 'Pregunta debe ser un texto válido' };
    }
    
    const trimmed = question.trim();
    if (trimmed.length === 0) {
        return { isValid: false, reason: 'Pregunta no puede estar vacía' };
    }
    
    if (trimmed.length < 3) {
        return { isValid: false, reason: 'Pregunta muy corta' };
    }
    
    if (trimmed.length > 500) {
        return { isValid: false, reason: 'Pregunta muy larga (máximo 500 caracteres)' };
    }
    
    return { isValid: true };
}

/**
 * Formatea la respuesta del sistema con metadata adicional
 * @param {string} response - Respuesta generada por el modelo
 * @param {string} queryType - Tipo de consulta ('news' o 'general')
 * @param {number} processingTime - Tiempo de procesamiento en ms
 * @returns {string} Respuesta formateada
 */
export function formatResponse(response, queryType, processingTime = null) {
    let formattedResponse = response;
    
    // Agregar indicador de tipo de consulta
    const typeIndicator = queryType === 'news' ? '📰 NOTICIAS' : '🧠 GENERAL';
    
    // Agregar tiempo de procesamiento si está disponible
    const timeInfo = processingTime ? ` (${processingTime}ms)` : '';
    
    return {
        content: formattedResponse,
        metadata: {
            queryType: typeIndicator,
            processingTime: timeInfo,
            timestamp: new Date().toLocaleString()
        }
    };
}

/**
 * Limpia y normaliza el texto de entrada
 * @param {string} text - Texto a limpiar
 * @returns {string} Texto limpio
 */
export function cleanText(text) {
    if (!text) return '';
    
    return text
        .trim()
        .replace(/\s+/g, ' ') // Reemplazar múltiples espacios por uno solo
        .replace(/\n\s*\n/g, '\n') // Limpiar líneas vacías múltiples
        .replace(/[^\S\n]+/g, ' '); // Limpiar espacios en blanco excepto saltos de línea
}

/**
 * Genera estadísticas de documentos cargados
 * @param {Array} documents - Array de documentos
 * @returns {Object} Estadísticas de los documentos
 */
export function generateDocumentStats(documents) {
    if (!documents || documents.length === 0) {
        return {
            total: 0,
            avgLength: 0,
            sources: [],
            totalCharacters: 0
        };
    }
    
    const totalCharacters = documents.reduce((sum, doc) => sum + doc.pageContent.length, 0);
    const avgLength = Math.round(totalCharacters / documents.length);
    
    // Extraer fuentes únicas
    const sources = [...new Set(documents.map(doc => {
        const url = doc.metadata?.source || 'unknown';
        try {
            return new URL(url).hostname;
        } catch {
            return 'unknown';
        }
    }))];
    
    return {
        total: documents.length,
        avgLength,
        sources,
        totalCharacters
    };
}

/**
 * Maneja errores del sistema de manera consistente
 * @param {Error} error - Error capturado
 * @param {string} context - Contexto donde ocurrió el error
 * @returns {string} Mensaje de error formateado para el usuario
 */
export function handleSystemError(error, context = 'sistema') {
    console.error(`❌ Error en ${context}:`, error.message);
    
    // Errores específicos de LangChain/OpenAI
    if (error.message.includes('API key')) {
        return 'Error: Clave API de OpenAI no configurada o inválida. Por favor, verifica tu configuración.';
    }
    
    if (error.message.includes('rate limit') || error.message.includes('quota')) {
        return 'Error: Límite de API alcanzado. Por favor, intenta de nuevo más tarde.';
    }
    
    if (error.message.includes('network') || error.message.includes('timeout')) {
        return 'Error de conexión. Por favor, verifica tu conexión a internet e intenta de nuevo.';
    }
    
    // Error genérico
    return `Lo siento, ocurrió un error en el ${context}. Por favor, intenta de nuevo.`;
}

/**
 * Registra métricas de uso del sistema
 * @param {string} queryType - Tipo de consulta
 * @param {number} processingTime - Tiempo de procesamiento
 * @param {boolean} success - Si la consulta fue exitosa
 */
export function logMetrics(queryType, processingTime, success) {
    const timestamp = new Date().toISOString();
    const logEntry = {
        timestamp,
        queryType,
        processingTime,
        success,
        date: new Date().toDateString()
    };
    
    // En un entorno de producción, esto se podría enviar a un servicio de logging
    console.log('📊 Métrica:', JSON.stringify(logEntry));
}

export default {
    formatDocumentsAsString,
    validateQuestion,
    formatResponse,
    cleanText,
    generateDocumentStats,
    handleSystemError,
    logMetrics
};
