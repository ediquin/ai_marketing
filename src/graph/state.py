"""
Estado del workflow de marketing para LangGraph
"""
from typing import Dict, Any, List, Optional, ClassVar
from datetime import datetime
from pydantic import Field, ConfigDict
from pydantic import BaseModel as PydanticBaseModel

from src.models.content_brief import (
    MarketingState, PromptAnalysis, PostType, BrandVoice, 
    FactualGrounding, ContentBrief, EngagementElements, 
    VisualConcept, ReasoningModule, ProcessingMetadata
)

class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(extra='ignore', use_enum_values=True)

class WorkflowState(BaseModel):
    """
    Estado del workflow de LangGraph
    Compatible con el sistema de tipos de LangGraph
    """
    
    # Input del usuario
    input_prompt: str = Field(description="Prompt de entrada del usuario")
    
    # Análisis del prompt
    prompt_analysis: Optional[PromptAnalysis] = Field(default=None, description="Análisis del prompt")
    
    # Clasificación de contenido
    post_type: Optional[PostType] = Field(default=None, description="Tipo de post clasificado")
    post_justification: Optional[str] = Field(default=None, description="Justificación de la clasificación")
    
    # Voz de marca
    brand_voice: Optional[BrandVoice] = Field(default=None, description="Voz de marca")
    
    # Base factual
    factual_grounding: Optional[FactualGrounding] = Field(default=None, description="Base factual")
    
    # Contenido generado
    core_content: Optional[str] = Field(default=None, description="Contenido principal generado")
    
    # Elementos de engagement
    engagement_elements: Optional[EngagementElements] = Field(default=None, description="Elementos de engagement")
    
    # Concepto visual
    visual_concept: Optional[VisualConcept] = Field(default=None, description="Concepto visual")
    
    # Razonamiento estratégico
    reasoning: Optional[ReasoningModule] = Field(default=None, description="Razonamiento estratégico")
    
    # Características opcionales (+5 puntos cada una)
    visual_format_recommendation: Optional[Dict[str, Any]] = Field(default=None, description="Recomendación de formato visual")
    video_script: Optional[Dict[str, Any]] = Field(default=None, description="Script de video estructurado")
    result_optimizations: Optional[Dict[str, Any]] = Field(default=None, description="Optimizaciones basadas en resultados")
    contextual_awareness: Optional[Dict[str, Any]] = Field(default=None, description="Conciencia contextual en tiempo real")
    
    # Brief final
    final_brief: Optional[ContentBrief] = Field(default=None, description="Brief final completo")
    
    # Configuración de idioma
    language_config: Optional[Dict[str, str]] = Field(default=None, description="Configuración de idioma para respuestas")
    
    # Metadatos del sistema
    errors: List[str] = Field(default_factory=list, description="Errores durante el procesamiento")
    warnings: List[str] = Field(default_factory=list, description="Advertencias del sistema")
    processing_start: Optional[datetime] = Field(default=None, description="Inicio del procesamiento")
    processing_end: Optional[datetime] = Field(default=None, description="Fin del procesamiento")
    is_complete: bool = Field(default=False, description="Indica si el workflow está completo")
    is_error: bool = Field(default=False, description="Indica si hubo errores críticos")
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    # Tiempos por agente
    agent_timings: Dict[str, float] = Field(default_factory=dict, description="Tiempos de procesamiento por agente")
    
    # Control del workflow
    current_step: str = Field(default="initialize", description="Paso actual del workflow")
    completed_steps: List[str] = Field(default_factory=list, description="Pasos completados")
    
    # Manejo de errores
    errors: List[str] = Field(default_factory=list, description="Lista de errores")
    warnings: List[str] = Field(default_factory=list, description="Lista de advertencias")
    
    # Estado del workflow
    is_complete: bool = Field(default=False, description="Indica si el workflow está completo")
    is_error: bool = Field(default=False, description="Indica si hubo errores críticos")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

