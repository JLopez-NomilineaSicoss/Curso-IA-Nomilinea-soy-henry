// =================================================================
// Sistema de Consulta de Noticias - JavaScript Cliente
// =================================================================

class NewsQueryInterface {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.isTyping = false;
        this.messageCount = 0;
        this.startTime = new Date();
        this.currentQuery = '';
        
        this.initializeElements();
        this.initializeSocket();
        this.setupEventListeners();
        this.showWelcomeMessage();
        this.showLoadingOverlay('Inicializando sistema...', 'Conectando con el servidor y cargando configuración');
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
            queryInput: document.getElementById('messageInput'),
            sendButton: document.getElementById('sendButton'),
            charCounter: document.getElementById('charCount'),
            
            // Sidebar stats
            totalQueries: document.getElementById('totalQueries'),
            newsQueries: document.getElementById('newsQueries'),
            generalQueries: document.getElementById('generalQueries'),
            sessionTime: document.getElementById('sessionTime'),
            
            // Actions
            clearChatBtn: document.getElementById('clearChatBtn'),
            exportChatBtn: document.getElementById('exportChatBtn'),
            
            // Configuration
            llmProvider: document.getElementById('llmProvider'),
            embeddingProvider: document.getElementById('embeddingProvider'),
            
            // Loading overlay
            loadingOverlay: document.getElementById('loadingOverlay'),
            loadingText: document.getElementById('loadingText'),
            loadingSubtext: document.getElementById('loadingSubtext'),
            progressBar: document.getElementById('progressBar')
        };
    }

    initializeSocket() {
        // Conectar a Socket.IO
        this.socket = io();
        
        // Event listeners para Socket.IO
        this.socket.on('connect', () => {
            console.log('✅ Conectado al servidor');
            this.isConnected = true;
            this.updateConnectionStatus('connected', 'Conectado');
            this.hideLoadingOverlay();
        });

        this.socket.on('disconnect', () => {
            console.log('❌ Desconectado del servidor');
            this.isConnected = false;
            this.updateConnectionStatus('error', 'Desconectado');
            this.addSystemMessage('Conexión perdida. Reintentando...', 'error');
        });

        this.socket.on('connect_error', () => {
            console.log('❌ Error de conexión');
            this.updateConnectionStatus('error', 'Error de conexión');
            this.hideLoadingOverlay();
            this.addSystemMessage('Error de conexión con el servidor', 'error');
        });

        this.socket.on('systemReady', (data) => {
            console.log('✅ Sistema listo:', data);
            this.updateConfiguration(data.config);
            this.addSystemMessage('Sistema inicializado correctamente. ¡Puedes empezar a hacer consultas!', 'success');
        });

        this.socket.on('systemError', (data) => {
            console.error('❌ Error del sistema:', data);
            this.addSystemMessage(`Error del sistema: ${data.message}`, 'error');
            this.hideLoadingOverlay();
        });

        this.socket.on('queryResponse', (data) => {
            this.handleQueryResponse(data);
        });

        this.socket.on('queryError', (data) => {
            this.handleQueryError(data);
        });
    }

    setupEventListeners() {
        // Input de consulta
        this.elements.queryInput.addEventListener('input', (e) => {
            this.updateCharCounter();
            this.currentQuery = e.target.value;
        });

        this.elements.queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendQuery();
            }
        });

        // Botón enviar
        this.elements.sendButton.addEventListener('click', () => {
            this.sendQuery();
        });

        // Acciones del sidebar
        this.elements.clearChatBtn.addEventListener('click', () => {
            this.clearChat();
        });

        this.elements.exportChatBtn.addEventListener('click', () => {
            this.exportChat();
        });

        // Actualizar tiempo de sesión cada segundo
        setInterval(() => {
            this.updateSessionTime();
        }, 1000);
    }

    // =================================================================
    // Manejo de Mensajes
    // =================================================================

    sendQuery() {
        const query = this.elements.queryInput.value.trim();
        
        if (!query) {
            this.showNotification('Por favor, ingresa una consulta', 'warning');
            return;
        }

        if (!this.isConnected) {
            this.showNotification('No hay conexión con el servidor', 'error');
            return;
        }

        if (this.isTyping) {
            this.showNotification('El sistema está procesando tu consulta anterior', 'warning');
            return;
        }

        // Agregar mensaje del usuario
        this.addMessage('user', query);
        
        // Limpiar input
        this.elements.queryInput.value = '';
        this.updateCharCounter();
        
        // Mostrar indicador de escritura
        this.showTypingIndicator();
        
        // Enviar consulta al servidor
        this.socket.emit('query', { text: query });
        
        // Incrementar contador
        this.messageCount++;
        this.updateStats();
    }

    handleQueryResponse(data) {
        this.hideTypingIndicator();
        
        // Agregar respuesta del asistente
        this.addMessage('assistant', data.response, data.queryType);
        
        // Actualizar estadísticas
        this.updateQueryTypeStats(data.queryType);
        
        console.log('✅ Respuesta recibida:', data);
    }

    handleQueryError(data) {
        this.hideTypingIndicator();
        
        this.addSystemMessage(`Error al procesar la consulta: ${data.message}`, 'error');
        
        console.error('❌ Error en consulta:', data);
    }

    // =================================================================
    // UI de Mensajes
    // =================================================================

    addMessage(sender, content, queryType = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        let queryTypeBadge = '';
        if (queryType) {
            queryTypeBadge = `<span class="query-type ${queryType}">${queryType === 'news' ? 'Consulta de Noticias' : 'Consulta General'}</span>`;
        }
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">
                    ${queryTypeBadge}
                    ${this.formatMessageContent(content, sender)}
                </div>
                <div class="message-time">${timestamp}</div>
            </div>
        `;
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addSystemMessage(content, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-triangle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">
                    <i class="${icons[type] || icons.info}"></i>
                    ${content}
                </div>
            </div>
        `;
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessageContent(content, sender) {
        if (sender === 'user') {
            return `<i class="fas fa-user"></i>${content}`;
        }
        
        // Formato para respuestas del asistente
        if (typeof content === 'string') {
            // Convertir markdown básico a HTML
            content = content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>')
                .replace(/`(.*?)`/g, '<code>$1</code>')
                .replace(/\n/g, '<br>');
                
            // Detectar y formatear listas
            if (content.includes('-') || content.includes('•')) {
                const lines = content.split('<br>');
                let formattedLines = [];
                let inList = false;
                
                for (let line of lines) {
                    const trimmed = line.trim();
                    if (trimmed.startsWith('-') || trimmed.startsWith('•')) {
                        if (!inList) {
                            formattedLines.push('<ul>');
                            inList = true;
                        }
                        formattedLines.push(`<li>${trimmed.substring(1).trim()}</li>`);
                    } else {
                        if (inList) {
                            formattedLines.push('</ul>');
                            inList = false;
                        }
                        if (trimmed) {
                            formattedLines.push(line);
                        }
                    }
                }
                
                if (inList) {
                    formattedLines.push('</ul>');
                }
                
                content = formattedLines.join('');
            }
        }
        
        return `<i class="fas fa-robot"></i>${content}`;
    }

    showTypingIndicator() {
        if (document.querySelector('.typing-indicator')) return;
        
        this.isTyping = true;
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
        this.isTyping = false;
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    showWelcomeMessage() {
        setTimeout(() => {
            this.addSystemMessage(`
                <h3><i class="fas fa-newspaper"></i> ¡Bienvenido al Sistema de Consulta de Noticias!</h3>
                <p>Este sistema utiliza inteligencia artificial para ayudarte a consultar noticias y responder preguntas generales.</p>
                <ul>
                    <li><strong>Consultas de noticias:</strong> Pregunta sobre eventos actuales, noticias específicas o temas de actualidad</li>
                    <li><strong>Consultas generales:</strong> Haz preguntas sobre cualquier tema y obtén respuestas informativas</li>
                    <li><strong>Memoria conversacional:</strong> El sistema recuerda el contexto de la conversación</li>
                </ul>
                <p><em>Ejemplo:</em> "¿Cuáles son las últimas noticias sobre tecnología?" o "¿Qué está pasando con el cambio climático?"</p>
            `, 'info');
        }, 1000);
    }

    scrollToBottom() {
        setTimeout(() => {
            this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        }, 100);
    }

    // =================================================================
    // Estado y Configuración
    // =================================================================

    updateConnectionStatus(status, text) {
        this.elements.statusDot.className = `status-dot ${status}`;
        this.elements.statusText.textContent = text;
    }

    updateConfiguration(config) {
        if (config.llmProvider) {
            this.elements.llmProvider.innerHTML = `${config.llmProvider} <span class="free-badge">GRATIS</span>`;
        }
        if (config.embeddingProvider) {
            this.elements.embeddingProvider.innerHTML = `${config.embeddingProvider} <span class="free-badge">GRATIS</span>`;
        }
    }

    updateCharCounter() {
        const count = this.elements.queryInput.value.length;
        this.elements.charCounter.textContent = count;
        
        // Actualizar el estilo del contador
        const counterContainer = this.elements.charCounter.parentElement;
        if (count > 450) {
            counterContainer.style.color = 'var(--error-color)';
        } else if (count > 350) {
            counterContainer.style.color = 'var(--warning-color)';
        } else {
            counterContainer.style.color = 'var(--text-secondary)';
        }
    }

    updateStats() {
        this.elements.totalQueries.textContent = this.messageCount;
    }

    updateQueryTypeStats(queryType) {
        const currentNews = parseInt(this.elements.newsQueries.textContent) || 0;
        const currentGeneral = parseInt(this.elements.generalQueries.textContent) || 0;
        
        if (queryType === 'news') {
            this.elements.newsQueries.textContent = currentNews + 1;
        } else {
            this.elements.generalQueries.textContent = currentGeneral + 1;
        }
    }

    updateSessionTime() {
        const now = new Date();
        const diff = now - this.startTime;
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        
        this.elements.sessionTime.textContent = `${minutes}m ${seconds}s`;
    }

    // =================================================================
    // Acciones
    // =================================================================

    clearChat() {
        if (confirm('¿Estás seguro de que quieres limpiar el chat? Esta acción no se puede deshacer.')) {
            this.elements.chatMessages.innerHTML = '';
            this.messageCount = 0;
            this.elements.totalQueries.textContent = '0';
            this.elements.newsQueries.textContent = '0';
            this.elements.generalQueries.textContent = '0';
            this.startTime = new Date();
            
            // Enviar evento al servidor para limpiar memoria
            this.socket.emit('clearMemory');
            
            this.showWelcomeMessage();
            this.showNotification('Chat limpiado correctamente', 'success');
        }
    }

    exportChat() {
        const messages = Array.from(this.elements.chatMessages.children);
        let exportText = `Sistema de Consulta de Noticias - Exportación del Chat\n`;
        exportText += `Fecha: ${new Date().toLocaleString()}\n`;
        exportText += `Total de consultas: ${this.messageCount}\n`;
        exportText += `Duración de sesión: ${this.elements.sessionTime.textContent}\n`;
        exportText += `${'='.repeat(60)}\n\n`;

        messages.forEach((message, index) => {
            const content = message.querySelector('.message-text');
            const time = message.querySelector('.message-time');
            const isUser = message.classList.contains('user');
            const isSystem = message.classList.contains('system-message');
            
            if (content) {
                let sender = isUser ? 'Usuario' : isSystem ? 'Sistema' : 'Asistente';
                let text = content.textContent.replace(/\s+/g, ' ').trim();
                let timestamp = time ? time.textContent : '';
                
                exportText += `[${timestamp}] ${sender}: ${text}\n\n`;
            }
        });

        // Crear y descargar archivo
        const blob = new Blob([exportText], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-export-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('Chat exportado correctamente', 'success');
    }

    // =================================================================
    // Loading y Notificaciones
    // =================================================================

    showLoadingOverlay(text, subtext = '') {
        this.elements.loadingText.textContent = text;
        this.elements.loadingSubtext.textContent = subtext;
        this.elements.loadingOverlay.style.display = 'flex';
        
        // Simular progreso
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress > 100) progress = 100;
            this.elements.progressBar.style.width = `${progress}%`;
            
            if (progress === 100) {
                clearInterval(interval);
            }
        }, 200);
    }

    hideLoadingOverlay() {
        setTimeout(() => {
            this.elements.loadingOverlay.style.display = 'none';
        }, 500);
    }

    showNotification(message, type = 'info') {
        // Crear notificación temporal
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--surface);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--${type === 'success' ? 'success' : type === 'error' ? 'error' : type === 'warning' ? 'warning' : 'primary'}-color);
            padding: 1rem 1.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-lg);
            z-index: 1001;
            max-width: 400px;
            animation: slideInRight 0.3s ease;
        `;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-triangle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <i class="${icons[type] || icons.info}" style="color: var(--${type === 'success' ? 'success' : type === 'error' ? 'error' : type === 'warning' ? 'warning' : 'primary'}-color);"></i>
                <span style="color: var(--text-primary); font-weight: 500;">${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remover después de 4 segundos
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
}

// =================================================================
// Inicialización
// =================================================================

// Agregar estilos para animaciones
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Iniciando Sistema de Consulta de Noticias...');
    window.newsApp = new NewsQueryInterface();
});

// Manejo de errores globales
window.addEventListener('error', (event) => {
    console.error('❌ Error global:', event.error);
    if (window.newsApp) {
        window.newsApp.showNotification('Se produjo un error inesperado', 'error');
    }
});

// Manejo de errores de promesas no capturadas
window.addEventListener('unhandledrejection', (event) => {
    console.error('❌ Promesa rechazada:', event.reason);
    if (window.newsApp) {
        window.newsApp.showNotification('Error en operación asíncrona', 'error');
    }
});
