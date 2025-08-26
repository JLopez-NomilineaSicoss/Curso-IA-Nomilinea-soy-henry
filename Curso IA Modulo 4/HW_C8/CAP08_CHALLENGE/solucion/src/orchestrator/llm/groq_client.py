"""
Cliente para Groq Cloud API
Proporciona funcionalidad de streaming de respuestas
"""

import os
import asyncio
from typing import AsyncGenerator, List, Dict, Any
import aiohttp
from util.logger import get_logger

logger = get_logger(__name__)

class GroqClient:
    """Cliente para Groq Cloud API con soporte para streaming"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        self.base_url = "https://api.groq.com/openai/v1"
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY no está configurada en las variables de entorno")
    
    async def stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """
        Genera respuestas en streaming usando Groq Cloud
        
        Args:
            messages: Lista de mensajes en formato OpenAI
            temperature: Temperatura para la generación
            max_tokens: Máximo número de tokens
            
        Yields:
            Tokens de respuesta en streaming
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"Error en Groq API: {response.status}")
                        yield "Error: No se pudo generar la respuesta"
                        return
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        
                        if line.startswith('data: '):
                            data = line[6:]  # Remover 'data: '
                            
                            if data == '[DONE]':
                                break
                            
                            try:
                                # Parsear JSON de la línea
                                import json
                                chunk = json.loads(data)
                                
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    
                                    if content:
                                        yield content
                                        
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"Error en streaming de Groq: {e}")
            yield f"Error: {str(e)}"
    
    async def generate_response(
        self, 
        prompt: str, 
        context: str = "",
        temperature: float = 0.7
    ) -> str:
        """
        Genera una respuesta completa (no streaming)
        
        Args:
            prompt: Prompt principal
            context: Contexto adicional
            temperature: Temperatura para la generación
            
        Returns:
            Respuesta generada
        """
        try:
            # Construir mensajes
            messages = []
            
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Usa la siguiente información como contexto: {context}"
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Generar respuesta
            response = ""
            async for token in self.stream_chat(messages, temperature):
                response += token
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return f"Error: No se pudo generar la respuesta - {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """Retorna lista de modelos disponibles en Groq"""
        return [
            "llama3-8b-8192",
            "llama3-70b-8192", 
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
