/**
 * Sistema de Consulta de Noticias Modularizado
 * 
 * Clase principal que encapsula toda la lógica del sistema de noticias
 * para ser usado tanto por CLI como por la interfaz web.
 */

import { RecursiveUrlLoader } from "@langchain/community/document_loaders/web/recursive_url";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";
import { RunnablePassthrough, RunnableSequence } from "@langchain/core/runnables";
import { ConversationSummaryBufferMemory } from "langchain/memory";
import { compile } from "html-to-text";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { MemoryVectorStore } from "langchain/vectorstores/memory";
import { CONFIG } from './config.js';
import { createLLMModel, createEmbeddingsModel } from './providers.js';
import { formatDocumentsAsString, generateDocumentStats } from './utils.js';

export class NewsQuerySystem {
    constructor() {
        this.model = null;
        this.parser = new StringOutputParser();
        this.conversationMemory = null;
        this.newsChain = null;
        this.generalChain = null;
        this.classificationChain = null;
        this.isInitialized = false;
        this.documentStats = null;
    }

    /**
     * Inicializar el sistema completo
     */
    async initialize() {
        try {
            console.log('🤖 Inicializando modelos...');
            await this.initializeModels();
            
            console.log('📰 Configurando cadenas...');
            await this.setupChains();
            
            console.log('💾 Configurando memoria...');
            this.setupMemory();
            
            console.log('📊 Cargando noticias...');
            await this.setupNewsChain();
            
            this.isInitialized = true;
            console.log('✅ Sistema inicializado correctamente');
            
        } catch (error) {
            console.error('❌ Error en inicialización:', error.message);
            throw error;
        }
    }

    /**
     * Inicializar modelos de IA
     */
    async initializeModels() {
        this.model = createLLMModel();
    }

    /**
     * Configurar memoria conversacional
     */
    setupMemory() {
        this.conversationMemory = new ConversationSummaryBufferMemory({
            llm: this.model,
            maxTokenLimit: CONFIG.memory.maxTokens,
            returnMessages: true,
        });
    }

    /**
     * Configurar cadenas básicas
     */
    async setupChains() {
        // Cadena de clasificación
        const classificationPrompt = ChatPromptTemplate.fromTemplate(`
Clasifica la siguiente pregunta como 'news' o 'general'. 
Solo responde con una de estas dos palabras.

Criterios:
- 'news': Si pregunta sobre eventos actuales, noticias recientes, política actual, deportes actuales, economía actual
- 'general': Si pregunta sobre conocimiento general, conceptos, definiciones, historia, ciencia básica

Pregunta: {question}
`);

        this.classificationChain = RunnableSequence.from([
            classificationPrompt,
            this.model,
            this.parser
        ]);

        // Cadena general
        this.generalChain = RunnableSequence.from([
            {
                question: new RunnablePassthrough(),
                chat_history: async () => {
                    const memory = await this.conversationMemory.loadMemoryVariables({});
                    return memory.history || [];
                },
            },
            ChatPromptTemplate.fromMessages([
                ["system", `Eres un asistente útil y conocedor. Responde preguntas generales de manera clara y precisa.
                
                HISTORIAL DE CONVERSACIÓN:
                {chat_history}`],
                ["human", "{question}"],
            ]),
            this.model,
            this.parser
        ]);
    }

