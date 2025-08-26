"""
Configuración de pytest y fixtures comunes
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture(scope="session")
def temp_dir():
    """Directorio temporal para toda la sesión de pruebas"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_env_vars():
    """Variables de entorno simuladas para pruebas"""
    env_vars = {
        "SERPER_API_KEY": "test_serper_key_12345",
        "GROQ_API_KEY": "test_groq_key_67890",
        "GOOGLE_AI_API_KEY": "test_openai_key_abcdef",
        "SERPER_API_URL": "https://google.serper.dev/search",
        "MAX_SEARCH_RESULTS": "5",
        "LLM_PROVIDER": "groq",
        "GROQ_MODEL": "llama3-8b-8192",
        "STREAMING_ENABLED": "true",
        "STREAMING_CHUNK_SIZE": "100"
    }
    
    # Simular variables de entorno
    with pytest.MonkeyPatch().context() as m:
        for key, value in env_vars.items():
            m.setenv(key, value)
        yield env_vars

@pytest.fixture
def mock_search_result():
    """Resultado de búsqueda simulado"""
    class MockItem:
        def __init__(self, title, link, display_link, snippet=""):
            self.title = title
            self.link = link
            self.displayLink = display_link
            self.snippet = snippet
    
    class MockSearchResult:
        def __init__(self):
            self.items = [
                MockItem("Python Programming Language", "https://python.org", "python.org", "Python is a programming language"),
                MockItem("Python Tutorial", "https://tutorial.python.org", "tutorial.python.org", "Learn Python programming"),
                MockItem("Python Documentation", "https://docs.python.org", "docs.python.org", "Official Python documentation")
            ]
    
    return MockSearchResult()

@pytest.fixture
def mock_sources():
    """Fuentes simuladas para pruebas"""
    return [
        {
            "title": "Python Programming Language",
            "url": "https://python.org",
            "domain": "python.org"
        },
        {
            "title": "Python Tutorial",
            "url": "https://tutorial.python.org",
            "domain": "tutorial.python.org"
        },
        {
            "title": "Python Documentation",
            "url": "https://docs.python.org",
            "domain": "docs.python.org"
        }
    ]

@pytest.fixture
def mock_llm_response():
    """Respuesta simulada del LLM"""
    return [
        "Python", " es", " un", " lenguaje", " de", " programación", 
        " de", " alto", " nivel", " muy", " popular", "."
    ]

@pytest.fixture
def mock_memory():
    """Memoria simulada para pruebas"""
    memory = Mock()
    memory.conversation_id = "test_conv_123"
    memory.messages = []
    memory.max_messages = 50
    memory.add_user_message = Mock()
    memory.add_assistant_message = Mock()
    memory.get_context_for_llm = Mock(return_value="")
    memory.get_conversation_summary = Mock(return_value={
        "conversation_id": "test_conv_123",
        "total_messages": 0,
        "user_messages": 0,
        "assistant_messages": 0
    })
    memory.clear_memory = Mock()
    memory.export_conversation = Mock()
    return memory

@pytest.fixture
def mock_preferences():
    """Preferencias simuladas para pruebas"""
    prefs = Mock()
    prefs.search.max_results = 5
    prefs.search.language = "es"
    prefs.search.region = "ES"
    prefs.llm.provider = "groq"
    prefs.llm.model = "llama3-8b-8192"
    prefs.llm.temperature = 0.7
    prefs.llm.max_tokens = 1000
    prefs.streaming.enabled = True
    prefs.streaming.chunk_size = 100
    prefs.ui.theme = "light"
    prefs.ui.font_size = "medium"
    
    prefs.get_all_preferences = Mock(return_value={
        "search": {"max_results": 5, "language": "es", "region": "ES"},
        "llm": {"provider": "groq", "model": "llama3-8b-8192", "temperature": 0.7, "max_tokens": 1000},
        "streaming": {"enabled": True, "chunk_size": 100},
        "ui": {"theme": "light", "font_size": "medium"}
    })
    
    prefs.update_search_preferences = Mock()
    prefs.update_llm_preferences = Mock()
    prefs.update_streaming_preferences = Mock()
    prefs.update_ui_preferences = Mock()
    prefs.reset_to_defaults = Mock()
    prefs.validate_preferences = Mock(return_value=True)
    
    return prefs

@pytest.fixture
def mock_serper_searcher():
    """Buscador Serper simulado para pruebas"""
    searcher = Mock()
    searcher.search = AsyncMock()
    return searcher

@pytest.fixture
def mock_groq_client():
    """Cliente Groq simulado para pruebas"""
    client = Mock()
    client.stream_chat = AsyncMock()
    return client

@pytest.fixture
def mock_source_formatter():
    """Formateador de fuentes simulado para pruebas"""
    formatter = Mock()
    formatter.extract_sources_from_search = Mock()
    formatter.format_sources_for_display = Mock()
    formatter.format_sources_for_prompt = Mock()
    formatter.validate_source_url = Mock(return_value=True)
    formatter.clean_source_title = Mock(side_effect=lambda x: x)
    return formatter

@pytest.fixture
def sample_conversation():
    """Conversación de ejemplo para pruebas"""
    return [
        {
            "role": "user",
            "content": "¿Qué es Python?",
            "timestamp": "2024-01-01T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "Python es un lenguaje de programación de alto nivel muy popular.",
            "timestamp": "2024-01-01T10:00:05Z",
            "sources": [
                {"title": "Python.org", "url": "https://python.org", "domain": "python.org"}
            ]
        },
        {
            "role": "user",
            "content": "¿Cuáles son sus características principales?",
            "timestamp": "2024-01-01T10:01:00Z"
        }
    ]

@pytest.fixture
def mock_fastapi_app():
    """Aplicación FastAPI simulada para pruebas"""
    app = Mock()
    app.get = Mock()
    app.post = Mock()
    app.put = Mock()
    app.delete = Mock()
    app.websocket = Mock()
    return app

# Configuración de pytest
def pytest_configure(config):
    """Configuración de pytest"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Modifica la colección de pruebas"""
    for item in items:
        # Marcar pruebas de integración
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        # Marcar pruebas unitarias
        elif "test_" in item.nodeid and "integration" not in item.nodeid:
            item.add_marker(pytest.mark.unit)
        # Marcar pruebas lentas
        if any(keyword in item.nodeid for keyword in ["search", "llm", "web"]):
            item.add_marker(pytest.mark.slow)
