import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class CloudSettings(BaseSettings):
    """Configuraciones optimizadas para deployment en la nube - Solo modelos cloud"""
    
    # APIs principales (requeridas)
    google_api_key: Optional[str] = None
    google_model: str = "gemini-1.5-flash"
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-70b-versatile"
    
    # APIs opcionales
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # Configuración cloud-only (sin Ollama)
    MODEL_STRATEGY: str = "cloud_only"
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
    max_retries: int = 2
    timeout_seconds: int = 20
    max_tokens: int = 1500
    temperature: float = 0.7
    target_processing_time: float = 8.0
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instancia global de configuración cloud
cloud_settings = CloudSettings()

def get_cloud_settings():
    """Función para obtener la configuración cloud"""
    return cloud_settings
