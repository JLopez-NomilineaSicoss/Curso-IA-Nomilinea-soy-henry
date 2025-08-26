"""
Pruebas unitarias para el módulo web API
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

# Agregar el directorio src al path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from web.api import app

class TestWebAPI:
    """Pruebas para la API web del chatbot"""
    
    @pytest.fixture
    def client(self):
        """Cliente de prueba para FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_memory(self):
        """Mock de ConversationMemory"""
        memory = Mock()
        memory.conversation_id = "test_conv_123"
        memory.messages = []
        memory.add_user_message = Mock()
        memory.add_assistant_message = Mock()
        memory.get_context_for_llm = Mock(return_value="Contexto de prueba")
        memory.get_conversation_summary = Mock(return_value={
            "conversation_id": "test_conv_123",
            "total_messages": 2,
            "user_messages": 1,
            "assistant_messages": 1
        })
        memory.export_conversation = Mock()
        memory.clear_memory = Mock()
        return memory
    
    @pytest.fixture
    def mock_preferences(self):
        """Mock de UserPreferences"""
        prefs = Mock()
        prefs.get_all_preferences = Mock(return_value={
            "search": {"max_results": 5, "language": "es"},
            "llm": {"provider": "groq", "temperature": 0.7},
            "streaming": {"enabled": True, "chunk_size": 100},
            "ui": {"theme": "light", "font_size": "medium"}
        })
        prefs.update_search_preferences = Mock()
        prefs.update_llm_preferences = Mock()
        prefs.update_streaming_preferences = Mock()
        prefs.update_ui_preferences = Mock()
        prefs.reset_to_defaults = Mock()
        return prefs
    
    def test_root_endpoint(self, client):
        """Prueba el endpoint raíz (página HTML)"""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Chatbot con Búsqueda Web" in response.text
        assert "🤖" in response.text
    
    @patch('web.api.memory')
    @patch('web.api.preferences')
    @patch('web.api.serper_searcher')
    @patch('web.api.source_formatter')
    @patch('web.api.groq_client')
    def test_chat_endpoint_success(self, mock_groq, mock_formatter, mock_searcher, mock_prefs, mock_mem, client, mock_memory, mock_preferences):
        """Prueba el endpoint de chat con éxito"""
        # Configurar mocks
        mock_mem.return_value = mock_memory
        mock_prefs.return_value = mock_preferences
        
        # Mock de búsqueda
        mock_search_result = Mock()
        mock_search_result.items = [
            Mock(title="Test Result", link="https://test.com", displayLink="test.com")
        ]
        mock_searcher.search = AsyncMock(return_value=mock_search_result)
        
        # Mock de formateo de fuentes
        mock_sources = [{"title": "Test", "url": "https://test.com", "domain": "test.com"}]
        mock_formatter.extract_sources_from_search = Mock(return_value=mock_sources)
        
        # Mock de LLM
        mock_groq.stream_chat = AsyncMock()
        mock_groq.stream_chat.__aiter__ = Mock(return_value=iter(["Respuesta", " de", " prueba"]))
        
        # Mock de preferencias
        mock_preferences.llm.temperature = 0.7
        mock_preferences.llm.max_tokens = 1000
        
        # Realizar petición
        response = client.post("/api/chat", json={
            "message": "¿Qué es Python?",
            "conversation_id": None
        })
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "sources" in data
        assert "conversation_id" in data
        assert "timestamp" in data
        assert data["response"] == "Respuesta de prueba"
        assert len(data["sources"]) == 1
    
    @patch('web.api.memory')
    @patch('web.api.preferences')
    def test_get_preferences(self, mock_prefs, mock_mem, client, mock_preferences):
        """Prueba obtener preferencias del usuario"""
        mock_prefs.return_value = mock_preferences
        
        response = client.get("/api/preferences")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "preferences" in data
        assert "search" in data["preferences"]
        assert "llm" in data["preferences"]
        assert "streaming" in data["preferences"]
        assert "ui" in data["preferences"]
    
    @patch('web.api.memory')
    @patch('web.api.preferences')
    def test_update_preferences(self, mock_prefs, mock_mem, client, mock_preferences):
        """Prueba actualizar preferencias del usuario"""
        mock_prefs.return_value = mock_preferences
        
        update_data = {
            "search": {"max_results": 10, "language": "en"},
            "llm": {"temperature": 0.5, "max_tokens": 2000}
        }
        
        response = client.put("/api/preferences", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verificar que se llamaron los métodos de actualización
        mock_preferences.update_search_preferences.assert_called_with(max_results=10, language="en")
        mock_preferences.update_llm_preferences.assert_called_with(temperature=0.5, max_tokens=2000)
    
    @patch('web.api.memory')
    @patch('web.api.preferences')
    def test_reset_preferences(self, mock_prefs, mock_mem, client, mock_preferences):
        """Prueba resetear preferencias a valores por defecto"""
        mock_prefs.return_value = mock_preferences
        
        response = client.post("/api/preferences/reset")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verificar que se llamó el método de reset
        mock_preferences.reset_to_defaults.assert_called_once()
    
    @patch('web.api.memory')
    def test_get_conversation_summary(self, mock_mem, client, mock_memory):
        """Prueba obtener resumen de conversación"""
        mock_mem.return_value = mock_memory
        
        response = client.get("/api/conversation/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "summary" in data
        assert data["summary"]["conversation_id"] == "test_conv_123"
        assert data["summary"]["total_messages"] == 2
    
    @patch('web.api.memory')
    def test_export_conversation(self, mock_mem, client, mock_memory):
        """Prueba exportar conversación"""
        mock_mem.return_value = mock_memory
        
        response = client.post("/api/conversation/export")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert "filename" in data
        
        # Verificar que se llamó el método de exportación
        mock_memory.export_conversation.assert_called_once()
    
    @patch('web.api.memory')
    def test_clear_conversation(self, mock_mem, client, mock_memory):
        """Prueba limpiar conversación"""
        mock_mem.return_value = mock_memory
        
        response = client.delete("/api/conversation/clear")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verificar que se llamó el método de limpieza
        mock_memory.clear_memory.assert_called_once()
    
    def test_chat_endpoint_invalid_json(self, client):
        """Prueba endpoint de chat con JSON inválido"""
        response = client.post("/api/chat", json={
            "invalid_field": "test"
        })
        
        # Debe fallar por validación de Pydantic
        assert response.status_code == 422
    
    def test_chat_endpoint_missing_message(self, client):
        """Prueba endpoint de chat sin mensaje"""
        response = client.post("/api/chat", json={})
        
        assert response.status_code == 422
    
    @patch('web.api.memory')
    @patch('web.api.preferences')
    @patch('web.api.serper_searcher')
    def test_chat_endpoint_search_error(self, mock_searcher, mock_prefs, mock_mem, client, mock_memory, mock_preferences):
        """Prueba endpoint de chat con error en búsqueda"""
        mock_mem.return_value = mock_memory
        mock_prefs.return_value = mock_preferences
        
        # Simular error en búsqueda
        mock_searcher.search = AsyncMock(side_effect=Exception("Error de búsqueda"))
        
        response = client.post("/api/chat", json={
            "message": "¿Qué es Python?"
        })
        
        # Debe fallar con error 500
        assert response.status_code == 500
        assert "Error de búsqueda" in response.json()["detail"]
    
    def test_preferences_endpoint_invalid_data(self, client):
        """Prueba endpoint de preferencias con datos inválidos"""
        response = client.put("/api/preferences", json={
            "invalid_section": {"key": "value"}
        })
        
        # Debe procesar solo las secciones válidas
        assert response.status_code == 200
    
    def test_cors_headers(self, client):
        """Prueba que los headers CORS estén configurados"""
        response = client.options("/api/chat")
        
        # Verificar que CORS esté configurado
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_api_documentation(self, client):
        """Prueba que la documentación de la API esté disponible"""
        response = client.get("/docs")
        
        # Verificar que Swagger UI esté disponible
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema(self, client):
        """Prueba que el esquema OpenAPI esté disponible"""
        response = client.get("/openapi.json")
        
        # Verificar esquema OpenAPI
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "Chatbot API"

if __name__ == '__main__':
    pytest.main([__file__])
