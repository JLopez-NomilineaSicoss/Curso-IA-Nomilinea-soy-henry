// =================================================================
// Sistema de Consulta de Noticias - JavaScript Cliente Simplificado
// =================================================================

class NewsQueryInterface {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.messageCount = 0;
        this.startTime = new Date();
        
        this.initializeElements();
        this.initializeSocket();
        this.setupEventListeners();
        this.updateSessionTime();
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

        // Verificar que todos los elementos existen
        for (const [key, element] of Object.entries(this.elements)) {
            if (!element) {
                console.warn(`⚠️ Elemento no encontrado: ${key}`);
            }
        }
    }

    initializeSocket() {
        console.log('🔌 Conectando a Socket.IO...');
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('✅ Conectado al servidor');
            this.isConnected = true;
            this.updateConnectionStatus('connected', 'Conectado');
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Desconectado del servidor');
            this.isConnected = false;
            this.updateConnectionStatus('error', 'Desconectado');
        });

        this.socket.on('systemReady', (data) => {
            console.log('✅ Sistema listo:', data);
            this.updateConfiguration(data.config);
            this.addSystemMessage('🤖 Sistema inicializado correctamente. ¡Puedes empezar a hacer consultas!');
        });

        this.socket.on('systemError', (data) => {
            console.error('❌ Error del sistema:', data);
            this.addSystemMessage(`❌ Error del sistema: ${data.message}`);
        });

        this.socket.on('queryResponse', (data) => {
            console.log('📨 Respuesta recibida:', data);
            this.addMessage('assistant', data.response, data.queryType);
            this.updateQueryStats(data.queryType);
            this.hideTypingIndicator();
        });

        this.socket.on('queryError', (data) => {
            console.error('❌ Error en consulta:', data);
            this.addSystemMessage(`❌ Error: ${data.message}`);
            this.hideTypingIndicator();
        });

        this.socket.on('memoryCleared', () => {
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

        // Actualizar tiempo de sesión cada segundo
        setInterval(() => {
            this.updateSessionTime();
        }, 1000);
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
            const typeText = queryType === 'news' ? 'Noticias' : 'General';
            queryTypeBadge = `<span class="query-type ${queryType}">${typeText}</span>`;
        }
        
        const icon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">
                    ${queryTypeBadge}
                    <i class="${icon}"></i>
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
        
        return content;
    }

    showTypingIndicator() {
        if (!this.elements.chatMessages) return;
        if (document.querySelector('.typing-indicator')) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <i class="fas fa-robot"></i>
            El asistente está escribiendo
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
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
        if (queryType === 'news' && this.elements.newsQueries) {
            const current = parseInt(this.elements.newsQueries.textContent) || 0;
            this.elements.newsQueries.textContent = current + 1;
        } else if (queryType === 'general' && this.elements.generalQueries) {
            const current = parseInt(this.elements.generalQueries.textContent) || 0;
            this.elements.generalQueries.textContent = current + 1;
        }
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
            if (this.elements.totalQueries) this.elements.totalQueries.textContent = '0';
            if (this.elements.newsQueries) this.elements.newsQueries.textContent = '0';
            if (this.elements.generalQueries) this.elements.generalQueries.textContent = '0';
            
            // Limpiar memoria del servidor
            if (this.socket) {
                this.socket.emit('clearMemory');
            }
            
            this.showNotification('✅ Chat limpiado correctamente', 'success');
        }
    }

    exportChat() {
        if (!this.elements.chatMessages) return;
        
        const messages = Array.from(this.elements.chatMessages.children);
        let exportText = `Sistema de Consulta de Noticias - Chat Export\n`;
        exportText += `Fecha: ${new Date().toLocaleString()}\n`;
        exportText += `Total de mensajes: ${this.messageCount}\n`;
        exportText += `${'='.repeat(50)}\n\n`;

        messages.forEach((message) => {
            const content = message.querySelector('.message-text');
            const time = message.querySelector('.message-time');
            
            if (content && time) {
                const isUser = message.classList.contains('user');
                const sender = isUser ? 'Usuario' : 'Asistente';
                const text = content.textContent.replace(/\s+/g, ' ').trim();
                
                exportText += `[${time.textContent}] ${sender}: ${text}\n\n`;
            }
        });

        // Descargar archivo
        const blob = new Blob([exportText], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-export-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('✅ Chat exportado correctamente', 'success');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border: 1px solid #ddd;
            border-left: 4px solid ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#f59e0b'};
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            max-width: 300px;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 4000);
    }
}

// =================================================================
// Inicialización
// =================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Iniciando Sistema de Consulta de Noticias...');
    window.newsApp = new NewsQueryInterface();
    
    // Mensaje de bienvenida
    setTimeout(() => {
        if (window.newsApp) {
            window.newsApp.addSystemMessage(`
                📰 ¡Bienvenido al Sistema de Consulta de Noticias!<br><br>
                🤖 Puedes hacer consultas sobre noticias actuales o preguntas generales<br>
                💡 Ejemplos: "¿Últimas noticias de tecnología?" o "¿Qué es la IA?"<br>
                🆓 Sistema 100% gratuito con APIs de Groq y Google
            `);
        }
    }, 1000);
});

// Manejo de errores
window.addEventListener('error', (event) => {
    console.error('❌ Error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('❌ Promesa rechazada:', event.reason);
});