def create_initial_state(input_prompt: str) -> WorkflowState:
    """Crea el estado inicial del workflow"""
    # Detectar idioma del prompt
    language = "en" if _is_english_prompt(input_prompt) else "es"
    
    return WorkflowState(
        input_prompt=input_prompt,
        processing_start=datetime.now(),
        current_step="initialize",
        language_config={"language": language}
    )

def _is_english_prompt(prompt: str) -> bool:
    """Detecta si un prompt está en inglés basado en palabras clave"""
    # Palabras claramente en español
    spanish_keywords = [
        "crear", "generar", "escribir", "hacer", "desarrollar", "construir", "diseñar",
        "campaña", "contenido", "redes", "sociales", "marca", "producto", "servicio",
        "empresa", "negocio", "cliente", "audiencia", "estrategia", "promoción",
        "publicidad", "para", "con", "una", "del", "las", "los", "que", "como"
    ]
    
    # Palabras claramente en inglés
    english_keywords = [
        "create", "generate", "write", "make", "develop", "build", "design",
        "marketing", "campaign", "post", "content", "social", "media",
        "brand", "product", "service", "company", "business", "customer",
        "audience", "engagement", "strategy", "promotion", "advertisement",
        "for", "with", "the", "and", "our", "new", "launch", "targeting"
    ]
    
    prompt_lower = prompt.lower()
    
    # Contar palabras en español e inglés
    spanish_count = sum(1 for word in spanish_keywords if word in prompt_lower)
    english_count = sum(1 for word in english_keywords if word in prompt_lower)
    
    # Si hay más palabras en español, es español
    if spanish_count > english_count:
        return False
    
    # Si hay más palabras en inglés, es inglés
    if english_count > spanish_count:
        return True
    
    # Si hay empate o no hay palabras claras, usar inglés como default
    return english_count >= 2

def update_state_with_analysis(state: WorkflowState, analysis: PromptAnalysis) -> WorkflowState:
    """Actualiza el estado con el análisis del prompt"""
    state.prompt_analysis = analysis
    state.completed_steps.append("prompt_analysis")
    state.current_step = "post_classification"
    return state

def update_state_with_classification(state: WorkflowState, post_type: PostType, justification: str) -> WorkflowState:
    """Actualiza el estado con la clasificación del post"""
    state.post_type = post_type
    state.post_justification = justification
    state.completed_steps.append("post_classification")
    state.current_step = "brand_voice"
    return state

def update_state_with_brand_voice(state: WorkflowState, brand_voice: BrandVoice) -> WorkflowState:
    """Actualiza el estado con la voz de marca"""
    state.brand_voice = brand_voice
    state.completed_steps.append("brand_voice")
    state.current_step = "fact_grounding"
    return state

def update_state_with_facts(state: WorkflowState, factual_grounding: FactualGrounding) -> WorkflowState:
    """Actualiza el estado con la base factual"""
    state.factual_grounding = factual_grounding
    state.completed_steps.append("fact_grounding")
    state.current_step = "text_generation"
    return state

def update_state_with_content(state: WorkflowState, core_content: str) -> WorkflowState:
    """Actualiza el estado con el contenido principal"""
    state.core_content = core_content
    state.completed_steps.append("text_generation")
    state.current_step = "caption_creation"
    return state

def update_state_with_engagement(state: WorkflowState, engagement_elements: EngagementElements) -> WorkflowState:
    """Actualiza el estado con los elementos de engagement"""
    state.engagement_elements = engagement_elements
    state.completed_steps.append("caption_creation")
    state.current_step = "visual_concept"
    return state

def update_state_with_visual(state: WorkflowState, visual_concept: VisualConcept) -> WorkflowState:
    """Actualiza el estado con el concepto visual"""
    state.visual_concept = visual_concept
    state.completed_steps.append("visual_concept")
    state.current_step = "reasoning"
    return state

def update_state_with_reasoning(state: WorkflowState, reasoning: ReasoningModule) -> WorkflowState:
    """Actualiza el estado con el razonamiento estratégico"""
    state.reasoning = reasoning
    state.completed_steps.append("reasoning")
    state.current_step = "visual_format_recommendation"
    return state

