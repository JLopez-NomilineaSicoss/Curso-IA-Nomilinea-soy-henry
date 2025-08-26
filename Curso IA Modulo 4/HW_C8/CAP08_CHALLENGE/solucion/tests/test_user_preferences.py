"""
Pruebas unitarias para el módulo de preferencias del usuario
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

# Agregar el directorio src al path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.user_preferences import (
    UserPreferences, 
    SearchPreferences, 
    LLMPreferences, 
    StreamingPreferences, 
    UIPreferences
)

class TestUserPreferences:
    """Pruebas para la clase UserPreferences"""
    
    def test_init_defaults(self):
        """Prueba inicialización con valores por defecto"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Verificar preferencias por defecto
            assert prefs.search.max_results == 5
            assert prefs.search.language == "es"
            assert prefs.search.region == "ES"
            assert prefs.llm.provider == "groq"
            assert prefs.llm.temperature == 0.7
            assert prefs.streaming.enabled is True
            assert prefs.ui.theme == "light"
    
    def test_load_preferences_file_not_exists(self):
        """Prueba carga de preferencias cuando el archivo no existe"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Debe crear el archivo con valores por defecto
            config_file = Path(temp_dir) / "user_preferences.json"
            assert config_file.exists()
            
            # Verificar contenido del archivo
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "search" in data
            assert "llm" in data
            assert "streaming" in data
            assert "ui" in data
    
    def test_load_existing_preferences(self):
        """Prueba carga de preferencias existentes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Crear archivo de preferencias manualmente
            config_file = Path(temp_dir) / "user_preferences.json"
            test_prefs = {
                "search": {
                    "max_results": 10,
                    "language": "en",
                    "region": "US"
                },
                "llm": {
                    "provider": "openai",
                    "temperature": 0.5
                },
                "streaming": {
                    "enabled": False,
                    "chunk_size": 200
                },
                "ui": {
                    "theme": "dark",
                    "font_size": "large"
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(test_prefs, f)
            
            # Cargar preferencias
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Verificar que se cargaron correctamente
            assert prefs.search.max_results == 10
            assert prefs.search.language == "en"
            assert prefs.llm.provider == "openai"
            assert prefs.llm.temperature == 0.5
            assert prefs.streaming.enabled is False
            assert prefs.streaming.chunk_size == 200
            assert prefs.ui.theme == "dark"
            assert prefs.ui.font_size == "large"
    
    def test_update_search_preferences(self):
        """Prueba actualización de preferencias de búsqueda"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Actualizar preferencias
            prefs.update_search_preferences(
                max_results=15,
                language="fr",
                region="FR"
            )
            
            # Verificar cambios
            assert prefs.search.max_results == 15
            assert prefs.search.language == "fr"
            assert prefs.search.region == "FR"
            
            # Verificar que se guardó en archivo
            config_file = Path(temp_dir) / "user_preferences.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert data["search"]["max_results"] == 15
            assert data["search"]["language"] == "fr"
    
    def test_update_llm_preferences(self):
        """Prueba actualización de preferencias del LLM"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Actualizar preferencias
            prefs.update_llm_preferences(
                provider="google",
                model="gemini-pro",
                temperature=1.0,
                max_tokens=2000
            )
            
            # Verificar cambios
            assert prefs.llm.provider == "google"
            assert prefs.llm.model == "gemini-pro"
            assert prefs.llm.temperature == 1.0
            assert prefs.llm.max_tokens == 2000
    
    def test_update_streaming_preferences(self):
        """Prueba actualización de preferencias de streaming"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Actualizar preferencias
            prefs.update_streaming_preferences(
                enabled=False,
                chunk_size=150,
                show_progress_bar=False
            )
            
            # Verificar cambios
            assert prefs.streaming.enabled is False
            assert prefs.streaming.chunk_size == 150
            assert prefs.streaming.show_progress_bar is False
    
    def test_update_ui_preferences(self):
        """Prueba actualización de preferencias de UI"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Actualizar preferencias
            prefs.update_ui_preferences(
                theme="dark",
                font_size="small",
                show_timestamps=False
            )
            
            # Verificar cambios
            assert prefs.ui.theme == "dark"
            assert prefs.ui.font_size == "small"
            assert prefs.ui.show_timestamps is False
    
    def test_reset_to_defaults(self):
        """Prueba reseteo de preferencias a valores por defecto"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Cambiar algunas preferencias
            prefs.search.max_results = 20
            prefs.llm.temperature = 1.5
            prefs.ui.theme = "dark"
            
            # Resetear a valores por defecto
            prefs.reset_to_defaults()
            
            # Verificar que se resetearon
            assert prefs.search.max_results == 5
            assert prefs.llm.temperature == 0.7
            assert prefs.ui.theme == "light"
    
    def test_get_all_preferences(self):
        """Prueba obtención de todas las preferencias"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            all_prefs = prefs.get_all_preferences()
            
            # Verificar estructura
            assert "search" in all_prefs
            assert "llm" in all_prefs
            assert "streaming" in all_prefs
            assert "ui" in all_prefs
            
            # Verificar contenido
            assert all_prefs["search"]["max_results"] == 5
            assert all_prefs["llm"]["provider"] == "groq"
            assert all_prefs["streaming"]["enabled"] is True
            assert all_prefs["ui"]["theme"] == "light"
    
    def test_validate_preferences_valid(self):
        """Prueba validación de preferencias válidas"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Preferencias válidas
            assert prefs.validate_preferences() is True
    
    def test_validate_preferences_invalid(self):
        """Prueba validación de preferencias inválidas"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Hacer preferencias inválidas
            prefs.search.max_results = 25  # Debe estar entre 1 y 20
            prefs.llm.temperature = 3.0    # Debe estar entre 0.0 y 2.0
            prefs.streaming.chunk_size = 600  # Debe estar entre 10 y 500
            
            # Validar
            assert prefs.validate_preferences() is False
    
    def test_export_preferences(self):
        """Prueba exportación de preferencias"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Archivo de exportación
            export_file = Path(temp_dir) / "exported_prefs.json"
            
            # Exportar preferencias
            prefs.export_preferences(str(export_file))
            
            # Verificar que se creó el archivo
            assert export_file.exists()
            
            # Verificar contenido
            with open(export_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "search" in data
            assert "llm" in data
            assert "streaming" in data
            assert "ui" in data
            assert "metadata" in data
    
    def test_import_preferences(self):
        """Prueba importación de preferencias"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Archivo de importación
            import_file = Path(temp_dir) / "import_prefs.json"
            import_data = {
                "search": {
                    "max_results": 12,
                    "language": "de",
                    "region": "DE"
                },
                "llm": {
                    "provider": "anthropic",
                    "model": "claude-3",
                    "temperature": 0.3
                },
                "streaming": {
                    "enabled": True,
                    "chunk_size": 75
                },
                "ui": {
                    "theme": "auto",
                    "font_size": "medium"
                }
            }
            
            # Crear archivo de importación
            with open(import_file, 'w', encoding='utf-8') as f:
                json.dump(import_data, f)
            
            # Importar preferencias
            success = prefs.import_preferences(str(import_file))
            
            # Verificar éxito
            assert success is True
            
            # Verificar que se importaron correctamente
            assert prefs.search.max_results == 12
            assert prefs.search.language == "de"
            assert prefs.llm.provider == "anthropic"
            assert prefs.llm.temperature == 0.3
            assert prefs.streaming.chunk_size == 75
            assert prefs.ui.theme == "auto"
    
    def test_import_preferences_invalid_file(self):
        """Prueba importación de archivo de preferencias inválido"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prefs = UserPreferences(config_dir=temp_dir)
            
            # Archivo inválido (falta sección)
            import_file = Path(temp_dir) / "invalid_prefs.json"
            invalid_data = {
                "search": {"max_results": 5},
                "llm": {"provider": "groq"}
                # Falta "streaming" y "ui"
            }
            
            # Crear archivo inválido
            with open(import_file, 'w', encoding='utf-8') as f:
                json.dump(invalid_data, f)
            
            # Intentar importar
            success = prefs.import_preferences(str(import_file))
            
            # Debe fallar
            assert success is False

if __name__ == '__main__':
    pytest.main([__file__])