    /**
     * Configurar cadena de noticias
     */
    async setupNewsChain() {
        console.log("📰 Cargando noticias de CNN Español...");
        const cnnLoader = new RecursiveUrlLoader(CONFIG.sources.cnn, {
            extractor: compile({ 
                wordwrap: 130,
                selectors: [
                    { selector: 'a', options: { ignoreHref: true } },
                    { selector: 'img', format: 'skip' }
                ]
            }),
            maxDepth: CONFIG.crawling.maxDepth,
            excludeDirs: CONFIG.crawling.excludeDirs,
        });

        console.log("📰 Cargando noticias de CBC News...");
        const cbcLoader = new RecursiveUrlLoader(CONFIG.sources.cbc, {
            extractor: compile({ 
                wordwrap: 130,
                selectors: [
                    { selector: 'a', options: { ignoreHref: true } },
                    { selector: 'img', format: 'skip' }
                ]
            }),
            maxDepth: CONFIG.crawling.maxDepth,
            excludeDirs: CONFIG.crawling.excludeDirs,
        });

        const cnnDocs = await cnnLoader.load();
        const cbcDocs = await cbcLoader.load();
        
        const allDocs = cnnDocs.concat(cbcDocs);
        console.log(`📊 Total de documentos cargados: ${allDocs.length}`);

        let docs = allDocs.filter(item => item.pageContent.trim() !== "");
        console.log(`✅ Documentos después del filtrado: ${docs.length}`);

        // Generar estadísticas
        this.documentStats = generateDocumentStats(docs);
        console.log(`📈 Estadísticas: ${this.documentStats.total} docs, promedio ${this.documentStats.avgLength} chars`);

        // Dividir documentos
        const textSplitter = new RecursiveCharacterTextSplitter({
            chunkSize: CONFIG.retriever.chunkSize,
            chunkOverlap: CONFIG.retriever.chunkOverlap,
        });
        const allSplits = await textSplitter.splitDocuments(docs);
        console.log(`🔄 Documentos divididos en chunks: ${allSplits.length}`);

        // Crear vector store
        console.log("🔍 Creando almacén vectorial...");
        const embeddingsModel = createEmbeddingsModel();
        const vectorStore = await MemoryVectorStore.fromDocuments(allSplits, embeddingsModel);

        const vectorStoreRetriever = vectorStore.asRetriever({
            searchType: "similarity",
            k: CONFIG.retriever.k,
        });

        // Configurar prompt de noticias
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

        const newsPrompt = ChatPromptTemplate.fromMessages([
            ["system", SYSTEM_TEMPLATE],
            new MessagesPlaceholder("chat_history"),
            ["human", "{question}"],
        ]);

        // Crear cadena de noticias
        this.newsChain = RunnableSequence.from([
            {
                context: vectorStoreRetriever.pipe(formatDocumentsAsString),
                question: new RunnablePassthrough(),
                chat_history: async () => {
                    const memory = await this.conversationMemory.loadMemoryVariables({});
                    return memory.history || [];
                },
            },
            newsPrompt,
            this.model,
            this.parser
        ]);

        console.log("✅ Cadena de noticias configurada exitosamente");
    }

    /**
     * Inicialización rápida sin cargar noticias externas
     * Evita cuelgues en la inicialización
     */
    async quickInitialize() {
        try {
            console.log('⚡ Inicialización rápida iniciada...');
            
            console.log('🤖 Inicializando modelos básicos...');
            await this.initializeModels();
            
            console.log('📰 Configurando cadenas básicas...');
            await this.setupBasicChains();
            
            console.log('💾 Configurando memoria...');
            this.setupMemory();
            
            this.isInitialized = true;
            console.log('✅ Sistema en modo rápido listo');
            
        } catch (error) {
            console.error('❌ Error en inicialización rápida:', error.message);
            throw error;
        }
    }

    /**
     * Configurar cadenas básicas sin cargar noticias externas
     */
    async setupBasicChains() {
        // Configurar clasificación
        const classificationTemplate = `Analiza la siguiente consulta y determina si se trata de una consulta sobre noticias actuales/eventos recientes o una consulta general.

Criterios para consulta de NOTICIAS:
- Menciona palabras como: noticias, últimas, reciente, actual, hoy, ayer, esta semana
- Pregunta sobre eventos actuales, política, deportes, economía, tecnología reciente
- Busca información sobre lo que está pasando ahora

Responde SOLO con "NOTICIAS" o "GENERAL".

Consulta: {question}
Clasificación:`;

        this.classificationChain = ChatPromptTemplate.fromTemplate(classificationTemplate).pipe(this.model).pipe(this.parser);

        // Configurar cadena general básica
        const generalTemplate = `Eres un asistente inteligente que responde preguntas generales de manera clara y útil.

Pregunta: {question}
Historial de conversación: {chat_history}

Respuesta:`;

        this.generalChain = ChatPromptTemplate.fromTemplate(generalTemplate).pipe(this.model).pipe(this.parser);

        // Configurar cadena de noticias básica (sin documentos externos)
        const newsTemplate = `Eres un asistente especializado en noticias. Como no tengo acceso a noticias en tiempo real en este momento, te explicaré esto claramente.

Consulta sobre noticias: {question}
Historial: {chat_history}

Responde explicando que para obtener noticias actuales necesitas:
1. Acceso a fuentes de noticias en tiempo real
2. Conexión a APIs de noticias
3. Sistema completamente inicializado

Ofrece responder preguntas generales mientras tanto.`;

        this.newsChain = ChatPromptTemplate.fromTemplate(newsTemplate).pipe(this.model).pipe(this.parser);
    }

