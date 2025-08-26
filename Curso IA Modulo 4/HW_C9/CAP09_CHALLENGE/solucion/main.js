/**
 * Sistema de Consulta de Noticias con LangChain
 * 
 * Este sistema utiliza LangChain para crear un chatbot inteligente que:
 * - Extrae noticias de CNN Español y CBC News
 * - Clasifica preguntas automáticamente (noticias vs generales)
 * - Proporciona respuestas contextuales usando vectorización
 * - Mantiene memoria de conversación para respuestas personalizadas
 */

import { RecursiveUrlLoader } from "@langchain/community/document_loaders/web/recursive_url";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";
import { RunnablePassthrough, RunnableSequence } from "@langchain/core/runnables";
import { ConversationSummaryBufferMemory } from "langchain/memory";
import { compile } from "html-to-text";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import readline from "readline";
import { CONFIG, initializeConfig } from './config.js';
import { createLLMModel, createEmbeddingsModel, checkProviderAvailability, getOptimalConfiguration } from './providers.js';
import { 
    formatDocumentsAsString, 
    validateQuestion, 
    formatResponse, 
    generateDocumentStats, 
    handleSystemError, 
    logMetrics 
} from './utils.js';

// Inicializar configuración del sistema
initializeConfig();

// Verificar disponibilidad de proveedores y mostrar recomendaciones
checkProviderAvailability();
getOptimalConfiguration();

// ========================================================================================
// CONFIGURACIÓN DE MODELOS Y PARSERS
// ========================================================================================

/**
 * Configuración del extractor de HTML a texto plano
 * Utiliza html-to-text para convertir contenido web a formato legible
 */
const compiledConvert = compile({ 
    wordwrap: 130,
    selectors: [
        { selector: 'a', options: { ignoreHref: true } },
        { selector: 'img', format: 'skip' }
    ]
}); 

/**
 * Configuración de los cargadores de documentos para las fuentes de noticias
 * - CNN Español: Fuente principal de noticias en español
 * - CBC News: Fuente de noticias en inglés para diversidad de contenido
 */
const cnnLoader = new RecursiveUrlLoader(CONFIG.sources.cnn, {
    extractor: compiledConvert,
    maxDepth: CONFIG.crawling.maxDepth,
    excludeDirs: CONFIG.crawling.excludeDirs,
});

const cbcLoader = new RecursiveUrlLoader(CONFIG.sources.cbc, {
    extractor: compiledConvert,
    maxDepth: CONFIG.crawling.maxDepth,
    excludeDirs: CONFIG.crawling.excludeDirs,
});

/**
 * Inicialización del modelo de lenguaje y parser de salida
 * - Utiliza configuración desde config.js priorizando opciones gratuitas
 * - StringOutputParser para obtener respuestas en formato de texto
 */
const model = createLLMModel();
const parser = new StringOutputParser();

// ========================================================================================
// SISTEMA DE MEMORIA CONVERSACIONAL
// ========================================================================================

/**
 * Implementación de memoria conversacional para mantener contexto
 * Utiliza ConversationSummaryBufferMemory para eficiencia en conversaciones largas
 */
const conversationMemory = new ConversationSummaryBufferMemory({
    llm: model,
    maxTokenLimit: CONFIG.memory.maxTokens,
    returnMessages: true,
});

// ========================================================================================
// CLASIFICADOR DE PREGUNTAS
// ========================================================================================

/**
 * Template para clasificar preguntas del usuario
 * Determina si la consulta requiere información de noticias actuales o conocimiento general
 */
const classificationPrompt = ChatPromptTemplate.fromTemplate(`
Clasifica la siguiente pregunta como 'news' o 'general'. 
Solo responde con una de estas dos palabras.

Criterios:
- 'news': Si pregunta sobre eventos actuales, noticias recientes, política actual, deportes actuales, economía actual
- 'general': Si pregunta sobre conocimiento general, conceptos, definiciones, historia, ciencia básica

Pregunta: {question}
`);

const classificationChain = RunnableSequence.from([
    classificationPrompt,
    model,
    parser
]);

// ========================================================================================
// CADENA DE PROCESAMIENTO DE NOTICIAS
// ========================================================================================

/**
 * Configura la cadena de procesamiento para consultas de noticias
 * 
 * Proceso:
 * 1. Carga noticias de CNN Español y CBC News
 * 2. Filtra contenido vacío
 * 3. Divide texto en chunks para procesamiento eficiente
 * 4. Crea almacén vectorial para búsqueda semántica
 * 5. Configura cadena de recuperación y generación de respuestas
 * 
 * @returns {RunnableSequence} Cadena configurada para procesar consultas de noticias
 */