def update_state_with_visual_format(state: WorkflowState, visual_format: Dict[str, Any]) -> WorkflowState:
    """Actualiza el estado con la recomendación de formato visual"""
    state.visual_format_recommendation = visual_format
    state.completed_steps.append("visual_format_recommendation")
    state.current_step = "video_script"
    return state

def update_state_with_video_script(state: WorkflowState, video_script: Dict[str, Any]) -> WorkflowState:
    """Actualiza el estado con el script de video"""
    state.video_script = video_script
    state.completed_steps.append("video_script")
    state.current_step = "result_optimization"
    return state

def update_state_with_optimization(state: WorkflowState, optimizations: Dict[str, Any]) -> WorkflowState:
    """Actualiza el estado con las optimizaciones basadas en resultados"""
    state.result_optimizations = optimizations
    state.completed_steps.append("result_optimization")
    state.current_step = "contextual_awareness"
    return state

def update_state_with_context(state: WorkflowState, context: Dict[str, Any]) -> WorkflowState:
    """Actualiza el estado con la conciencia contextual"""
    state.contextual_awareness = context
    state.completed_steps.append("contextual_awareness")
    state.current_step = "final_assembly"
    return state

def finalize_state(state: WorkflowState) -> WorkflowState:
    """Finaliza el estado del workflow"""
    state.processing_end = datetime.now()
    state.is_complete = True
    state.current_step = "complete"
    
    # Crear el brief final
    if all([
        state.post_type, state.core_content, state.engagement_elements,
        state.visual_concept, state.brand_voice, state.factual_grounding, state.reasoning
    ]):
        # Calcular tiempo total
        if state.processing_start and state.processing_end:
            total_time = (state.processing_end - state.processing_start).total_seconds()
        else:
            total_time = 0.0
        
        # Crear metadatos
        metadata = ProcessingMetadata(
            processing_time=total_time,
            agent_timings=state.agent_timings,
            model_used="llm_client",  # Se actualizará con el modelo real
            timestamp=state.processing_end,
            version="1.0.0"
        )
        
        # Crear brief final solo si tenemos todos los componentes necesarios
        try:
            if (state.post_type and state.core_content and 
                state.engagement_elements and state.visual_concept and 
                state.brand_voice and state.factual_grounding and state.reasoning):
                
                state.final_brief = ContentBrief(
                    post_type=state.post_type,
                    core_content=state.core_content,
                    engagement_elements=state.engagement_elements,
                    visual_concept=state.visual_concept,
                    brand_voice=state.brand_voice,
                    factual_grounding=state.factual_grounding,
                    reasoning=state.reasoning,
                    metadata=metadata
                )
            else:
                # Log qué componentes faltan
                missing = []
                if not state.post_type: missing.append("post_type")
                if not state.core_content: missing.append("core_content")
                if not state.engagement_elements: missing.append("engagement_elements")
                if not state.visual_concept: missing.append("visual_concept")
                if not state.brand_voice: missing.append("brand_voice")
                if not state.factual_grounding: missing.append("factual_grounding")
                if not state.reasoning: missing.append("reasoning")
                
                error_msg = f"No se puede crear brief final. Componentes faltantes: {', '.join(missing)}"
                state.errors.append(error_msg)
                state.final_brief = None
                
        except Exception as e:
            error_msg = f"Error creando brief final: {str(e)}"
            state.errors.append(error_msg)
            state.final_brief = None
    
    return state

def add_error_to_state(state: WorkflowState, error: str, step: str) -> WorkflowState:
    """Añade un error al estado"""
    state.errors.append(f"[{step}]: {error}")
    state.is_error = True
    state.current_step = "error"
    return state

def add_warning_to_state(state: WorkflowState, warning: str, step: str) -> WorkflowState:
    """Añade una advertencia al estado"""
    state.warnings.append(f"[{step}]: {warning}")
    return state

def record_agent_timing(state: WorkflowState, agent_name: str, timing: float) -> WorkflowState:
    """Registra el tiempo de un agente"""
    state.agent_timings[agent_name] = timing
    return state

