"""
Pruebas unitarias para el cliente de Groq Cloud
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import os
import sys

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from llm.groq_client import GroqClient

class TestGroqClient:
    """Pruebas para la clase GroqClient"""
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock de variables de entorno"""
        with patch.dict(os.environ, {
            'GROQ_API_KEY': 'test_key',
            'GROQ_MODEL': 'llama3-8b-8192'
        }):
            yield
    
    @pytest.fixture
    def groq_client(self, mock_env_vars):
        """Instancia de GroqClient para pruebas"""
        return GroqClient()
    
    def test_init_with_valid_key(self, mock_env_vars):
        """Prueba inicialización con API key válida"""
        client = GroqClient()
        assert client.api_key == 'test_key'
        assert client.model == 'llama3-8b-8192'
        assert client.base_url == 'https://api.groq.com/openai/v1'
    
    def test_init_without_key(self):
        """Prueba inicialización sin API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GROQ_API_KEY no está configurada"):
                GroqClient()
    
    @pytest.mark.asyncio
    async def test_stream_chat_success(self, groq_client):
        """Prueba streaming de chat exitoso"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.content = AsyncMock()
        
        # Simular contenido de streaming
        async def mock_content():
            yield b'data: {"choices": [{"delta": {"content": "Hola"}}]}\n'
            yield b'data: {"choices": [{"delta": {"content": " mundo"}}]}\n'
            yield b'data: [DONE]\n'
        
        mock_response.content.__aiter__ = mock_content
        
        mock_session = Mock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = AsyncMock(return_value=mock_response)
        
        messages = [{"role": "user", "content": "Hola"}]
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            tokens = []
            async for token in groq_client.stream_chat(messages):
                tokens.append(token)
            
            assert len(tokens) == 2
            assert tokens[0] == "Hola"
            assert tokens[1] == " mundo"
    
    @pytest.mark.asyncio
    async def test_stream_chat_error_response(self, groq_client):
        """Prueba manejo de error en respuesta HTTP"""
        mock_response = Mock()
        mock_response.status = 500
        
        mock_session = Mock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = AsyncMock(return_value=mock_response)
        
        messages = [{"role": "user", "content": "Hola"}]
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            tokens = []
            async for token in groq_client.stream_chat(messages):
                tokens.append(token)
            
            assert len(tokens) == 1
            assert "Error: No se pudo generar la respuesta" in tokens[0]
    
    @pytest.mark.asyncio
    async def test_stream_chat_exception(self, groq_client):
        """Prueba manejo de excepciones en streaming"""
        mock_session = Mock()
        mock_session.__aenter__ = AsyncMock(side_effect=Exception("Network error"))
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        messages = [{"role": "user", "content": "Hola"}]
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            tokens = []
            async for token in groq_client.stream_chat(messages):
                tokens.append(token)
            
            assert len(tokens) == 1
            assert "Error: Network error" in tokens[0]
    
    @pytest.mark.asyncio
    async def test_generate_response(self, groq_client):
        """Prueba generación de respuesta completa"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.content = AsyncMock()
        
        # Simular contenido de streaming
        async def mock_content():
            yield b'data: {"choices": [{"delta": {"content": "Respuesta completa"}}]}\n'
            yield b'data: [DONE]\n'
        
        mock_response.content.__aiter__ = mock_content
        
        mock_session = Mock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = AsyncMock(return_value=mock_response)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            response = await groq_client.generate_response("Test prompt", "Test context")
            
            assert response == "Respuesta completa"
    
    @pytest.mark.asyncio
    async def test_generate_response_with_context(self, groq_client):
        """Prueba generación de respuesta con contexto"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.content = AsyncMock()
        
        async def mock_content():
            yield b'data: {"choices": [{"delta": {"content": "Respuesta con contexto"}}]}\n'
            yield b'data: [DONE]\n'
        
        mock_response.content.__aiter__ = mock_content
        
        mock_session = Mock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = AsyncMock(return_value=mock_response)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            response = await groq_client.generate_response("Test prompt", "Test context")
            
            assert response == "Respuesta con contexto"
    
    def test_get_available_models(self, groq_client):
        """Prueba obtención de modelos disponibles"""
        models = groq_client.get_available_models()
        
        assert isinstance(models, list)
        assert "llama3-8b-8192" in models
        assert "llama3-70b-8192" in models
        assert "mixtral-8x7b-32768" in models
        assert "gemma2-9b-it" in models

if __name__ == '__main__':
    pytest.main([__file__])
