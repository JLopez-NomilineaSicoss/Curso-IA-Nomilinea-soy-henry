"""
Módulo de memoria de conversación
Mantiene el historial de la conversación durante runtime
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from util.logger import get_logger

logger = get_logger(__name__)

@dataclass
class Message:
    """Representa un mensaje en la conversación"""
    role: str  # 'user' o 'assistant'
    content: str
    timestamp: datetime
    sources: Optional[List[Dict[str, str]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el mensaje a diccionario"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class ConversationMemory:
    """Maneja la memoria de conversación durante runtime"""
    
    def __init__(self, max_messages: int = 50):
        self.max_messages = max_messages
        self.messages: List[Message] = []
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Conversación iniciada con ID: {self.conversation_id}")
    
    def add_user_message(self, content: str) -> None:
        """Agrega un mensaje del usuario"""
        message = Message(
            role="user",
            content=content,
            timestamp=datetime.now()
        )
        self._add_message(message)
        logger.info(f"Mensaje de usuario agregado: {content[:50]}...")
    
    def add_assistant_message(self, content: str, sources: Optional[List[Dict[str, str]]] = None) -> None:
        """Agrega un mensaje del asistente con fuentes"""
        message = Message(
            role="assistant",
            content=content,
            timestamp=datetime.now(),
            sources=sources or []
        )
        self._add_message(message)
        logger.info(f"Mensaje del asistente agregado con {len(sources or [])} fuentes")
    
    def _add_message(self, message: Message) -> None:
        """Agrega un mensaje y mantiene el límite de memoria"""
        self.messages.append(message)
        
        # Mantener solo los últimos max_messages
        if len(self.messages) > self.max_messages:
            removed = self.messages.pop(0)
            logger.debug(f"Mensaje removido de memoria: {removed.content[:30]}...")
    
    def get_conversation_history(self, max_context: int = 10) -> List[Dict[str, str]]:
        """Obtiene el historial de conversación para contexto del LLM"""
        # Obtener solo los últimos max_context mensajes
        recent_messages = self.messages[-max_context:] if len(self.messages) > max_context else self.messages
        
        # Convertir a formato OpenAI
        history = []
        for msg in recent_messages:
            history.append({
                "role": msg.role,
                "content": msg.content
            })
        
        logger.debug(f"Historial de conversación obtenido: {len(history)} mensajes")
        return history
    
    def get_full_conversation(self) -> List[Message]:
        """Obtiene toda la conversación"""
        return self.messages.copy()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de la conversación"""
        user_messages = [msg for msg in self.messages if msg.role == "user"]
        assistant_messages = [msg for msg in self.messages if msg.role == "assistant"]
        
        total_sources = sum(len(msg.sources or []) for msg in assistant_messages)
        
        return {
            "conversation_id": self.conversation_id,
            "total_messages": len(self.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "total_sources_cited": total_sources,
            "start_time": self.messages[0].timestamp.isoformat() if self.messages else None,
            "last_message_time": self.messages[-1].timestamp.isoformat() if self.messages else None
        }
    
    def clear_memory(self) -> None:
        """Limpia toda la memoria de conversación"""
        self.messages.clear()
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info("Memoria de conversación limpiada")
    
    def export_conversation(self, filepath: str) -> None:
        """Exporta la conversación a un archivo JSON"""
        try:
            data = {
                "conversation_id": self.conversation_id,
                "summary": self.get_conversation_summary(),
                "messages": [msg.to_dict() for msg in self.messages]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Conversación exportada a: {filepath}")
            
        except Exception as e:
            logger.error(f"Error exportando conversación: {e}")
    
    def get_context_for_llm(self, current_query: str, max_context: int = 5) -> str:
        """Genera contexto para el LLM basado en la conversación reciente"""
        if not self.messages:
            return ""
        
        # Obtener mensajes recientes
        recent_messages = self.messages[-max_context:] if len(self.messages) > max_context else self.messages
        
        context_parts = []
        for msg in recent_messages:
            role_label = "Usuario" if msg.role == "user" else "Asistente"
            context_parts.append(f"{role_label}: {msg.content}")
        
        # Agregar la consulta actual
        context_parts.append(f"Consulta actual: {current_query}")
        
        context = "\n\n".join(context_parts)
        logger.debug(f"Contexto generado para LLM: {len(context)} caracteres")
        
        return context
