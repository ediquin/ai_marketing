from typing import List, Optional, Dict, Any, ClassVar
from datetime import datetime
from enum import Enum
from pydantic import Field, ConfigDict
from pydantic import BaseModel as PydanticBaseModel

class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(extra='ignore', use_enum_values=True)

class PostType(str, Enum):
    LAUNCH = "Launch"
    EDUCATIONAL = "Educational"
    PROMOTIONAL = "Promotional"
    STORYTELLING = "Storytelling"
    ENGAGEMENT = "Engagement"

class BrandVoice(BaseModel):
    tone: str = Field(description="Tono general de la marca")
    personality: str = Field(description="Personalidad de la marca")
    style: str = Field(description="Estilo de comunicación")
    values: List[str] = Field(description="Valores clave de la marca")
    language_level: str = Field(description="Nivel de lenguaje (formal, casual, técnico)")

class EngagementElements(BaseModel):
    caption: str = Field(description="Caption principal del post")
    call_to_action: str = Field(description="Llamada a la acción")
    hashtags: List[str] = Field(description="Hashtags relevantes")
    engagement_hooks: List[str] = Field(description="Ganchos de engagement")
    questions: Optional[List[str]] = Field(description="Preguntas para generar interacción")

class VisualConcept(BaseModel):
    mood: str = Field(description="Estado de ánimo visual")
    color_palette: List[str] = Field(description="Paleta de colores")
    imagery_type: str = Field(description="Tipo de imágenes a usar")
    layout_style: str = Field(description="Estilo de layout")
    visual_elements: List[str] = Field(description="Elementos visuales específicos")
    design_notes: str = Field(description="Notas adicionales para el diseñador")

class FactualGrounding(BaseModel):
    key_facts: List[str] = Field(description="Hechos clave verificados")
    data_sources: List[str] = Field(default=[], description="Fuentes de datos")
    statistics: Optional[List[str]] = Field(default=[], description="Estadísticas relevantes")
    verification_status: str = Field(default="needs_verification", description="Estado de verificación")
    
    @classmethod
    def from_llm_response(cls, data: Dict[str, Any]) -> 'FactualGrounding':
        """Crea una instancia desde la respuesta del LLM, manejando diferentes formatos"""
        # Extraer key_facts
        key_facts = []
        if 'key_facts' in data:
            facts_data = data['key_facts']
            if isinstance(facts_data, list):
                for fact in facts_data:
                    if isinstance(fact, str):
                        key_facts.append(fact)
                    elif isinstance(fact, dict) and 'fact' in fact:
                        key_facts.append(fact['fact'])
                    else:
                        key_facts.append(str(fact))
        
        # Extraer otros campos con valores por defecto
        data_sources = data.get('data_sources', [])
        statistics = data.get('statistics', [])
        verification_status = data.get('verification_status', 'needs_verification')
        
        return cls(
            key_facts=key_facts,
            data_sources=data_sources,
            statistics=statistics,
            verification_status=verification_status
        )

class ReasoningModule(BaseModel):
    strategic_decisions: List[str] = Field(description="Decisiones estratégicas tomadas")
    audience_considerations: str = Field(description="Consideraciones sobre la audiencia")
    platform_optimization: str = Field(description="Optimización para la plataforma")
    competitive_analysis: Optional[str] = Field(description="Análisis competitivo")
    risk_assessment: str = Field(description="Evaluación de riesgos")

class ProcessingMetadata(BaseModel):
    processing_time: float = Field(description="Tiempo total de procesamiento en segundos")
    agent_timings: Dict[str, float] = Field(description="Tiempos de cada agente")
    model_used: str = Field(description="Modelo LLM utilizado")
    timestamp: datetime = Field(description="Timestamp de procesamiento")
    version: str = Field(description="Versión del sistema")

class ContentBrief(BaseModel):
    post_type: PostType = Field(description="Tipo de post identificado")
    core_content: str = Field(description="Contenido principal del post")
    engagement_elements: EngagementElements = Field(description="Elementos de engagement")
    visual_concept: VisualConcept = Field(description="Concepto visual")
    brand_voice: BrandVoice = Field(description="Voz de marca")
    factual_grounding: FactualGrounding = Field(description="Base factual")
    reasoning: ReasoningModule = Field(description="Módulo de razonamiento")
    metadata: ProcessingMetadata = Field(description="Metadatos de procesamiento")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

class PromptAnalysis(BaseModel):
    objective: str = Field(description="Objetivo del prompt")
    audience: str = Field(description="Audiencia objetivo")
    brand_cues: List[str] = Field(description="Indicadores de marca")
    key_facts: List[str] = Field(description="Hechos clave mencionados")
    urgency: Optional[str] = Field(description="Elementos de urgencia temporal")
    platform: Optional[str] = Field(description="Plataforma específica mencionada")
    tone_indicators: List[str] = Field(description="Indicadores de tono")
    content_goals: List[str] = Field(description="Metas de contenido")

class MarketingState(BaseModel):
    """Estado del workflow de marketing"""
    
    input_prompt: str = Field(description="Prompt de entrada del usuario")
    prompt_analysis: Optional[PromptAnalysis] = Field(description="Análisis del prompt")
    post_type: Optional[PostType] = Field(description="Tipo de post clasificado")
    brand_voice: Optional[BrandVoice] = Field(description="Voz de marca definida")
    factual_grounding: Optional[FactualGrounding] = Field(description="Base factual")
    core_content: Optional[str] = Field(description="Contenido principal generado")
    engagement_elements: Optional[EngagementElements] = Field(description="Elementos de engagement")
    visual_concept: Optional[VisualConcept] = Field(description="Concepto visual")
    reasoning: Optional[ReasoningModule] = Field(description="Razonamiento estratégico")
    final_brief: Optional[ContentBrief] = Field(description="Brief final completo")
    errors: List[str] = Field(default_factory=list, description="Errores durante el procesamiento")
    warnings: List[str] = Field(default_factory=list, description="Advertencias del sistema")
    processing_start: Optional[datetime] = Field(description="Inicio del procesamiento")
    processing_end: Optional[datetime] = Field(description="Fin del procesamiento")
    
    class Config:
        model_config = ConfigDict(
            json_encoders={
                datetime: lambda v: v.isoformat()
            }
        )
