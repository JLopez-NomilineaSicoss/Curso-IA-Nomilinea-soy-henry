"""
Módulo de búsqueda usando la API de Serper.dev
Reemplaza la funcionalidad de Google Custom Search
"""

import os
import aiohttp
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from models.search import SearchResult, SearchDoc
from util.logger import get_logger

logger = get_logger(__name__)

class SerperSearcher:
    """Implementación de búsqueda usando Serper.dev API"""
    
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        self.api_url = os.getenv("SERPER_API_URL", "https://google.serper.dev/search")
        self.max_results = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
        
        if not self.api_key:
            raise ValueError("SERPER_API_KEY no está configurada en las variables de entorno")
    
    async def search(self, query: str) -> SearchResult:
        """
        Realiza una búsqueda usando Serper.dev API
        
        Args:
            query: Consulta de búsqueda
            
        Returns:
            SearchResult con los resultados de la búsqueda
        """
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": self.max_results,
                "gl": "es",  # Geolocalización para España
                "hl": "es"   # Idioma español
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"Error en búsqueda Serper: {response.status}")
                        return self._create_fallback_result(query)
                    
                    data = await response.json()
                    return self._parse_serper_response(data, query)
                    
        except Exception as e:
            logger.error(f"Error en búsqueda Serper: {e}")
            return self._create_fallback_result(query)
    
    def _parse_serper_response(self, data: Dict[str, Any], query: str) -> SearchResult:
        """Parsea la respuesta de Serper.dev a nuestro modelo SearchResult"""
        
        items = []
        
        # Procesar resultados orgánicos
        if "organic" in data:
            for result in data["organic"][:self.max_results]:
                item = SearchDoc(
                    title=result.get("title", ""),
                    link=result.get("link", ""),
                    snippet=result.get("snippet", ""),
                    displayLink=result.get("displayLink", "")
                )
                items.append(item)
        
        # Si no hay resultados orgánicos, usar otros tipos
        if not items and "knowledgeGraph" in data:
            kg = data["knowledgeGraph"]
            item = SearchDoc(
                title=kg.get("title", ""),
                link=kg.get("link", ""),
                snippet=kg.get("description", ""),
                displayLink=kg.get("displayLink", "")
            )
            items.append(item)
        
        # Crear resultado final
        search_info = {
            "searchTime": data.get("searchTime", 0),
            "totalResults": len(items),
            "query": query
        }
        
        return SearchResult(
            items=items,
            searchInformation=search_info
        )
    
    def _create_fallback_result(self, query: str) -> SearchResult:
        """Crea un resultado de fallback cuando hay errores"""
        fallback_item = SearchDoc(
            title="Error en búsqueda",
            link="",
            snippet="No se pudo realizar la búsqueda. Verifica tu conexión a internet.",
            displayLink=""
        )
        
        return SearchResult(
            items=[fallback_item],
            searchInformation={
                "searchTime": 0,
                "totalResults": 1,
                "query": query
            }
        )
