import os
from typing import Optional, ClassVar
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class CloudSettings(BaseSettings):
    """Configuraciones optimizadas para deployment en la nube - Solo modelos cloud"""
    
    model_config = SettingsConfigDict(
        extra='ignore',  # Ignorar variables de entorno adicionales
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )
        
    # APIs principales (requeridas)
    google_api_key: Optional[str] = None
    google_model: str = "gemini-1.5-flash"
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-70b-versatile"
    
    # Configuración de modelos locales (ignorados en modo cloud)
    ollama_base_url: Optional[str] = None
    local_model_fast: Optional[str] = None
    local_model_balanced: Optional[str] = None
    local_model_creative: Optional[str] = None
    fallback_to_cloud: bool = False
    log_file: str = "marketing_system.log"
    metrics_port: int = 8080
    
    # APIs opcionales
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # Configuración cloud-only (sin Ollama)
    model_strategy: ClassVar[str] = "cloud_only"
    prefer_local: bool = False
    fallback_to_local: bool = False
    model_preference: str = "cloud"
    
    # Asignación por agente - Solo cloud
    prompt_analyzer_model: str = "gemini"
    post_classifier_model: str = "groq"
    brand_voice_model: str = "gemini"
    fact_grounding_model: str = "groq"
    text_generator_model: str = "gemini"
    caption_creator_model: str = "groq"
    visual_concept_model: str = "gemini"
    reasoning_module_model: str = "gemini"
    visual_format_recommender_model: str = "groq"
    video_scripter_model: str = "gemini"
    result_optimizer_model: str = "groq"
    contextual_awareness_model: str = "gemini"
    
    # Configuración del sistema optimizada para cloud
    max_retries: int = Field(default=2, description="Número máximo de reintentos")
    timeout_seconds: int = Field(default=20, description="Tiempo máximo de espera en segundos")
    max_tokens: int = Field(default=1500, description="Número máximo de tokens")
    temperature: float = Field(default=0.7, description="Temperatura para la generación")
    target_processing_time: float = Field(default=8.0, description="Tiempo objetivo de procesamiento")
    
    # Cache y performance
    enable_caching: bool = True
    cache_duration_hours: int = 12
    enable_parallel_processing: bool = False  # Evitar rate limits
    
    # Logging optimizado para producción
    log_level: str = "WARNING"
    debug_mode: bool = False
    enable_detailed_logs: bool = False
    
    # Observabilidad
    enable_metrics: bool = True
    enable_tracing: bool = False
    
    # Output
    output_format: str = "json"
    include_reasoning: bool = True
    include_metadata: bool = True
    enable_validation: bool = True
    
    # Cloud deployment specific
    port: int = int(os.getenv("PORT", 8501))
    host: str = "0.0.0.0"
    
    # RAG System (cloud optimized)
    enable_rag: bool = True
    use_realtime_data: bool = False  # Disable to avoid external API calls

# Instancia global de configuración cloud
cloud_settings = CloudSettings()

def get_cloud_settings():
    """Función para obtener la configuración cloud"""
    return cloud_settings
