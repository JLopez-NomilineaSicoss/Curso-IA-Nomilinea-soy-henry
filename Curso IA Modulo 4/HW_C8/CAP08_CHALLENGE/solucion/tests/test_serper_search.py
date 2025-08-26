"""
Pruebas unitarias para el módulo de búsqueda de Serper.dev
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import os
import sys

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from retrieval.serper_search import SerperSearcher
from models.search import SearchResult, SearchDoc

class TestSerperSearcher:
    """Pruebas para la clase SerperSearcher"""
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock de variables de entorno"""
        with patch.dict(os.environ, {
            'SERPER_API_KEY': 'test_key',
            'SERPER_API_URL': 'https://test.serper.dev/search',
            'MAX_SEARCH_RESULTS': '5'
        }):
            yield
    
    @pytest.fixture
    def serper_searcher(self, mock_env_vars):
        """Instancia de SerperSearcher para pruebas"""
        return SerperSearcher()
    
    def test_init_with_valid_key(self, mock_env_vars):
        """Prueba inicialización con API key válida"""
        searcher = SerperSearcher()
        assert searcher.api_key == 'test_key'
        assert searcher.api_url == 'https://test.serper.dev/search'
        assert searcher.max_results == 5
    
    def test_init_without_key(self):
        """Prueba inicialización sin API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="SERPER_API_KEY no está configurada"):
                SerperSearcher()
    
    @pytest.mark.asyncio
    async def test_search_success(self, serper_searcher):
        """Prueba búsqueda exitosa"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'organic': [
                {
                    'title': 'Test Title 1',
                    'link': 'https://test1.com',
                    'snippet': 'Test snippet 1',
                    'displayLink': 'test1.com'
                },
                {
                    'title': 'Test Title 2', 
                    'link': 'https://test2.com',
                    'snippet': 'Test snippet 2',
                    'displayLink': 'test2.com'
                }
            ],
            'searchTime': 0.5
        })
        
        mock_session = Mock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = AsyncMock(return_value=mock_response)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await serper_searcher.search('test query')
            
            assert isinstance(result, SearchResult)
            assert len(result.items) == 2
            assert result.items[0].title == 'Test Title 1'
            assert result.items[0].link == 'https://test1.com'
            assert result.searchInformation['totalResults'] == 2
    
    @pytest.mark.asyncio
    async def test_search_error_response(self, serper_searcher):
        """Prueba manejo de error en respuesta HTTP"""
        mock_response = Mock()
        mock_response.status = 500
        
        mock_session = Mock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post = AsyncMock(return_value=mock_response)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await serper_searcher.search('test query')
            
            assert isinstance(result, SearchResult)
            assert len(result.items) == 1
            assert 'Error en búsqueda' in result.items[0].title
    
    @pytest.mark.asyncio
    async def test_search_exception(self, serper_searcher):
        """Prueba manejo de excepciones"""
        mock_session = Mock()
        mock_session.__aenter__ = AsyncMock(side_effect=Exception("Network error"))
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            result = await serper_searcher.search('test query')
            
            assert isinstance(result, SearchResult)
            assert len(result.items) == 1
            assert 'Error en búsqueda' in result.items[0].title
    
    def test_parse_serper_response_organic(self, serper_searcher):
        """Prueba parsing de respuesta con resultados orgánicos"""
        data = {
            'organic': [
                {
                    'title': 'Test Title',
                    'link': 'https://test.com',
                    'snippet': 'Test snippet',
                    'displayLink': 'test.com'
                }
            ],
            'searchTime': 0.3
        }
        
        result = serper_searcher._parse_serper_response(data, 'test query')
        
        assert isinstance(result, SearchResult)
        assert len(result.items) == 1
        assert result.items[0].title == 'Test Title'
        assert result.items[0].link == 'https://test.com'
    
    def test_parse_serper_response_knowledge_graph(self, serper_searcher):
        """Prueba parsing de respuesta con Knowledge Graph"""
        data = {
            'knowledgeGraph': {
                'title': 'KG Title',
                'link': 'https://kg.com',
                'description': 'KG description',
                'displayLink': 'kg.com'
            }
        }
        
        result = serper_searcher._parse_serper_response(data, 'test query')
        
        assert isinstance(result, SearchResult)
        assert len(result.items) == 1
        assert result.items[0].title == 'KG Title'
        assert result.items[0].link == 'https://kg.com'
    
    def test_create_fallback_result(self, serper_searcher):
        """Prueba creación de resultado de fallback"""
        result = serper_searcher._create_fallback_result('test query')
        
        assert isinstance(result, SearchResult)
        assert len(result.items) == 1
        assert 'Error en búsqueda' in result.items[0].title
        assert result.searchInformation['query'] == 'test query'

if __name__ == '__main__':
    pytest.main([__file__])
