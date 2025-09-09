import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings, ConfigDict

class Settings(BaseSettings):
    """Configuraciones del sistema de marketing"""
    
    # Configuración de LLM
    llm_provider: str = "google_ai"  # google_ai, openai, anthropic, groq, local
    
    # APIs principales
    google_api_key: Optional[str] = None
    google_model: str = "gemini-1.5-flash"
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-70b-versatile"
    
    # APIs opcionales
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # Configuración local
    ollama_base_url: str = "http://localhost:11434"
    local_model_fast: str = "llama3.1:8b"  # Cambiado de phi3.5:mini (no disponible)
    local_model_balanced: str = "llama3.1:8b"
    local_model_creative: str = "qwen2.5:14b"
    
    # Configuración de estrategia de modelos
    MODEL_STRATEGY: str = "cloud_first"  # "local_first", "cloud_first", "hybrid"
    prefer_local: bool = False
    fallback_to_local: bool = True
    model_preference: str = "cloud"  # From .env file
    
    # Asignación por agente
    prompt_analyzer_model: str = "gemini"
    post_classifier_model: str = "local_fast"
    brand_voice_model: str = "gemini"
    fact_grounding_model: str = "groq"
    text_generator_model: str = "gemini"
    caption_creator_model: str = "groq"
    visual_concept_model: str = "gemini"
    reasoning_module_model: str = "gemini"
    
    # Configuración del sistema
    max_retries: int = 3
    timeout_seconds: int = 30
    max_tokens: int = 2000
    temperature: float = 0.7
    target_processing_time: float = 10.0
    
    # Cache y performance
    enable_caching: bool = True
    cache_duration_hours: int = 24
    enable_parallel_processing: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "marketing_system.log"
    debug_mode: bool = False
    enable_detailed_logs: bool = True
    
    # Observabilidad
    enable_metrics: bool = True
    enable_tracing: bool = True
    metrics_port: int = 8080
    
    # Output
    output_format: str = "json"
    include_reasoning: bool = True
    include_metadata: bool = True
    enable_validation: bool = True
    
    # Para compatibilidad
    llm_provider: str = "google_ai"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()

def get_settings():
    """Función para obtener la configuración global"""
    class SettingsWrapper:
        def __init__(self, settings):
            self.__dict__.update(settings.__dict__)
            
        def getLogger(self, name):
            import logging
            return logging.getLogger(name)
    
    return SettingsWrapper(settings)

