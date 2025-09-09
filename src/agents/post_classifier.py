"""
Agente Post Classifier - Identifica el tipo de post más efectivo
"""
import logging
import time
from typing import Dict, Any

from src.models.content_brief import PostType
from src.tools.llm_client import LLMClient
from src.config.prompts import get_prompt_template, AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class PostClassifier:
    """
    Agente que clasifica el tipo de post más efectivo basándose en el análisis del prompt
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado y clasifica el tipo de post
        
        Args:
            state: Estado del workflow
            
        Returns:
            Estado actualizado con la clasificación del post
        """
        start_time = time.time()
        
        try:
            self.logger.info("Iniciando clasificación del post")
            
            # Verificar que tenemos el análisis del prompt
            if not state.get("prompt_analysis"):
                raise ValueError("No hay análisis del prompt disponible")
            
            # 1. Preparar prompt específico según idioma
            language_config = state.get("language_config", {})
            language = language_config.get("language", "es")
            
            analysis_summary = self._create_analysis_summary(state["prompt_analysis"])
            template = get_prompt_template(AGENT_TEMPLATES["post_classifier"], language)
            prompt = template.format(analysis=analysis_summary)
            
            # 2. Llamar al LLM
            self.logger.info("Generando clasificación con LLM")
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con tipo de post y justificación"
            )
            
            # 3. Parsear respuesta
            self.logger.info("Parseando clasificación del LLM")
            post_type_str = response.get("post_type")
            justification = response.get("justification", "")
            
            if not post_type_str:
                raise ValueError("No se pudo determinar el tipo de post")
            
            # Validar que el tipo sea válido
            try:
                post_type = PostType(post_type_str)
            except ValueError:
                raise ValueError(f"Tipo de post no válido: {post_type_str}")
            
            # 4. Validar output
            self.logger.info("Validando clasificación generada")
            if not justification:
                justification = f"Clasificado como {post_type.value} basándose en el análisis del prompt"
            
            # 5. Actualizar estado
            state["post_type"] = post_type
            state["post_justification"] = justification
            state["current_step"] = "brand_voice"
            state["completed_steps"].append("post_classification")
            
            # 6. Log del proceso
            generation_time = time.time() - start_time
            self.logger.info(f"Clasificación del post completada en {generation_time:.2f}s")
            self.logger.info(f"Tipo de post: {post_type.value}")
            self.logger.info(f"Justificación: {justification}")
            
            # Registrar tiempo del agente
            state["agent_timings"]["post_classifier"] = generation_time
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Error en PostClassifier: {str(e)}"
            self.logger.error(error_msg)
            
            # Actualizar estado con error
            state["errors"].append(f"[post_classifier]: {error_msg}")
            state["current_step"] = "error"
            state["is_error"] = True
            
            # Registrar tiempo del agente
            state["agent_timings"]["post_classifier"] = generation_time
        
        return state
    
    def _create_analysis_summary(self, analysis) -> str:
        """
        Crea un resumen del análisis para el prompt de clasificación
        
        Args:
            analysis: Análisis del prompt (puede ser dict o PromptAnalysis)
            
        Returns:
            Resumen formateado del análisis
        """
        summary_parts = []
        
        # Manejar tanto dict como objeto PromptAnalysis
        if hasattr(analysis, 'objective'):
            objective = analysis.objective
            audience = analysis.audience
            brand_cues = analysis.brand_cues
        else:
            objective = analysis.get('objective')
            audience = analysis.get('audience')
            brand_cues = analysis.get('brand_cues', [])
        
        if objective:
            summary_parts.append(f"OBJETIVO: {objective}")
        
        if audience:
            summary_parts.append(f"AUDIENCIA: {audience}")
        
        if brand_cues:
            summary_parts.append(f"BRAND CUES: {', '.join(brand_cues)}")
        
        # Continuar con el manejo compatible
        if hasattr(analysis, 'key_facts'):
            key_facts = analysis.key_facts
            urgency = analysis.urgency
            platform = analysis.platform
        else:
            key_facts = analysis.get('key_facts', [])
            urgency = analysis.get('urgency')
            platform = analysis.get('platform')
        
        if key_facts:
            summary_parts.append(f"HECHOS CLAVE: {', '.join(key_facts)}")
        
        if urgency:
            summary_parts.append(f"URGENCIA: {urgency}")
        
        if platform:
            summary_parts.append(f"PLATAFORMA: {platform}")
        
        # Continuar con el manejo compatible para el resto
        if hasattr(analysis, 'tone_indicators'):
            tone_indicators = analysis.tone_indicators
            content_goals = analysis.content_goals
        else:
            tone_indicators = analysis.get('tone_indicators', [])
            content_goals = analysis.get('content_goals', [])
        
        if tone_indicators:
            summary_parts.append(f"TONO: {', '.join(tone_indicators)}")
        
        if content_goals:
            summary_parts.append(f"METAS: {', '.join(content_goals)}")
        
        return "\n".join(summary_parts)
    
    async def classify_post(self, analysis) -> tuple[PostType, str]:
        """
        Método auxiliar para clasificar un post específico
        
        Args:
            analysis: Análisis del prompt
            
        Returns:
            Tupla con (tipo de post, justificación)
        """
        try:
            analysis_summary = self._create_analysis_summary(analysis)
            prompt = POST_CLASSIFIER_TEMPLATE.format(analysis=analysis_summary)
            
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con tipo de post y justificación"
            )
            
            post_type = PostType(response["post_type"])
            justification = response.get("justification", "")
            
            return post_type, justification
            
        except Exception as e:
            self.logger.error(f"Error clasificando post: {e}")
            raise