async function setupNewsChain() {
    console.log("📰 Cargando noticias de CNN Español...");
    const cnnDocs = await cnnLoader.load();
    
    console.log("📰 Cargando noticias de CBC News...");
    const cbcDocs = await cbcLoader.load();
    
    // Combinar documentos de ambas fuentes
    const allDocs = cnnDocs.concat(cbcDocs);
    console.log(`📊 Total de documentos cargados: ${allDocs.length}`);

    // Filtrar documentos con contenido vacío
    let docs = allDocs.filter(item => item.pageContent.trim() !== "");
    console.log(`✅ Documentos después del filtrado: ${docs.length}`);

    // Mostrar estadísticas de documentos
    const stats = generateDocumentStats(docs);
    console.log(`📈 Estadísticas: ${stats.total} docs, promedio ${stats.avgLength} chars, fuentes: ${stats.sources.join(', ')}`);

    /**
     * Configuración del divisor de texto
     * Utiliza parámetros de CONFIG para personalización
     */
    const textSplitter = new RecursiveCharacterTextSplitter({
        chunkSize: CONFIG.retriever.chunkSize,
        chunkOverlap: CONFIG.retriever.chunkOverlap,
    });
    const allSplits = await textSplitter.splitDocuments(docs);
    console.log(`🔄 Documentos divididos en chunks: ${allSplits.length}`);

    /**
     * Creación del almacén vectorial para búsqueda semántica
     * Utiliza embeddings configurados (Google por defecto - GRATUITO)
     */
    console.log("🔍 Creando almacén vectorial...");
    const embeddingsModel = createEmbeddingsModel();
    const vectorStore = await MemoryVectorStore.fromDocuments(allSplits, embeddingsModel);

    // Configurar recuperador con parámetros optimizados desde CONFIG
    const vectorStoreRetriever = vectorStore.asRetriever({
        searchType: "similarity",
        k: CONFIG.retriever.k,
    });

    /**
     * Template del sistema para respuestas de noticias
     * Incluye instrucciones específicas para manejo de contexto de noticias
     */
    const SYSTEM_TEMPLATE = `Eres un asistente especializado en noticias actuales. 
    Utiliza el siguiente contexto de noticias para responder la pregunta del usuario.
    
    INSTRUCCIONES IMPORTANTES:
    - Si encuentras información relevante en el contexto, úsala para dar una respuesta completa
    - Si no encuentras información específica, indica claramente que no tienes esa información en las noticias actuales
    - Siempre menciona las fuentes cuando sea relevante (CNN Español o CBC News)
    - Proporciona fechas cuando estén disponibles
    - Sé conciso pero informativo
    
    CONTEXTO DE NOTICIAS:
    ----------------
    {context}
    
    HISTORIAL DE CONVERSACIÓN:
    {chat_history}`;

    /**
     * Configuración del prompt con memoria conversacional
     */
    const newsPrompt = ChatPromptTemplate.fromMessages([
        ["system", SYSTEM_TEMPLATE],
        new MessagesPlaceholder("chat_history"),
        ["human", "{question}"],
    ]);
    
    /**
     * Función para formatear documentos recuperados como string
     * Utiliza la función de utilidades para formato consistente
     */
    const documentFormatter = formatDocumentsAsString;

    /**
     * Cadena principal de procesamiento de noticias
     * Integra recuperación de contexto, memoria conversacional y generación de respuestas
     */
    const chain = RunnableSequence.from([
        {
            context: vectorStoreRetriever.pipe(documentFormatter),
            question: new RunnablePassthrough(),
            chat_history: async () => {
                const memory = await conversationMemory.loadMemoryVariables({});
                return memory.history || [];
            },
        },
        newsPrompt,
        model,
        new StringOutputParser()
    ]);
    
    console.log("✅ Cadena de noticias configurada exitosamente");
    return chain;
}

// ========================================================================================
// CADENA DE CONOCIMIENTO GENERAL
// ========================================================================================

/**
 * Cadena para responder consultas de conocimiento general
 * Integra memoria conversacional para respuestas contextuales
 */
const generalChain = RunnableSequence.from([
    {
        question: new RunnablePassthrough(),
        chat_history: async () => {
            const memory = await conversationMemory.loadMemoryVariables({});
            return memory.history || [];
        },
    },
    ChatPromptTemplate.fromMessages([
        ["system", `Eres un asistente útil y conocedor. Responde preguntas generales de manera clara y precisa.
        
        HISTORIAL DE CONVERSACIÓN:
        {chat_history}`],
        ["human", "{question}"],
    ]),
    model,
    parser
]);

// ========================================================================================
// INICIALIZACIÓN DEL SISTEMA
// ========================================================================================

console.log("🚀 Iniciando Sistema de Consulta de Noticias...");
console.log("⏳ Configurando cadenas de procesamiento...");

/**
 * Inicialización de la cadena de noticias
 * Se ejecuta al arrancar el sistema para tener todo listo
 */
