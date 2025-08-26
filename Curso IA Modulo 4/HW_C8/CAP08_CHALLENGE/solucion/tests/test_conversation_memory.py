"""
Pruebas unitarias para el módulo de memoria de conversación
"""

import pytest
import json
import tempfile
import os
from datetime import datetime
from unittest.mock import patch

# Agregar el directorio src al path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from memory.conversation_memory import ConversationMemory, Message

class TestConversationMemory:
    """Pruebas para la clase ConversationMemory"""
    
    def test_init(self):
        """Prueba inicialización de la memoria"""
        memory = ConversationMemory(max_messages=30)
        
        assert memory.max_messages == 30
        assert len(memory.messages) == 0
        assert memory.conversation_id is not None
        assert len(memory.conversation_id) > 0
    
    def test_add_user_message(self):
        """Prueba agregar mensaje de usuario"""
        memory = ConversationMemory()
        content = "¿Cómo está el clima hoy?"
        
        memory.add_user_message(content)
        
        assert len(memory.messages) == 1
        assert memory.messages[0].role == "user"
        assert memory.messages[0].content == content
        assert memory.messages[0].sources is None
    
    def test_add_assistant_message(self):
        """Prueba agregar mensaje del asistente con fuentes"""
        memory = ConversationMemory()
        content = "El clima está soleado según el pronóstico"
        sources = [
            {"title": "Pronóstico del tiempo", "url": "https://weather.com", "domain": "weather.com"}
        ]
        
        memory.add_assistant_message(content, sources)
        
        assert len(memory.messages) == 1
        assert memory.messages[0].role == "assistant"
        assert memory.messages[0].content == content
        assert memory.messages[0].sources == sources
    
    def test_max_messages_limit(self):
        """Prueba límite de mensajes en memoria"""
        memory = ConversationMemory(max_messages=3)
        
        # Agregar 4 mensajes
        for i in range(4):
            memory.add_user_message(f"Mensaje {i}")
        
        # Solo deben quedar los últimos 3
        assert len(memory.messages) == 3
        assert memory.messages[0].content == "Mensaje 1"
        assert memory.messages[-1].content == "Mensaje 3"
    
    def test_get_conversation_history(self):
        """Prueba obtención de historial de conversación"""
        memory = ConversationMemory()
        
        # Agregar algunos mensajes
        memory.add_user_message("Hola")
        memory.add_assistant_message("¡Hola! ¿En qué puedo ayudarte?")
        memory.add_user_message("¿Cómo estás?")
        
        history = memory.get_conversation_history(max_context=2)
        
        assert len(history) == 2
        assert history[0]["role"] == "assistant"
        assert history[1]["role"] == "user"
        assert history[1]["content"] == "¿Cómo estás?"
    
    def test_get_conversation_summary(self):
        """Prueba obtención de resumen de conversación"""
        memory = ConversationMemory()
        
        # Agregar mensajes con fuentes
        memory.add_user_message("Pregunta 1")
        memory.add_assistant_message("Respuesta 1", [{"title": "Fuente 1", "url": "url1"}])
        memory.add_user_message("Pregunta 2")
        memory.add_assistant_message("Respuesta 2", [{"title": "Fuente 2", "url": "url2"}])
        
        summary = memory.get_conversation_summary()
        
        assert summary["total_messages"] == 4
        assert summary["user_messages"] == 2
        assert summary["assistant_messages"] == 2
        assert summary["total_sources_cited"] == 2
        assert summary["conversation_id"] == memory.conversation_id
    
    def test_clear_memory(self):
        """Prueba limpieza de memoria"""
        memory = ConversationMemory()
        
        # Agregar mensajes
        memory.add_user_message("Test")
        memory.add_assistant_message("Test response")
        
        assert len(memory.messages) == 2
        
        # Limpiar memoria
        old_id = memory.conversation_id
        memory.clear_memory()
        
        assert len(memory.messages) == 0
        assert memory.conversation_id != old_id
    
    def test_get_context_for_llm(self):
        """Prueba generación de contexto para LLM"""
        memory = ConversationMemory()
        
        # Agregar conversación
        memory.add_user_message("¿Qué es Python?")
        memory.add_assistant_message("Python es un lenguaje de programación")
        memory.add_user_message("¿Es fácil de aprender?")
        
        context = memory.get_context_for_llm("¿Dónde puedo aprender Python?")
        
        assert "Usuario: ¿Qué es Python?" in context
        assert "Asistente: Python es un lenguaje de programación" in context
        assert "Usuario: ¿Es fácil de aprender?" in context
        assert "Consulta actual: ¿Dónde puedo aprender Python?" in context
    
    def test_export_conversation(self):
        """Prueba exportación de conversación"""
        memory = ConversationMemory()
        
        # Agregar mensajes
        memory.add_user_message("Test question")
        memory.add_assistant_message("Test answer", [{"title": "Test source", "url": "test.com"}])
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # Exportar conversación
            memory.export_conversation(temp_file)
            
            # Verificar que el archivo existe y tiene contenido
            assert os.path.exists(temp_file)
            
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "conversation_id" in data
            assert "summary" in data
            assert "messages" in data
            assert len(data["messages"]) == 2
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_message_to_dict(self):
        """Prueba conversión de mensaje a diccionario"""
        memory = ConversationMemory()
        memory.add_user_message("Test message")
        
        message = memory.messages[0]
        message_dict = message.to_dict()
        
        assert message_dict["role"] == "user"
        assert message_dict["content"] == "Test message"
        assert "timestamp" in message_dict
        assert message_dict["sources"] is None

if __name__ == '__main__':
    pytest.main([__file__])
