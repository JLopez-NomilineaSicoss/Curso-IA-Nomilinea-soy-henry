// =================================================================
// Sistema de Consulta de Noticias - Cliente Final Optimizado
// =================================================================

class NewsQueryInterface {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.isSystemReady = false;
        this.messageCount = 0;
        this.startTime = new Date();
        
        // Contadores por tipo
        this.newsCount = 0;
        this.generalCount = 0;
        
        this.initializeElements();
        this.initializeSocket();
        this.setupEventListeners();
        this.startSessionTimer();
        this.showWelcomeMessage();
    }

    // =================================================================
    // Inicialización
    // =================================================================

    initializeElements() {
        this.elements = {
            // Status
            statusDot: document.getElementById('statusDot'),
            statusText: document.getElementById('statusText'),
            
            // Chat
            chatMessages: document.getElementById('chatMessages'),
            messageInput: document.getElementById('messageInput'),
            sendButton: document.getElementById('sendButton'),
            charCount: document.getElementById('charCount'),
            
            // Stats
            totalQueries: document.getElementById('totalQueries'),
            newsQueries: document.getElementById('newsQueries'),
            generalQueries: document.getElementById('generalQueries'),
            sessionTime: document.getElementById('sessionTime'),
            
            // Actions
            clearChatBtn: document.getElementById('clearChatBtn'),
            exportChatBtn: document.getElementById('exportChatBtn'),
            
            // Config display
            llmProvider: document.getElementById('llmProvider'),
            embeddingProvider: document.getElementById('embeddingProvider')
        };

        // Verificar elementos críticos
        const criticalElements = ['chatMessages', 'messageInput', 'sendButton'];
        for (const elementId of criticalElements) {
            if (!this.elements[elementId]) {
                console.error(`❌ Elemento crítico no encontrado: ${elementId}`);
            }
        }
    }

    initializeSocket() {
        console.log('🔌 Conectando a Socket.IO...');
        this.socket = io({
            transports: ['websocket', 'polling'],
            timeout: 10000
        });
        
        this.socket.on('connect', () => {
            console.log('✅ Conectado al servidor');
            this.isConnected = true;
            this.updateConnectionStatus('connecting', 'Conectando...');
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Desconectado del servidor');
            this.isConnected = false;
            this.isSystemReady = false;
            this.updateConnectionStatus('error', 'Desconectado');
            this.addSystemMessage('❌ Conexión perdida. Reintentando...');
        });

        this.socket.on('connect_error', (error) => {
            console.error('❌ Error de conexión:', error);
            this.updateConnectionStatus('error', 'Error conexión');
            this.addSystemMessage('❌ Error conectando al servidor');
        });

        this.socket.on('systemStatus', (data) => {
            console.log('📊 Estado del sistema:', data);
            this.updateConnectionStatus('connecting', data.message);
            this.addSystemMessage(`⏳ ${data.message}`);
        });

        this.socket.on('systemReady', (data) => {
            console.log('✅ Sistema listo:', data);
            this.isSystemReady = true;
            this.updateConnectionStatus('connected', 'Sistema listo');
            this.updateConfiguration(data.config);
            this.addSystemMessage('✅ Sistema inicializado. ¡Puedes hacer consultas!');
        });

        this.socket.on('systemError', (data) => {
            console.error('❌ Error del sistema:', data);
            this.isSystemReady = false;
            this.updateConnectionStatus('error', 'Error sistema');
            this.addSystemMessage(`❌ Error: ${data.message}`);
        });

        this.socket.on('queryResponse', (data) => {
            console.log('📨 Respuesta recibida:', data);
            this.hideTypingIndicator();
            this.addMessage('assistant', data.response, data.queryType);
            this.updateQueryStats(data.queryType);
        });

        this.socket.on('queryError', (data) => {
            console.error('❌ Error en consulta:', data);
            this.hideTypingIndicator();
            this.addSystemMessage(`❌ Error: ${data.message}`);
        });

        this.socket.on('memoryCleared', (data) => {
            console.log('🧹 Memoria limpiada:', data);
            this.addSystemMessage('🧹 Memoria del sistema limpiada');
        });
    }

    setupEventListeners() {
        // Input de mensaje
        if (this.elements.messageInput) {
            this.elements.messageInput.addEventListener('input', () => {
                this.updateCharCounter();
            });

            this.elements.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // Botón enviar
        if (this.elements.sendButton) {
            this.elements.sendButton.addEventListener('click', () => {
                this.sendMessage();
            });
        }

        // Botón limpiar chat
        if (this.elements.clearChatBtn) {
            this.elements.clearChatBtn.addEventListener('click', () => {
                this.clearChat();
            });
        }

        // Botón exportar chat
        if (this.elements.exportChatBtn) {
            this.elements.exportChatBtn.addEventListener('click', () => {
                this.exportChat();
            });
        }
    }

    // =================================================================
    // Funciones Principales
    // =================================================================

    sendMessage() {
        const message = this.elements.messageInput?.value?.trim();
        
        if (!message) {
            this.showNotification('⚠️ Por favor, ingresa un mensaje', 'warning');
            return;
        }

        if (!this.isConnected) {
            this.showNotification('❌ No hay conexión con el servidor', 'error');
            return;
        }

        if (!this.isSystemReady) {
            this.showNotification('⏳ El sistema se está inicializando, espera un momento', 'warning');
            return;
        }

        // Agregar mensaje del usuario
        this.addMessage('user', message);
        
        // Limpiar input
        this.elements.messageInput.value = '';
        this.updateCharCounter();
        
        // Mostrar indicador de escritura
        this.showTypingIndicator();
        
        // Enviar al servidor
        this.socket.emit('query', { text: message });
        
        // Actualizar estadísticas
        this.messageCount++;
        this.updateStats();
    }

    addMessage(sender, content, queryType = null) {
        if (!this.elements.chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        let queryTypeBadge = '';
        if (queryType) {
            const typeText = queryType === 'news' ? '📰 Noticias' : '🤔 General';
            const typeClass = queryType === 'news' ? 'news' : 'general';
            queryTypeBadge = `<span class="query-type ${typeClass}">${typeText}</span>`;
        }
        
        const icon = sender === 'user' ? '👤' : '🤖';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">
                    ${queryTypeBadge}
                    <span class="message-icon">${icon}</span>
                    ${this.formatContent(content)}
                </div>
                <div class="message-time">${timestamp}</div>
            </div>
        `;
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addSystemMessage(content) {
        if (!this.elements.chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">
                    ${content}
                </div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            </div>
        `;
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatContent(content) {
        if (typeof content !== 'string') return content;
        
        // Convertir saltos de línea a <br>
        content = content.replace(/\n/g, '<br>');
        
        // Convertir markdown básico
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
        content = content.replace(/`(.*?)`/g, '<code>$1</code>');
        
        return content;
    }

    showTypingIndicator() {
        if (!this.elements.chatMessages) return;
        if (document.querySelector('.typing-indicator')) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-content">
                🤖 El asistente está escribiendo
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.elements.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // =================================================================
    // Utilidades de UI
    // =================================================================

    updateConnectionStatus(status, text) {
        if (this.elements.statusDot) {
            this.elements.statusDot.className = `status-dot ${status}`;
        }
        if (this.elements.statusText) {
            this.elements.statusText.textContent = text;
        }
    }

    updateConfiguration(config) {
        if (config?.llmProvider && this.elements.llmProvider) {
            this.elements.llmProvider.innerHTML = `${config.llmProvider} <span class="free-badge">GRATIS</span>`;
        }
        if (config?.embeddingProvider && this.elements.embeddingProvider) {
            this.elements.embeddingProvider.innerHTML = `${config.embeddingProvider} <span class="free-badge">GRATIS</span>`;
        }
    }

    updateCharCounter() {
        if (!this.elements.messageInput || !this.elements.charCount) return;
        
        const count = this.elements.messageInput.value.length;
        this.elements.charCount.textContent = count;
    }

    updateStats() {
        if (this.elements.totalQueries) {
            this.elements.totalQueries.textContent = this.messageCount;
        }
    }

    updateQueryStats(queryType) {
        if (queryType === 'news') {
            this.newsCount++;
            if (this.elements.newsQueries) {
                this.elements.newsQueries.textContent = this.newsCount;
            }
        } else if (queryType === 'general') {
            this.generalCount++;
            if (this.elements.generalQueries) {
                this.elements.generalQueries.textContent = this.generalCount;
            }
        }
    }

    startSessionTimer() {
        setInterval(() => {
            this.updateSessionTime();
        }, 1000);
    }

    updateSessionTime() {
        if (!this.elements.sessionTime) return;
        
        const now = new Date();
        const diff = now - this.startTime;
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        
        this.elements.sessionTime.textContent = `${minutes}m ${seconds}s`;
    }

    scrollToBottom() {
        if (this.elements.chatMessages) {
            setTimeout(() => {
                this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
            }, 100);
        }
    }

    // =================================================================
    // Acciones
    // =================================================================

    clearChat() {
        if (confirm('¿Estás seguro de que quieres limpiar el chat?')) {
            if (this.elements.chatMessages) {
                this.elements.chatMessages.innerHTML = '';
            }
            
            // Resetear estadísticas
            this.messageCount = 0;
            this.newsCount = 0;
            this.generalCount = 0;
            
            if (this.elements.totalQueries) this.elements.totalQueries.textContent = '0';
            if (this.elements.newsQueries) this.elements.newsQueries.textContent = '0';
            if (this.elements.generalQueries) this.elements.generalQueries.textContent = '0';
            
            // Limpiar memoria del servidor
            if (this.socket && this.isConnected) {
                this.socket.emit('clearMemory');
            }
            
            this.showNotification('✅ Chat limpiado correctamente', 'success');
            this.showWelcomeMessage();
        }
    }

    exportChat() {
        if (!this.elements.chatMessages) return;
        
        const messages = Array.from(this.elements.chatMessages.children);
        let exportText = `Sistema de Consulta de Noticias - Exportación\n`;
        exportText += `Fecha: ${new Date().toLocaleString()}\n`;
        exportText += `Total de mensajes: ${this.messageCount}\n`;
        exportText += `Consultas de noticias: ${this.newsCount}\n`;
        exportText += `Consultas generales: ${this.generalCount}\n`;
        exportText += `Tiempo de sesión: ${this.elements.sessionTime?.textContent || 'N/A'}\n`;
        exportText += `${'='.repeat(60)}\n\n`;

        messages.forEach((message) => {
            const content = message.querySelector('.message-text');
            const time = message.querySelector('.message-time');
            
            if (content && time) {
                const isUser = message.classList.contains('user');
                const isSystem = message.classList.contains('system-message');
                const sender = isUser ? 'Usuario' : isSystem ? 'Sistema' : 'Asistente';
                const text = content.textContent.replace(/\s+/g, ' ').trim();
                
                exportText += `[${time.textContent}] ${sender}: ${text}\n\n`;
            }
        });

        // Descargar archivo
        const blob = new Blob([exportText], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-noticias-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('✅ Chat exportado correctamente', 'success');
    }

    showWelcomeMessage() {
        setTimeout(() => {
            this.addSystemMessage(`
                🎉 <strong>¡Bienvenido al Sistema de Consulta de Noticias!</strong><br><br>
                📰 <strong>Consultas de noticias:</strong> Pregunta sobre eventos actuales<br>
                <em>Ejemplo: "¿Últimas noticias de tecnología?"</em><br><br>
                🤔 <strong>Consultas generales:</strong> Preguntas sobre cualquier tema<br>
                <em>Ejemplo: "¿Qué es la inteligencia artificial?"</em><br><br>
                🆓 <strong>Sistema 100% gratuito</strong> con APIs de Groq y Google AI<br>
                💬 <strong>Chat en tiempo real</strong> con memoria conversacional
            `);
        }, 1000);
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const colors = {
            success: '#10b981',
            error: '#ef4444', 
            warning: '#f59e0b',
            info: '#3b82f6'
        };
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border: 1px solid #e5e7eb;
            border-left: 4px solid ${colors[type] || colors.info};
            padding: 1rem 1.25rem;
            border-radius: 0.5rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            max-width: 400px;
            font-size: 0.875rem;
            animation: slideIn 0.3s ease;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
}

// =================================================================
// Estilos para animaciones y mejoras visuales
// =================================================================

const styles = document.createElement('style');
styles.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 1rem;
        font-style: italic;
        color: #64748b;
        animation: fadeIn 0.3s ease;
    }
    
    .typing-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .typing-dots {
        display: flex;
        gap: 0.25rem;
    }
    
    .typing-dots span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #3b82f6;
        animation: typing 1.4s infinite;
    }
    
    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% { transform: scale(1); opacity: 0.4; }
        30% { transform: scale(1.2); opacity: 1; }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .message {
        animation: fadeIn 0.3s ease;
    }
    
    .query-type {
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: 600;
        margin-right: 0.5rem;
        display: inline-block;
    }
    
    .query-type.news {
        background: #f59e0b;
        color: white;
    }
    
    .query-type.general {
        background: #10b981;
        color: white;
    }
    
    .message-icon {
        margin-right: 0.5rem;
        font-size: 1.1rem;
    }
`;
document.head.appendChild(styles);

// =================================================================
// Inicialización
// =================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Iniciando Sistema de Consulta de Noticias...');
    window.newsApp = new NewsQueryInterface();
});

// Manejo de errores globales
window.addEventListener('error', (event) => {
    console.error('❌ Error global:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('❌ Promesa rechazada:', event.reason);
});