const newsChain = await setupNewsChain();

// ========================================================================================
// LÓGICA DE ENRUTAMIENTO Y PROCESAMIENTO
// ========================================================================================

/**
 * Función principal de enrutamiento de preguntas
 * 
 * @param {string} question - Pregunta del usuario
 * @returns {Promise<string>} Respuesta generada por el sistema
 */
async function routeQuestion(question) {
    const startTime = Date.now();
    
    try {
        // Validar la pregunta
        const validation = validateQuestion(question);
        if (!validation.isValid) {
            logMetrics('validation_error', Date.now() - startTime, false);
            return `⚠️ ${validation.reason}`;
        }
        
        console.log("🤔 Clasificando pregunta...");
        
        // Clasificar la pregunta
        const classification = await classificationChain.invoke({ "question": question });
        const isNewsQuery = classification.toLowerCase().trim() === 'news';
        
        console.log(`📊 Clasificación: ${isNewsQuery ? '📰 NOTICIAS' : '🧠 GENERAL'}`);
        
        let response;
        const queryType = isNewsQuery ? 'news' : 'general';
        
        // Enrutar según clasificación
        if (isNewsQuery) {
            console.log("🔍 Buscando en noticias actuales...");
            response = await newsChain.invoke(question);
        } else {
            console.log("💭 Procesando consulta general...");
            response = await generalChain.invoke(question);
        }
        
        // Guardar la interacción en memoria
        await conversationMemory.saveContext(
            { input: question },
            { output: response }
        );
        
        const processingTime = Date.now() - startTime;
        logMetrics(queryType, processingTime, true);
        
        return response;
        
    } catch (error) {
        const processingTime = Date.now() - startTime;
        logMetrics('error', processingTime, false);
        return handleSystemError(error, 'procesamiento de pregunta');
    }
}

// ========================================================================================
// INTERFAZ DE USUARIO - LÍNEA DE COMANDOS
// ========================================================================================

/**
 * Configuración de la interfaz de línea de comandos
 * Proporciona interacción continua con el usuario
 */
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Mensaje de bienvenida
console.log("\n" + "=".repeat(60));
console.log("🤖 SISTEMA DE CONSULTA DE NOTICIAS");
console.log("=".repeat(60));
console.log("✅ Sistema listo para consultas");
console.log("💡 Puedes preguntar sobre noticias actuales o temas generales");
console.log("🚪 Escribe 'exit' para salir");
console.log("=".repeat(60) + "\n");

/**
 * Manejador de entrada del usuario
 * Procesa cada línea ingresada y proporciona respuestas
 */
rl.on('line', async (line) => {
    const question = line.trim();
    
    // Comando de salida
    if (question.toLowerCase() === "exit") {
        console.log("👋 ¡Hasta luego! Gracias por usar el sistema.");
        rl.close();
        return;
    }
    
    // Comandos especiales
    if (question.toLowerCase() === "help") {
        console.log("\n📖 AYUDA DEL SISTEMA:");
        console.log("- Haz preguntas sobre noticias actuales o temas generales");
        console.log("- El sistema clasificará automáticamente tu consulta");
        console.log("- Escribe 'exit' para salir");
        console.log("- Escribe 'clear' para limpiar memoria de conversación");
        console.log("- Escribe 'stats' para ver estadísticas del sistema\n");
        rl.prompt();
        return;
    }
    
    if (question.toLowerCase() === "clear") {
        await conversationMemory.clear();
        console.log("🧹 Memoria de conversación limpiada.");
        rl.prompt();
        return;
    }
    
    if (question.toLowerCase() === "stats") {
        const memory = await conversationMemory.loadMemoryVariables({});
        console.log("📊 ESTADÍSTICAS DEL SISTEMA:");
        console.log(`- Mensajes en memoria: ${memory.history ? memory.history.length : 0}`);
        console.log(`- Configuración: ${CONFIG.openai.model} @ ${CONFIG.openai.temperature}`);
        console.log(`- Límite de memoria: ${CONFIG.memory.maxTokens} tokens`);
        rl.prompt();
        return;
    }
    
    // Validar entrada vacía
    if (!question) {
        console.log("⚠️  Por favor, ingresa una pregunta válida.");
        rl.prompt();
        return;
    }
    
    console.log(`\n🔄 Procesando: "${question}"`);
    console.log("-".repeat(50));
    
    // Procesar la pregunta
    const answer = await routeQuestion(question);
    
    console.log("\n📝 RESPUESTA:");
    console.log("-".repeat(20));
    console.log(answer);
    console.log("\n" + "=".repeat(60) + "\n");
    
    rl.prompt();
});

// Configurar el prompt inicial
rl.setPrompt('💬 Tu pregunta: ');
rl.prompt();
