"""
API web del chatbot usando FastAPI
Proporciona interfaz web y endpoints para configuración
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
import os
import sys

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from memory import ConversationMemory
from config import UserPreferences
from retrieval.serper_search import SerperSearcher
from retrieval.source_formatter import SourceFormatter
from llm import GroqClient
from util.logger import get_logger

logger = get_logger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Chatbot API",
    description="API para chatbot con capacidad de búsqueda en internet",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Instancias globales
memory = ConversationMemory()
preferences = UserPreferences()
serper_searcher = SerperSearcher()
source_formatter = SourceFormatter()
groq_client = GroqClient()

# Modelos Pydantic para la API
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, str]]
    conversation_id: str
    timestamp: str

class PreferenceUpdate(BaseModel):
    section: str  # search, llm, streaming, ui
    key: str
    value: Any

class PreferenceResponse(BaseModel):
    success: bool
    message: str
    preferences: Dict[str, Any]

# Endpoints de la API

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página principal del chatbot"""
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chatbot con Búsqueda Web</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 30px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .chat-container {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                max-height: 400px;
                overflow-y: auto;
            }
            .input-container {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            input[type="text"] {
                flex: 1;
                padding: 15px;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
            }
            button {
                padding: 15px 30px;
                border: none;
                border-radius: 25px;
                background: #4CAF50;
                color: white;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover {
                background: #45a049;
            }
            .message {
                margin: 10px 0;
                padding: 15px;
                border-radius: 15px;
                max-width: 80%;
            }
            .user-message {
                background: rgba(76, 175, 80, 0.3);
                margin-left: auto;
                text-align: right;
            }
            .bot-message {
                background: rgba(255, 255, 255, 0.2);
            }
            .sources {
                font-size: 0.9em;
                margin-top: 10px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
            .preferences-btn {
                background: #2196F3;
                margin-right: 10px;
            }
            .preferences-btn:hover {
                background: #1976D2;
            }
            .preferences-panel {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin-top: 20px;
                display: none;
            }
            .preference-group {
                margin-bottom: 20px;
            }
            .preference-group h3 {
                margin-bottom: 10px;
                color: #FFD700;
            }
            .preference-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 10px 0;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
            .preference-item input, .preference-item select {
                padding: 8px;
                border: none;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Chatbot con Búsqueda Web</h1>
            
            <div class="chat-container" id="chatContainer">
                <div class="message bot-message">
                    ¡Hola! Soy tu asistente con capacidad de búsqueda en internet. 
                    ¿En qué puedo ayudarte hoy?
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="Escribe tu pregunta aquí..." />
                <button onclick="sendMessage()">Enviar</button>
                <button class="preferences-btn" onclick="togglePreferences()">⚙️ Preferencias</button>
            </div>
            
            <div class="preferences-panel" id="preferencesPanel">
                <h2>Configuración de Preferencias</h2>
                
                <div class="preference-group">
                    <h3>🔍 Búsqueda</h3>
                    <div class="preference-item">
                        <label>Máximo de resultados:</label>
                        <input type="number" id="maxResults" min="1" max="20" value="5" />
                    </div>
                    <div class="preference-item">
                        <label>Idioma:</label>
                        <select id="language">
                            <option value="es">Español</option>
                            <option value="en">English</option>
                            <option value="fr">Français</option>
                        </select>
                    </div>
                </div>
                
                <div class="preference-group">
                    <h3>🤖 Modelo de Lenguaje</h3>
                    <div class="preference-item">
                        <label>Temperatura:</label>
                        <input type="range" id="temperature" min="0" max="2" step="0.1" value="0.7" />
                        <span id="tempValue">0.7</span>
                    </div>
                    <div class="preference-item">
                        <label>Máximo de tokens:</label>
                        <input type="number" id="maxTokens" min="100" max="4000" value="1000" />
                    </div>
                </div>
                
                <div class="preference-group">
                    <h3>📡 Streaming</h3>
                    <div class="preference-item">
                        <label>Habilitar streaming:</label>
                        <input type="checkbox" id="streamingEnabled" checked />
                    </div>
                    <div class="preference-item">
                        <label>Tamaño de chunk:</label>
                        <input type="number" id="chunkSize" min="10" max="500" value="100" />
                    </div>
                </div>
                
                <button onclick="savePreferences()">💾 Guardar Preferencias</button>
                <button onclick="resetPreferences()" style="background: #f44336;">🔄 Resetear</button>
            </div>
        </div>
        
        <script>
            let conversationId = null;
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Agregar mensaje del usuario
                addMessage(message, 'user');
                input.value = '';
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: message,
                            conversation_id: conversationId
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        addMessage(data.response, 'bot', data.sources);
                        conversationId = data.conversation_id;
                    } else {
                        addMessage('Error: ' + data.message, 'bot');
                    }
                } catch (error) {
                    addMessage('Error de conexión: ' + error.message, 'bot');
                }
            }
            
            function addMessage(text, sender, sources = null) {
                const container = document.getElementById('chatContainer');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                
                let content = text;
                if (sources && sources.length > 0) {
                    content += '<div class="sources"><strong>Fuentes:</strong><br>';
                    sources.forEach((source, index) => {
                        content += `${index + 1}. <a href="${source.url}" target="_blank" style="color: #FFD700;">${source.title}</a><br>`;
                    });
                    content += '</div>';
                }
                
                messageDiv.innerHTML = content;
                container.appendChild(messageDiv);
                container.scrollTop = container.scrollHeight;
            }
            
            function togglePreferences() {
                const panel = document.getElementById('preferencesPanel');
                panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
            }
            
            function savePreferences() {
                const preferences = {
                    search: {
                        max_results: parseInt(document.getElementById('maxResults').value),
                        language: document.getElementById('language').value
                    },
                    llm: {
                        temperature: parseFloat(document.getElementById('temperature').value),
                        max_tokens: parseInt(document.getElementById('maxTokens').value)
                    },
                    streaming: {
                        enabled: document.getElementById('streamingEnabled').checked,
                        chunk_size: parseInt(document.getElementById('chunkSize').value)
                    }
                };
                
                fetch('/api/preferences', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(preferences)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Preferencias guardadas exitosamente');
                    } else {
                        alert('Error guardando preferencias: ' + data.message);
                    }
                })
                .catch(error => {
                    alert('Error de conexión: ' + error.message);
                });
            }
            
            function resetPreferences() {
                if (confirm('¿Estás seguro de que quieres resetear todas las preferencias?')) {
                    fetch('/api/preferences/reset', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Preferencias reseteadas exitosamente');
                            location.reload();
                        } else {
                            alert('Error reseteando preferencias: ' + data.message);
                        }
                    })
                    .catch(error => {
                        alert('Error de conexión: ' + error.message);
                    });
                }
            }
            
            // Event listeners
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            document.getElementById('temperature').addEventListener('input', function(e) {
                document.getElementById('tempValue').textContent = e.target.value;
            });
            
            // Cargar preferencias al iniciar
            window.addEventListener('load', function() {
                fetch('/api/preferences')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const prefs = data.preferences;
                        document.getElementById('maxResults').value = prefs.search.max_results;
                        document.getElementById('language').value = prefs.search.language;
                        document.getElementById('temperature').value = prefs.llm.temperature;
                        document.getElementById('tempValue').textContent = prefs.llm.temperature;
                        document.getElementById('maxTokens').value = prefs.llm.max_tokens;
                        document.getElementById('streamingEnabled').checked = prefs.streaming.enabled;
                        document.getElementById('chunkSize').value = prefs.streaming.chunk_size;
                    }
                })
                .catch(error => console.error('Error cargando preferencias:', error));
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Endpoint para enviar mensajes al chatbot"""
    try:
        # Agregar mensaje del usuario a la memoria
        memory.add_user_message(request.message)
        
        # Realizar búsqueda
        search_results = await serper_searcher.search(request.message)
        sources = source_formatter.extract_sources_from_search(search_results)
        
        # Generar respuesta usando Groq
        messages = [
            {"role": "user", "content": request.message}
        ]
        
        # Obtener contexto de conversación
        conversation_context = memory.get_context_for_llm(request.message)
        if conversation_context:
            messages.insert(0, {
                "role": "system", 
                "content": f"Contexto de conversación: {conversation_context}"
            })
        
        # Generar respuesta
        response_text = ""
        async for token in groq_client.stream_chat(
            messages, 
            temperature=preferences.llm.temperature,
            max_tokens=preferences.llm.max_tokens
        ):
            response_text += token
        
        # Agregar respuesta a la memoria
        memory.add_assistant_message(response_text, sources)
        
        return ChatResponse(
            response=response_text,
            sources=sources,
            conversation_id=memory.conversation_id,
            timestamp=memory.messages[-1].timestamp.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error en chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/preferences", response_model=PreferenceResponse)
async def get_preferences():
    """Obtiene todas las preferencias del usuario"""
    try:
        return PreferenceResponse(
            success=True,
            message="Preferencias obtenidas exitosamente",
            preferences=preferences.get_all_preferences()
        )
    except Exception as e:
        logger.error(f"Error obteniendo preferencias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/preferences", response_model=PreferenceResponse)
async def update_preferences(prefs: Dict[str, Any]):
    """Actualiza las preferencias del usuario"""
    try:
        # Actualizar preferencias según la sección
        if 'search' in prefs:
            preferences.update_search_preferences(**prefs['search'])
        if 'llm' in prefs:
            preferences.update_llm_preferences(**prefs['llm'])
        if 'streaming' in prefs:
            preferences.update_streaming_preferences(**prefs['streaming'])
        if 'ui' in prefs:
            preferences.update_ui_preferences(**prefs['ui'])
        
        return PreferenceResponse(
            success=True,
            message="Preferencias actualizadas exitosamente",
            preferences=preferences.get_all_preferences()
        )
        
    except Exception as e:
        logger.error(f"Error actualizando preferencias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/preferences/reset", response_model=PreferenceResponse)
async def reset_preferences():
    """Resetea las preferencias a valores por defecto"""
    try:
        preferences.reset_to_defaults()
        
        return PreferenceResponse(
            success=True,
            message="Preferencias reseteadas exitosamente",
            preferences=preferences.get_all_preferences()
        )
        
    except Exception as e:
        logger.error(f"Error reseteando preferencias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversation/summary")
async def get_conversation_summary():
    """Obtiene un resumen de la conversación actual"""
    try:
        return {
            "success": True,
            "summary": memory.get_conversation_summary()
        }
    except Exception as e:
        logger.error(f"Error obteniendo resumen: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversation/export")
async def export_conversation():
    """Exporta la conversación actual"""
    try:
        filename = f"conversation_{memory.conversation_id}.json"
        filepath = os.path.join("exports", filename)
        
        # Crear directorio si no existe
        os.makedirs("exports", exist_ok=True)
        
        memory.export_conversation(filepath)
        
        return {
            "success": True,
            "message": "Conversación exportada exitosamente",
            "filename": filename
        }
        
    except Exception as e:
        logger.error(f"Error exportando conversación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/conversation/clear")
async def clear_conversation():
    """Limpia la memoria de conversación"""
    try:
        memory.clear_memory()
        
        return {
            "success": True,
            "message": "Conversación limpiada exitosamente"
        }
        
    except Exception as e:
        logger.error(f"Error limpiando conversación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket para streaming en tiempo real
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para chat en tiempo real"""
    await websocket.accept()
    
    try:
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Procesar mensaje
            memory.add_user_message(message_data['message'])
            
            # Realizar búsqueda
            search_results = await serper_searcher.search(message_data['message'])
            sources = source_formatter.extract_sources_from_search(search_results)
            
            # Generar respuesta con streaming
            messages = [{"role": "user", "content": message_data['message']}]
            
            # Obtener contexto de conversación
            conversation_context = memory.get_context_for_llm(message_data['message'])
            if conversation_context:
                messages.insert(0, {
                    "role": "system", 
                    "content": f"Contexto de conversación: {conversation_context}"
                })
            
            # Enviar respuesta token por token
            response_text = ""
            async for token in groq_client.stream_chat(
                messages, 
                temperature=preferences.llm.temperature,
                max_tokens=preferences.llm.max_tokens
            ):
                response_text += token
                
                # Enviar token al cliente
                await websocket.send_text(json.dumps({
                    "type": "token",
                    "content": token
                }))
            
            # Enviar fuentes
            await websocket.send_text(json.dumps({
                "type": "sources",
                "sources": sources
            }))
            
            # Agregar respuesta a la memoria
            memory.add_assistant_message(response_text, sources)
            
    except WebSocketDisconnect:
        logger.info("Cliente WebSocket desconectado")
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
