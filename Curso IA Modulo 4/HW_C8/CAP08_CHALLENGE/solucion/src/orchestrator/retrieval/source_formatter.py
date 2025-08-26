"""
Módulo para extraer y formatear fuentes de información
"""

from typing import List, Dict, Any, Optional
from models.search import SearchResult, SearchDoc
from util.logger import get_logger

logger = get_logger(__name__)

class SourceFormatter:
    """Formatea y extrae fuentes de información de los resultados de búsqueda"""
    
    @staticmethod
    def extract_sources_from_search(search_result: SearchResult) -> List[Dict[str, str]]:
        """
        Extrae las fuentes de un resultado de búsqueda
        
        Args:
            search_result: Resultado de búsqueda de Serper.dev
            
        Returns:
            Lista de fuentes con título y URL
        """
        sources = []
        
        if not search_result or not search_result.items:
            return sources
        
        for item in search_result.items:
            if item.link and item.title:
                source = {
                    "title": item.title,
                    "url": item.link,
                    "domain": item.displayLink or item.link.split('/')[2] if item.link.startswith('http') else item.link
                }
                sources.append(source)
        
        logger.info(f"Fuentes extraídas: {len(sources)}")
        return sources
    
    @staticmethod
    def format_sources_for_display(sources: List[Dict[str, str]]) -> str:
        """
        Formatea las fuentes para mostrar al usuario
        
        Args:
            sources: Lista de fuentes extraídas
            
        Returns:
            String formateado con las fuentes
        """
        if not sources:
            return ""
        
        formatted_sources = "\n\n**Referencias:**\n"
        
        for i, source in enumerate(sources, 1):
            title = source.get("title", "Sin título")
            url = source.get("url", "")
            domain = source.get("domain", "")
            
            formatted_sources += f"{i}. [{title}]({url})"
            if domain:
                formatted_sources += f" - {domain}"
            formatted_sources += "\n"
        
        return formatted_sources
    
    @staticmethod
    def format_sources_for_prompt(sources: List[Dict[str, str]]) -> str:
        """
        Formatea las fuentes para incluir en el prompt del LLM
        
        Args:
            sources: Lista de fuentes extraídas
            
        Returns:
            String formateado para el prompt
        """
        if not sources:
            return ""
        
        formatted_sources = "\nFuentes disponibles:\n"
        
        for i, source in enumerate(sources, 1):
            title = source.get("title", "Sin título")
            url = source.get("url", "")
            
            formatted_sources += f"{i}. {title} - {url}\n"
        
        return formatted_sources
    
    @staticmethod
    def validate_source_url(url: str) -> bool:
        """
        Valida que una URL sea válida
        
        Args:
            url: URL a validar
            
        Returns:
            True si la URL es válida
        """
        if not url:
            return False
        
        # Validación básica de URL
        return url.startswith(('http://', 'https://')) and len(url) > 10
    
    @staticmethod
    def clean_source_title(title: str) -> str:
        """
        Limpia el título de una fuente
        
        Args:
            title: Título a limpiar
            
        Returns:
            Título limpio
        """
        if not title:
            return "Sin título"
        
        # Remover caracteres especiales y limitar longitud
        cleaned = title.strip()
        cleaned = cleaned.replace('\n', ' ').replace('\r', ' ')
        
        # Limitar a 100 caracteres
        if len(cleaned) > 100:
            cleaned = cleaned[:97] + "..."
        
        return cleaned
