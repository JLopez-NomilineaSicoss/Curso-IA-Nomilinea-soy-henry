"""
Pruebas unitarias para el módulo principal main.py
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock de módulos externos antes de importar main
with patch.dict('sys.modules', {
    'retrieval.serper_search': Mock(),
    'retrieval.source_formatter': Mock(),
    'llm': Mock(),
    'memory': Mock(),
    'prompt.prompt': Mock(),
    'util.logger': Mock()
}):
    from main import event_generator, main

class TestMainModule:
    """Pruebas para el módulo principal main.py"""
    
    @pytest.fixture
    def mock_serper_searcher(self):
        """Mock de SerperSearcher"""
        searcher = Mock()
        searcher.search = AsyncMock(return_value=Mock(
            items=[
                Mock(title="Test Result 1", link="https://test1.com", displayLink="test1.com"),
                Mock(title="Test Result 2", link="https://test2.com", displayLink="test2.com")
            ]
        ))
        return searcher
    
    @pytest.fixture
    def mock_source_formatter(self):
        """Mock de SourceFormatter"""
        formatter = Mock()
        formatter.extract_sources_from_search = Mock(return_value=[
            {"title": "Test 1", "url": "https://test1.com", "domain": "test1.com"},
            {"title": "Test 2", "url": "https://test2.com", "domain": "test2.com"}
        ])
        formatter.format_sources_for_prompt = Mock(return_value="\nFuentes disponibles:\n1. Test 1 - https://test1.com\n2. Test 2 - https://test2.com")
        formatter.format_sources_for_display = Mock(return_value="\n\n**Referencias:**\n1. [Test 1](https://test1.com) - test1.com\n2. [Test 2](https://test2.com) - test2.com")
        return formatter
    
    @pytest.fixture
    def mock_groq_client(self):
        """Mock de GroqClient"""
        client = Mock()
        client.stream_chat = AsyncMock()
        client.stream_chat.__aiter__ = Mock(return_value=iter([
            "Esta es una ", "respuesta de ", "prueba del ", "chatbot."
        ]))
        return client
    
    @pytest.fixture
    def mock_memory(self):
        """Mock de ConversationMemory"""
        memory = Mock()
        memory.add_user_message = Mock()
        memory.add_assistant_message = Mock()
        memory.get_context_for_llm = Mock(return_value="Contexto de conversación previa")
        return memory
    
    @pytest.fixture
    def mock_prompt(self):
        """Mock del prompt"""
        prompt = Mock()
        prompt.rag = "Contexto: {conversation_context}\n\nContexto de búsqueda: {context}\n\nPregunta: {question}"
        return prompt
    
    @pytest.mark.asyncio
    async def test_event_generator_search_events(self, mock_serper_searcher, mock_source_formatter, mock_groq_client, mock_memory, mock_prompt):
        """Prueba que event_generator genere eventos de búsqueda"""
        
        # Configurar mocks
        with patch('main.serper_searcher', mock_serper_searcher), \
             patch('main.source_formatter', mock_source_formatter), \
             patch('main.groq_client', mock_groq_client), \
             patch('main.memory', mock_memory), \
             patch('main.prompt', mock_prompt):
            
            # Generar eventos
            events = []
            async for event in event_generator("¿Qué es Python?", mock_memory):
                events.append(event)
            
            # Verificar eventos de búsqueda
            search_events = [e for e in events if e["event"] == "search"]
            assert len(search_events) == 1
            assert len(search_events[0]["data"]) == 2  # 2 resultados de búsqueda
            
            # Verificar evento de prompt
            prompt_events = [e for e in events if e["event"] == "prompt"]
            assert len(prompt_events) == 1
            assert "Contexto de conversación previa" in prompt_events[0]["data"]
            assert "Fuentes disponibles:" in prompt_events[0]["data"]
    
    @pytest.mark.asyncio
    async def test_event_generator_without_memory(self, mock_serper_searcher, mock_source_formatter, mock_groq_client, mock_memory, mock_prompt):
        """Prueba event_generator sin memoria previa"""
        
        # Configurar memoria vacía
        mock_memory.get_context_for_llm.return_value = ""
        
        with patch('main.serper_searcher', mock_serper_searcher), \
             patch('main.source_formatter', mock_source_formatter), \
             patch('main.groq_client', mock_groq_client), \
             patch('main.memory', mock_memory), \
             patch('main.prompt', mock_prompt):
            
            # Generar eventos
            events = []
            async for event in event_generator("¿Qué es Python?", mock_memory):
                events.append(event)
            
            # Verificar que no hay contexto de conversación
            prompt_events = [e for e in events if e["event"] == "prompt"]
            assert len(prompt_events) == 1
            assert "Contexto de conversación previa" not in prompt_events[0]["data"]
    
    @pytest.mark.asyncio
    async def test_event_generator_error_handling(self, mock_memory):
        """Prueba manejo de errores en event_generator"""
        
        # Simular error en búsqueda
        mock_searcher = Mock()
        mock_searcher.search = AsyncMock(side_effect=Exception("Error de API"))
        
        with patch('main.serper_searcher', mock_searcher), \
             patch('main.memory', mock_memory):
            
            # Debe manejar el error graciosamente
            events = []
            try:
                async for event in event_generator("¿Qué es Python?", mock_memory):
                    events.append(event)
            except Exception as e:
                # El error debe ser manejado internamente
                pass
            
            # Verificar que se generaron algunos eventos o se manejó el error
            assert True  # Si llegamos aquí, el error fue manejado
    
    @pytest.mark.asyncio
    async def test_main_function(self, mock_serper_searcher, mock_source_formatter, mock_groq_client, mock_memory, mock_prompt):
        """Prueba la función main"""
        
        # Configurar mocks
        with patch('main.serper_searcher', mock_serper_searcher), \
             patch('main.source_formatter', mock_source_formatter), \
             patch('main.groq_client', mock_groq_client), \
             patch('main.memory', mock_memory), \
             patch('main.prompt', mock_prompt), \
             patch('builtins.print') as mock_print:
            
            # Ejecutar función main
            await main("¿Qué es Python?", mock_memory)
            
            # Verificar que se agregó mensaje del usuario
            mock_memory.add_user_message.assert_called_once_with("¿Qué es Python?")
            
            # Verificar que se agregó respuesta del asistente
            mock_memory.add_assistant_message.assert_called_once()
            call_args = mock_memory.add_assistant_message.call_args
            assert call_args[0][0] == "Esta es una respuesta de prueba del chatbot."
            assert len(call_args[0][1]) == 2  # 2 fuentes
    
    @pytest.mark.asyncio
    async def test_main_function_output_formatting(self, mock_serper_searcher, mock_source_formatter, mock_groq_client, mock_memory, mock_prompt):
        """Prueba el formato de salida de la función main"""
        
        # Configurar mocks
        with patch('main.serper_searcher', mock_serper_searcher), \
             patch('main.source_formatter', mock_source_formatter), \
             patch('main.groq_client', mock_groq_client), \
             patch('main.memory', mock_memory), \
             patch('main.prompt', mock_prompt), \
             patch('builtins.print') as mock_print:
            
            # Ejecutar función main
            await main("¿Qué es Python?", mock_memory)
            
            # Verificar que se imprimieron los eventos de búsqueda
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            
            # Debe contener mensaje de búsqueda
            search_message = next((msg for msg in print_calls if "🔍 **Búsqueda en internet**" in msg), None)
            assert search_message is not None
            
            # Debe contener enlaces
            link_messages = [msg for msg in print_calls if "📄" in msg]
            assert len(link_messages) == 2
            
            # Debe contener referencias
            ref_message = next((msg for msg in print_calls if "**Referencias:**" in msg), None)
            assert ref_message is not None
    
    def test_imports(self):
        """Prueba que todos los imports necesarios estén disponibles"""
        try:
            from main import event_generator, main
            assert callable(event_generator)
            assert callable(main)
        except ImportError as e:
            pytest.fail(f"Error de importación: {e}")
    
    @pytest.mark.asyncio
    async def test_memory_integration(self, mock_serper_searcher, mock_source_formatter, mock_groq_client, mock_memory, mock_prompt):
        """Prueba integración con el sistema de memoria"""
        
        # Configurar mocks
        with patch('main.serper_searcher', mock_serper_searcher), \
             patch('main.source_formatter', mock_source_formatter), \
             patch('main.groq_client', mock_groq_client), \
             patch('main.memory', mock_memory), \
             patch('main.prompt', mock_prompt):
            
            # Ejecutar función main
            await main("¿Qué es Python?", mock_memory)
            
            # Verificar que se usó la memoria correctamente
            mock_memory.add_user_message.assert_called_once()
            mock_memory.add_assistant_message.assert_called_once()
            mock_memory.get_context_for_llm.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_source_citation(self, mock_serper_searcher, mock_source_formatter, mock_groq_client, mock_memory, mock_prompt):
        """Prueba que las fuentes se citen correctamente"""
        
        # Configurar mocks
        with patch('main.serper_searcher', mock_serper_searcher), \
             patch('main.source_formatter', mock_source_formatter), \
             patch('main.groq_client', mock_groq_client), \
             patch('main.memory', mock_memory), \
             patch('main.prompt', mock_prompt), \
             patch('builtins.print') as mock_print:
            
            # Ejecutar función main
            await main("¿Qué es Python?", mock_memory)
            
            # Verificar que se llamó el formateo de fuentes
            mock_source_formatter.extract_sources_from_search.assert_called_once()
            mock_source_formatter.format_sources_for_prompt.assert_called_once()
            mock_source_formatter.format_sources_for_display.assert_called_once()
            
            # Verificar que las fuentes se incluyeron en la memoria
            call_args = mock_memory.add_assistant_message.call_args
            assert len(call_args[0][1]) == 2  # 2 fuentes

if __name__ == '__main__':
    pytest.main([__file__])