    /**
     * Procesar una consulta del usuario
     * @param {string} question - Pregunta del usuario
     * @returns {Object} Respuesta con contenido y metadata
     */
    async processQuery(question) {
        if (!this.isInitialized) {
            throw new Error('Sistema no inicializado');
        }

        try {
            // Obtener historial de conversación
            const chatHistory = this.conversationMemory ? 
                await this.conversationMemory.loadMemoryVariables({}) : { history: "" };

            // Clasificar la pregunta
            const classification = await this.classificationChain.invoke({ 
                question: question 
            });
            
            const isNewsQuery = classification.toLowerCase().trim().includes('noticias') || 
                               classification.toLowerCase().trim().includes('news');
            const queryType = isNewsQuery ? 'news' : 'general';

            let response;
            
            // Parámetros para las chains
            const chainParams = {
                question: question,
                chat_history: chatHistory.history || ""
            };
            
            // Procesar según tipo
            if (isNewsQuery && this.newsChain) {
                response = await this.newsChain.invoke(chainParams);
            } else if (this.generalChain) {
                response = await this.generalChain.invoke(chainParams);
            } else {
                // Fallback si las chains no están disponibles
                response = `Respuesta básica a: "${question}". El sistema está en modo simplificado.`;
            }

            // Guardar en memoria si está disponible
            if (this.conversationMemory) {
                await this.conversationMemory.saveContext(
                    { input: question },
                    { output: response }
                );
            }

            return response;
            
        } catch (error) {
            console.error('❌ Error en processQuery:', error);
            throw error;
        }
    }

    /**
     * Limpiar memoria conversacional
     */
    async clearMemory() {
        if (this.conversationMemory) {
            await this.conversationMemory.clear();
        }
    }

    /**
     * Obtener estadísticas del sistema
     * @returns {Object} Estadísticas del sistema
     */
    async getStats() {
        const memory = await this.conversationMemory.loadMemoryVariables({});
        
        return {
            initialized: this.isInitialized,
            documentStats: this.documentStats,
            memoryMessages: memory.history ? memory.history.length : 0,
            config: {
                llmProvider: CONFIG.llm.provider,
                embeddingProvider: CONFIG.embeddings.provider,
                chunkSize: CONFIG.retriever.chunkSize,
                retrieverK: CONFIG.retriever.k,
                maxMemoryTokens: CONFIG.memory.maxTokens
            },
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Método de consulta principal (alias para processQuery)
     * @param {string} question - La pregunta del usuario
     * @returns {Promise<Object>} Resultado con respuesta y tipo
     */
    async query(question) {
        try {
            const result = await this.processQuery(question);
            return {
                response: result,
                queryType: question.toLowerCase().includes('noticia') || 
                          question.toLowerCase().includes('news') ||
                          question.toLowerCase().includes('últim') ? 'news' : 'general'
            };
        } catch (error) {
            console.error('❌ Error en consulta:', error);
            return {
                response: `❌ Error procesando la consulta: ${error.message}`,
                queryType: 'error'
            };
        }
    }

    /**
     * Limpiar la memoria de conversación
     */
    async clearMemory() {
        try {
            if (this.conversationMemory) {
                await this.conversationMemory.clear();
                console.log('🧹 Memoria de conversación limpiada');
            }
            return { success: true };
        } catch (error) {
            console.error('❌ Error limpiando memoria:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Verificar si el sistema está listo
     * @returns {boolean} Estado de inicialización
     */
    isReady() {
        return this.isInitialized;
    }
}
