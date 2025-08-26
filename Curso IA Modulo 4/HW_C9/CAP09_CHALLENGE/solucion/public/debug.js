// =================================================================
// Script de Debugging para Diagnóstico de Conexiones
// =================================================================

class DebugHelper {
    constructor() {
        this.startTime = Date.now();
        this.logs = [];
        this.init();
    }

    init() {
        this.log('🔍 Iniciando diagnóstico...');
        this.checkElements();
        this.checkSocketIO();
        this.testConnection();
        this.setupDebugPanel();
    }

    log(message) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `[${timestamp}] ${message}`;
        this.logs.push(logEntry);
        console.log(logEntry);
        this.updateDebugPanel();
    }

    checkElements() {
        this.log('🔍 Verificando elementos HTML...');
        
        const elements = {
            'chatMessages': document.getElementById('chatMessages'),
            'messageInput': document.getElementById('messageInput'),
            'sendButton': document.getElementById('sendButton'),
            'clearButton': document.getElementById('clearButton'),
            'charCount': document.getElementById('charCount'),
            'statusDot': document.getElementById('statusDot'),
            'statusText': document.getElementById('statusText'),
            'totalQueries': document.getElementById('totalQueries'),
            'sessionTime': document.getElementById('sessionTime')
        };

        for (const [name, element] of Object.entries(elements)) {
            if (element) {
                this.log(`✅ ${name}: Encontrado`);
            } else {
                this.log(`❌ ${name}: NO ENCONTRADO`);
            }
        }
    }

    checkSocketIO() {
        this.log('🔌 Verificando Socket.IO...');
        
        if (typeof io !== 'undefined') {
            this.log('✅ Socket.IO está disponible');
            this.log(`📋 Versión Socket.IO: ${io.version || 'Desconocida'}`);
        } else {
            this.log('❌ Socket.IO NO está disponible');
        }
    }

    testConnection() {
        this.log('🌐 Probando conexión al servidor...');
        
        if (typeof io === 'undefined') {
            this.log('❌ No se puede probar - Socket.IO no disponible');
            return;
        }

        const testSocket = io();
        
        testSocket.on('connect', () => {
            this.log('✅ Conexión exitosa al servidor');
            testSocket.emit('test', { message: 'Prueba de conectividad' });
        });

        testSocket.on('disconnect', () => {
            this.log('⚠️ Desconectado del servidor');
        });

        testSocket.on('connect_error', (error) => {
            this.log(`❌ Error de conexión: ${error.message}`);
        });

        // Timeout para la prueba
        setTimeout(() => {
            if (testSocket.connected) {
                this.log('✅ Conexión estable después de 5 segundos');
            } else {
                this.log('❌ Conexión fallida después de 5 segundos');
            }
            testSocket.close();
        }, 5000);
    }

    setupDebugPanel() {
        // Crear panel de debug si no existe
        if (!document.getElementById('debugPanel')) {
            const panel = document.createElement('div');
            panel.id = 'debugPanel';
            panel.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                width: 300px;
                max-height: 400px;
                background: rgba(0,0,0,0.9);
                color: #00ff00;
                font-family: monospace;
                font-size: 12px;
                padding: 10px;
                border-radius: 5px;
                overflow-y: auto;
                z-index: 10000;
                display: none;
            `;
            
            // Título del panel
            const title = document.createElement('div');
            title.innerHTML = '<strong>🔍 DEBUG PANEL</strong><hr>';
            panel.appendChild(title);
            
            // Contenido de logs
            const content = document.createElement('div');
            content.id = 'debugContent';
            panel.appendChild(content);
            
            // Botón para mostrar/ocultar
            const toggleBtn = document.createElement('button');
            toggleBtn.innerHTML = '🔍 Debug';
            toggleBtn.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                z-index: 10001;
                background: #007acc;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                cursor: pointer;
            `;
            
            toggleBtn.onclick = () => {
                panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
            };
            
            document.body.appendChild(panel);
            document.body.appendChild(toggleBtn);
        }
    }

    updateDebugPanel() {
        const content = document.getElementById('debugContent');
        if (content) {
            content.innerHTML = this.logs.map(log => `<div>${log}</div>`).join('');
            content.scrollTop = content.scrollHeight;
        }
    }

    // Métodos de utilidad para testing manual
    testQuery(message = 'Prueba de consulta') {
        this.log(`🧪 Probando consulta: "${message}"`);
        
        if (typeof window.newsInterface !== 'undefined' && window.newsInterface.socket) {
            window.newsInterface.socket.emit('query', { text: message });
            this.log('📤 Consulta enviada');
        } else {
            this.log('❌ No hay interfaz de noticias disponible');
        }
    }

    getSystemInfo() {
        return {
            userAgent: navigator.userAgent,
            location: window.location.href,
            timestamp: new Date().toISOString(),
            uptime: Date.now() - this.startTime,
            logs: this.logs
        };
    }
}

// Inicializar automáticamente cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    window.debugHelper = new DebugHelper();
    
    // Agregar funciones globales para debugging manual
    window.debugTest = (message) => window.debugHelper.testQuery(message);
    window.debugInfo = () => console.table(window.debugHelper.getSystemInfo());
});

// También disponible para uso inmediato
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.debugHelper) {
            window.debugHelper = new DebugHelper();
        }
    });
} else {
    window.debugHelper = new DebugHelper();
}
