"""
Pruebas unitarias para el módulo de formateo de fuentes
"""

import pytest
from unittest.mock import Mock

# Agregar el directorio src al path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from retrieval.source_formatter import SourceFormatter
from models.search import SearchResult, SearchDoc

class TestSourceFormatter:
    """Pruebas para la clase SourceFormatter"""
    
    def test_extract_sources_from_search(self):
        """Prueba extracción de fuentes de resultados de búsqueda"""
        # Crear mock de SearchResult
        mock_items = [
            Mock(
                title="Python Tutorial",
                link="https://python.org/tutorial",
                displayLink="python.org"
            ),
            Mock(
                title="Learn Python",
                link="https://learnpython.com",
                displayLink="learnpython.com"
            )
        ]
        
        mock_search_result = Mock()
        mock_search_result.items = mock_items
        
        sources = SourceFormatter.extract_sources_from_search(mock_search_result)
        
        assert len(sources) == 2
        assert sources[0]["title"] == "Python Tutorial"
        assert sources[0]["url"] == "https://python.org/tutorial"
        assert sources[0]["domain"] == "python.org"
        assert sources[1]["title"] == "Learn Python"
        assert sources[1]["url"] == "https://learnpython.com"
    
    def test_extract_sources_empty_result(self):
        """Prueba extracción de fuentes con resultado vacío"""
        mock_search_result = Mock()
        mock_search_result.items = []
        
        sources = SourceFormatter.extract_sources_from_search(mock_search_result)
        
        assert len(sources) == 0
    
    def test_extract_sources_none_result(self):
        """Prueba extracción de fuentes con resultado None"""
        sources = SourceFormatter.extract_sources_from_search(None)
        
        assert len(sources) == 0
    
    def test_format_sources_for_display(self):
        """Prueba formateo de fuentes para mostrar al usuario"""
        sources = [
            {
                "title": "Python Tutorial",
                "url": "https://python.org/tutorial",
                "domain": "python.org"
            },
            {
                "title": "Learn Python",
                "url": "https://learnpython.com",
                "domain": "learnpython.com"
            }
        ]
        
        formatted = SourceFormatter.format_sources_for_display(sources)
        
        assert "**Referencias:**" in formatted
        assert "[Python Tutorial](https://python.org/tutorial)" in formatted
        assert "[Learn Python](https://learnpython.com)" in formatted
        assert "python.org" in formatted
        assert "learnpython.com" in formatted
    
    def test_format_sources_for_display_empty(self):
        """Prueba formateo de fuentes vacías"""
        formatted = SourceFormatter.format_sources_for_display([])
        
        assert formatted == ""
    
    def test_format_sources_for_prompt(self):
        """Prueba formateo de fuentes para prompt del LLM"""
        sources = [
            {
                "title": "Python Tutorial",
                "url": "https://python.org/tutorial",
                "domain": "python.org"
            }
        ]
        
        formatted = SourceFormatter.format_sources_for_prompt(sources)
        
        assert "Fuentes disponibles:" in formatted
        assert "Python Tutorial - https://python.org/tutorial" in formatted
    
    def test_format_sources_for_prompt_empty(self):
        """Prueba formateo de fuentes vacías para prompt"""
        formatted = SourceFormatter.format_sources_for_prompt([])
        
        assert formatted == ""
    
    def test_validate_source_url_valid(self):
        """Prueba validación de URLs válidas"""
        valid_urls = [
            "https://example.com",
            "http://test.org/path",
            "https://sub.domain.co.uk/page"
        ]
        
        for url in valid_urls:
            assert SourceFormatter.validate_source_url(url) is True
    
    def test_validate_source_url_invalid(self):
        """Prueba validación de URLs inválidas"""
        invalid_urls = [
            "",
            "not-a-url",
            "ftp://example.com",
            "https://",
            "http://short"
        ]
        
        for url in invalid_urls:
            assert SourceFormatter.validate_source_url(url) is False
    
    def test_clean_source_title_normal(self):
        """Prueba limpieza de títulos normales"""
        title = "Python Tutorial - Learn Python Programming"
        cleaned = SourceFormatter.clean_source_title(title)
        
        assert cleaned == "Python Tutorial - Learn Python Programming"
    
    def test_clean_source_title_with_newlines(self):
        """Prueba limpieza de títulos con saltos de línea"""
        title = "Python\nTutorial\r\nLearn Python"
        cleaned = SourceFormatter.clean_source_title(title)
        
        assert cleaned == "Python Tutorial Learn Python"
    
    def test_clean_source_title_long(self):
        """Prueba limpieza de títulos largos"""
        long_title = "A" * 150
        cleaned = SourceFormatter.clean_source_title(long_title)
        
        assert len(cleaned) == 100
        assert cleaned.endswith("...")
    
    def test_clean_source_title_empty(self):
        """Prueba limpieza de títulos vacíos"""
        cleaned = SourceFormatter.clean_source_title("")
        
        assert cleaned == "Sin título"
    
    def test_clean_source_title_none(self):
        """Prueba limpieza de títulos None"""
        cleaned = SourceFormatter.clean_source_title(None)
        
        assert cleaned == "Sin título"

if __name__ == '__main__':
    pytest.main([__file__])
