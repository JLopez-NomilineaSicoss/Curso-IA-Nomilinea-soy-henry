"""
Módulo de preferencias del usuario
Permite configurar cómo y cuándo el chatbot realiza búsquedas
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from util.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SearchPreferences:
    """Preferencias de búsqueda del usuario"""
    max_results: int = 5
    search_engine: str = "serper"  # serper, google, bing
    language: str = "es"  # es, en, fr, etc.
    region: str = "ES"  # ES, US, MX, etc.
    include_images: bool = False
    include_videos: bool = False
    safe_search: bool = True

@dataclass
class LLMPreferences:
    """Preferencias del modelo de lenguaje"""
    provider: str = "groq"  # groq, openai, google
    model: str = "llama3-8b-8192"
    temperature: float = 0.7
    max_tokens: int = 1000
    response_language: str = "es"

@dataclass
class StreamingPreferences:
    """Preferencias de streaming"""
    enabled: bool = True
    chunk_size: int = 100
    show_sources_during_stream: bool = True
    show_progress_bar: bool = True

@dataclass
class UIPreferences:
    """Preferencias de interfaz de usuario"""
    theme: str = "light"  # light, dark, auto
    font_size: str = "medium"  # small, medium, large
    show_timestamps: bool = True
    show_typing_indicator: bool = True
    auto_scroll: bool = True

class UserPreferences:
    """Maneja las preferencias configurables del usuario"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "user_preferences.json"
        
        # Crear directorio si no existe
        self.config_dir.mkdir(exist_ok=True)
        
        # Inicializar preferencias por defecto
        self.search = SearchPreferences()
        self.llm = LLMPreferences()
        self.streaming = StreamingPreferences()
        self.ui = UIPreferences()
        
        # Cargar preferencias existentes
        self.load_preferences()
    
    def load_preferences(self) -> None:
        """Carga las preferencias desde archivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Actualizar preferencias con datos del archivo
                if 'search' in data:
                    self.search = SearchPreferences(**data['search'])
                if 'llm' in data:
                    self.llm = LLMPreferences(**data['llm'])
                if 'streaming' in data:
                    self.streaming = StreamingPreferences(**data['streaming'])
                if 'ui' in data:
                    self.ui = UIPreferences(**data['ui'])
                
                logger.info("Preferencias del usuario cargadas exitosamente")
            else:
                # Crear archivo con preferencias por defecto
                self.save_preferences()
                logger.info("Archivo de preferencias creado con valores por defecto")
                
        except Exception as e:
            logger.error(f"Error cargando preferencias: {e}")
    
    def save_preferences(self) -> None:
        """Guarda las preferencias en archivo"""
        try:
            data = {
                'search': asdict(self.search),
                'llm': asdict(self.llm),
                'streaming': asdict(self.streaming),
                'ui': asdict(self.ui)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info("Preferencias del usuario guardadas exitosamente")
            
        except Exception as e:
            logger.error(f"Error guardando preferencias: {e}")
    
    def update_search_preferences(self, **kwargs) -> None:
        """Actualiza preferencias de búsqueda"""
        for key, value in kwargs.items():
            if hasattr(self.search, key):
                setattr(self.search, key, value)
                logger.info(f"Preferencia de búsqueda actualizada: {key} = {value}")
        
        self.save_preferences()
    
    def update_llm_preferences(self, **kwargs) -> None:
        """Actualiza preferencias del LLM"""
        for key, value in kwargs.items():
            if hasattr(self.llm, key):
                setattr(self.llm, key, value)
                logger.info(f"Preferencia de LLM actualizada: {key} = {value}")
        
        self.save_preferences()
    
    def update_streaming_preferences(self, **kwargs) -> None:
        """Actualiza preferencias de streaming"""
        for key, value in kwargs.items():
            if hasattr(self.streaming, key):
                setattr(self.streaming, key, value)
                logger.info(f"Preferencia de streaming actualizada: {key} = {value}")
        
        self.save_preferences()
    
    def update_ui_preferences(self, **kwargs) -> None:
        """Actualiza preferencias de interfaz"""
        for key, value in kwargs.items():
            if hasattr(self.ui, key):
                setattr(self.ui, key, value)
                logger.info(f"Preferencia de UI actualizada: {key} = {value}")
        
        self.save_preferences()
    
    def reset_to_defaults(self) -> None:
        """Resetea todas las preferencias a valores por defecto"""
        self.search = SearchPreferences()
        self.llm = LLMPreferences()
        self.streaming = StreamingPreferences()
        self.ui = UIPreferences()
        
        self.save_preferences()
        logger.info("Preferencias reseteadas a valores por defecto")
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Obtiene todas las preferencias como diccionario"""
        return {
            'search': asdict(self.search),
            'llm': asdict(self.llm),
            'streaming': asdict(self.streaming),
            'ui': asdict(self.ui)
        }
    
    def validate_preferences(self) -> bool:
        """Valida que las preferencias sean correctas"""
        try:
            # Validar preferencias de búsqueda
            if self.search.max_results < 1 or self.search.max_results > 20:
                logger.warning("max_results debe estar entre 1 y 20")
                return False
            
            # Validar preferencias de LLM
            if self.llm.temperature < 0.0 or self.llm.temperature > 2.0:
                logger.warning("temperature debe estar entre 0.0 y 2.0")
                return False
            
            if self.llm.max_tokens < 100 or self.llm.max_tokens > 4000:
                logger.warning("max_tokens debe estar entre 100 y 4000")
                return False
            
            # Validar preferencias de streaming
            if self.streaming.chunk_size < 10 or self.streaming.chunk_size > 500:
                logger.warning("chunk_size debe estar entre 10 y 500")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando preferencias: {e}")
            return False
    
    def export_preferences(self, filepath: str) -> None:
        """Exporta las preferencias a un archivo"""
        try:
            data = self.get_all_preferences()
            data['metadata'] = {
                'exported_at': str(Path(filepath).stat().st_mtime) if Path(filepath).exists() else 'N/A',
                'version': '1.0'
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Preferencias exportadas a: {filepath}")
            
        except Exception as e:
            logger.error(f"Error exportando preferencias: {e}")
    
    def import_preferences(self, filepath: str) -> bool:
        """Importa preferencias desde un archivo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validar estructura del archivo
            required_sections = ['search', 'llm', 'streaming', 'ui']
            if not all(section in data for section in required_sections):
                logger.error("Archivo de preferencias inválido")
                return False
            
            # Actualizar preferencias
            self.search = SearchPreferences(**data['search'])
            self.llm = LLMPreferences(**data['llm'])
            self.streaming = StreamingPreferences(**data['streaming'])
            self.ui = UIPreferences(**data['ui'])
            
            # Guardar preferencias importadas
            self.save_preferences()
            logger.info(f"Preferencias importadas desde: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error importando preferencias: {e}")
            return False
