"""
Pruebas de integración del sistema completo
"""

import pytest
import asyncio
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock, Mock

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestSystemIntegration:
    """Pruebas de integración del sistema completo"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Directorio temporal para configuración"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def mock_env_vars(self):
        """Variables de entorno simuladas"""
        env_vars = {
            "SERPER_API_KEY": "test_serper_key",
            "GROQ_API_KEY": "test_groq_key",
            "GOOGLE_AI_API_KEY": "test_openai_key",
            "SERPER_API_URL": "https://google.serper.dev/search",
            "MAX_SEARCH_RESULTS": "5",
            "LLM_PROVIDER": "groq",
            "GROQ_MODEL": "llama3-8b-8192",
            "STREAMING_ENABLED": "true",
            "STREAMING_CHUNK_SIZE": "100"
        }
        
        # Simular variables de entorno
        with patch.dict(os.environ, env_vars):
            yield env_vars
    
    @pytest.mark.asyncio
    async def test_memory_and_preferences_integration(self, temp_config_dir, mock_env_vars):
        """Prueba integración entre memoria y preferencias"""
        
        with patch('config.user_preferences.Path') as mock_path:
            mock_path.return_value = Path(temp_config_dir)
            
            # Importar módulos
            from memory.conversation_memory import ConversationMemory
            from config.user_preferences import UserPreferences
            
            # Crear instancias
            memory = ConversationMemory()
            preferences = UserPreferences(config_dir=temp_config_dir)
            
            # Verificar que se pueden usar juntos
            memory.add_user_message("¿Qué es Python?")
            memory.add_assistant_message("Python es un lenguaje de programación", [])
            
            # Verificar que las preferencias afectan la memoria
            assert memory.max_messages == 50  # Valor por defecto
            preferences.update_ui_preferences(show_timestamps=False)
            
            # Verificar que se guardaron las preferencias
            assert os.path.exists(os.path.join(temp_config_dir, "user_preferences.json"))
    
    @pytest.mark.asyncio
    async def test_search_and_formatting_integration(self, mock_env_vars):
        """Prueba integración entre búsqueda y formateo"""
        
        # Mock de respuesta de búsqueda
        mock_search_result = type('MockSearchResult', (), {
            'items': [
                type('MockItem', (), {
                    'title': 'Test Result 1',
                    'link': 'https://test1.com',
                    'displayLink': 'test1.com',
                    'snippet': 'This is a test result'
                })(),
                type('MockItem', (), {
                    'title': 'Test Result 2',
                    'link': 'https://test2.com',
                    'displayLink': 'test2.com',
                    'snippet': 'Another test result'
                })()
            ]
        })()
        
        with patch('retrieval.serper_search.SerperSearcher.search', 
                  new_callable=AsyncMock, return_value=mock_search_result):
            
            from retrieval.serper_search import SerperSearcher
            from retrieval.source_formatter import SourceFormatter
            
            # Crear instancias
            searcher = SerperSearcher()
            formatter = SourceFormatter()
            
            # Realizar búsqueda
            search_results = await searcher.search("test query")
            
            # Formatear fuentes
            sources = formatter.extract_sources_from_search(search_results)
            formatted_sources = formatter.format_sources_for_display(sources)
            
            # Verificar integración
            assert len(sources) == 2
            assert "Test Result 1" in formatted_sources
            assert "https://test1.com" in formatted_sources
            assert "test1.com" in formatted_sources
    
    @pytest.mark.asyncio
    async def test_llm_and_memory_integration(self, mock_env_vars):
        """Prueba integración entre LLM y memoria"""
        
        # Mock de respuesta del LLM
        mock_tokens = ["Esta", " es", " una", " respuesta", " de", " prueba"]
        
        with patch('llm.groq_client.GroqClient.stream_chat', 
                  new_callable=AsyncMock) as mock_stream:
            mock_stream.__aiter__ = lambda self: iter(mock_tokens)
            
            from llm.groq_client import GroqClient
            from memory.conversation_memory import ConversationMemory
            
            # Crear instancias
            llm_client = GroqClient()
            memory = ConversationMemory()
            
            # Agregar mensaje del usuario
            memory.add_user_message("¿Qué es Python?")
            
            # Simular respuesta del LLM
            response_text = ""
            async for token in llm_client.stream_chat([{"role": "user", "content": "¿Qué es Python?"}]):
                response_text += token
            
            # Agregar respuesta a la memoria
            memory.add_assistant_message(response_text, [])
            
            # Verificar integración
            assert response_text == "Esta es una respuesta de prueba"
            assert len(memory.messages) == 2
            assert memory.messages[0].content == "¿Qué es Python?"
            assert memory.messages[1].content == "Esta es una respuesta de prueba"
    
    @pytest.mark.asyncio
    async def test_web_api_integration(self, temp_config_dir, mock_env_vars):
        """Prueba integración de la API web"""
        
        with patch('web.api.memory') as mock_memory, \
             patch('web.api.preferences') as mock_preferences, \
             patch('web.api.serper_searcher') as mock_searcher, \
             patch('web.api.source_formatter') as mock_formatter, \
             patch('web.api.groq_client') as mock_groq:
            
            # Configurar mocks
            mock_memory.return_value = type('MockMemory', (), {
                'conversation_id': 'test_conv_123',
                'add_user_message': Mock(),
                'add_assistant_message': Mock(),
                'get_context_for_llm': Mock(return_value=""),
                'messages': [type('MockMessage', (), {'timestamp': Mock()})()]
            })()
            
            mock_preferences.return_value = type('MockPrefs', (), {
                'llm': type('MockLLMPrefs', (), {'temperature': 0.7, 'max_tokens': 1000})(),
                'get_all_preferences': Mock(return_value={
                    'search': {'max_results': 5},
                    'llm': {'provider': 'groq'},
                    'streaming': {'enabled': True},
                    'ui': {'theme': 'light'}
                }),
                'update_search_preferences': Mock(),
                'update_llm_preferences': Mock(),
                'update_streaming_preferences': Mock(),
                'update_ui_preferences': Mock(),
                'reset_to_defaults': Mock()
            })()
            
            mock_search_result = type('MockSearchResult', (), {
                'items': [type('MockItem', (), {
                    'title': 'Test Result',
                    'link': 'https://test.com',
                    'displayLink': 'test.com'
                })()]
            })()
            mock_searcher.search = AsyncMock(return_value=mock_search_result)
            
            mock_sources = [{"title": "Test", "url": "https://test.com", "domain": "test.com"}]
            mock_formatter.extract_sources_from_search = Mock(return_value=mock_sources)
            
            mock_groq.stream_chat = AsyncMock()
            mock_groq.stream_chat.__aiter__ = lambda self: iter(["Respuesta", " de", " prueba"])
            
            # Importar y probar API
            from web.api import app
            from fastapi.testclient import TestClient
            
            client = TestClient(app)
            
            # Probar endpoint de chat
            response = client.post("/api/chat", json={
                "message": "¿Qué es Python?",
                "conversation_id": None
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "sources" in data
            assert data["response"] == "Respuesta de prueba"
    
    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, temp_config_dir, mock_env_vars):
        """Prueba el flujo completo del sistema"""
        
        # Mock de todos los componentes externos
        with patch('retrieval.serper_search.SerperSearcher.search') as mock_search, \
             patch('llm.groq_client.GroqClient.stream_chat') as mock_llm, \
             patch('config.user_preferences.Path') as mock_path:
            
            mock_path.return_value = Path(temp_config_dir)
            
            # Configurar mocks
            mock_search_result = type('MockSearchResult', (), {
                'items': [type('MockItem', (), {
                    'title': 'Python Programming',
                    'link': 'https://python.org',
                    'displayLink': 'python.org',
                    'snippet': 'Python is a programming language'
                })()]
            })()
            mock_search.return_value = mock_search_result
            
            mock_tokens = ["Python", " es", " un", " lenguaje", " de", " programación"]
            mock_llm.__aiter__ = lambda self: iter(mock_tokens)
            
            # Importar módulos
            from memory.conversation_memory import ConversationMemory
            from retrieval.serper_search import SerperSearcher
            from retrieval.source_formatter import SourceFormatter
            from llm.groq_client import GroqClient
            from config.user_preferences import UserPreferences
            
            # Crear instancias
            memory = ConversationMemory()
            searcher = SerperSearcher()
            formatter = SourceFormatter()
            llm_client = GroqClient()
            preferences = UserPreferences(config_dir=temp_config_dir)
            
            # Simular flujo completo
            user_message = "¿Qué es Python?"
            
            # 1. Agregar mensaje del usuario a la memoria
            memory.add_user_message(user_message)
            
            # 2. Realizar búsqueda
            search_results = await searcher.search(user_message)
            
            # 3. Extraer y formatear fuentes
            sources = formatter.extract_sources_from_search(search_results)
            formatted_sources = formatter.format_sources_for_display(sources)
            
            # 4. Generar respuesta del LLM
            response_text = ""
            async for token in llm_client.stream_chat([{"role": "user", "content": user_message}]):
                response_text += token
            
            # 5. Agregar respuesta a la memoria
            memory.add_assistant_message(response_text, sources)
            
            # Verificar flujo completo
            assert len(memory.messages) == 2
            assert memory.messages[0].content == user_message
            assert memory.messages[1].content == "Python es un lenguaje de programación"
            assert len(sources) == 1
            assert "python.org" in sources[0]["domain"]
            assert "Python Programming" in sources[0]["title"]
            
            # Verificar que las preferencias se guardaron
            assert os.path.exists(os.path.join(temp_config_dir, "user_preferences.json"))
    
    def test_module_imports(self):
        """Prueba que todos los módulos se puedan importar correctamente"""
        modules_to_test = [
            'memory.conversation_memory',
            'retrieval.serper_search',
            'retrieval.source_formatter',
            'llm.groq_client',
            'config.user_preferences',
            'web.api',
            'prompt.prompt',
            'util.logger'
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                assert True, f"Módulo {module_name} importado correctamente"
            except ImportError as e:
                pytest.fail(f"Error importando {module_name}: {e}")
    
    def test_configuration_consistency(self, temp_config_dir, mock_env_vars):
        """Prueba consistencia de configuración entre módulos"""
        
        with patch('config.user_preferences.Path') as mock_path:
            mock_path.return_value = Path(temp_config_dir)
            
            from config.user_preferences import UserPreferences
            from memory.conversation_memory import ConversationMemory
            
            # Crear instancias
            prefs = UserPreferences(config_dir=temp_config_dir)
            memory = ConversationMemory()
            
            # Verificar que los valores por defecto son consistentes
            assert prefs.search.max_results == 5
            assert prefs.llm.provider == "groq"
            assert prefs.streaming.enabled is True
            assert prefs.ui.theme == "light"
            
            # Verificar que la memoria tiene valores razonables
            assert memory.max_messages > 0
            assert memory.max_messages <= 1000  # Límite razonable
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, mock_env_vars):
        """Prueba manejo de errores en integración"""
        
        # Simular error en búsqueda
        with patch('retrieval.serper_search.SerperSearcher.search', 
                  new_callable=AsyncMock, side_effect=Exception("API Error")):
            
            from retrieval.serper_search import SerperSearcher
            from memory.conversation_memory import ConversationMemory
            
            searcher = SerperSearcher()
            memory = ConversationMemory()
            
            # Debe manejar el error graciosamente
            try:
                await searcher.search("test query")
                pytest.fail("Debería haber fallado")
            except Exception as e:
                assert "API Error" in str(e)
            
            # La memoria debe estar intacta
            assert len(memory.messages) == 0

if __name__ == '__main__':
    pytest.main([__file__])
