"""
Agente Brand Voice Agent - Define tono, personalidad y estilo de la marca
"""
import logging
import time
from typing import Dict, Any

from src.models.content_brief import BrandVoice
from tools.llm_client import LLMClient
from config.prompts import get_prompt_template, AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class BrandVoiceAgent:
    """
    Agente que define la voz de marca basándose en el análisis del prompt
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado y define la voz de marca
        
        Args:
            state: Estado del workflow
            
        Returns:
            Estado actualizado con la voz de marca
        """
        start_time = time.time()
        
        try:
            self.logger.info("Iniciando definición de voz de marca")
            
            # Verificar que tenemos el análisis del prompt y tipo de post
            if not state.get("prompt_analysis"):
                raise ValueError("No hay análisis del prompt disponible")
            
            if not state.get("post_type"):
                raise ValueError("No hay tipo de post disponible")
            
            # 1. Preparar prompt específico según idioma
            language_config = state.get("language_config", {})
            language = language_config.get("language", "es")
            
            analysis_summary = self._create_analysis_summary(state["prompt_analysis"])
            post_type = state["post_type"].value
            
            template = get_prompt_template(AGENT_TEMPLATES["brand_voice"], language)
            prompt = template.format(
                analysis=analysis_summary,
                post_type=post_type
            )
            
            # 2. Llamar al LLM
            self.logger.info("Generando voz de marca con LLM")
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con voz de marca"
            )
            
            # 3. Parsear respuesta
            self.logger.info("Parseando voz de marca del LLM")
            brand_voice = BrandVoice(**response)
            
            # 4. Validar output
            self.logger.info("Validando voz de marca generada")
            if not brand_voice.tone or not brand_voice.personality:
                raise ValueError("Voz de marca incompleta: faltan tono o personalidad")
            
            # 5. Actualizar estado
            state["brand_voice"] = brand_voice
            state["current_step"] = "fact_grounding"
            state["completed_steps"].append("brand_voice")
            
            # 6. Log del proceso
            generation_time = time.time() - start_time
            self.logger.info(f"Voz de marca definida en {generation_time:.2f}s")
            self.logger.info(f"Tono: {brand_voice.tone}")
            self.logger.info(f"Personalidad: {brand_voice.personality}")
            self.logger.info(f"Estilo: {brand_voice.style}")
            
            # Registrar tiempo del agente
            state["agent_timings"]["brand_voice_agent"] = generation_time
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Error en BrandVoiceAgent: {str(e)}"
            self.logger.error(error_msg)
            
            # Actualizar estado con error
            state["errors"].append(f"[brand_voice_agent]: {error_msg}")
            state["current_step"] = "error"
            state["is_error"] = True
            
            # Registrar tiempo del agente
            state["agent_timings"]["brand_voice_agent"] = generation_time
        
        return state
    
    def _create_analysis_summary(self, analysis) -> str:
        """
        Crea un resumen del análisis para el prompt de voz de marca
        
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
        if hasattr(analysis, 'tone_indicators'):
            tone_indicators = analysis.tone_indicators
            content_goals = analysis.content_goals
        else:
            tone_indicators = analysis.get('tone_indicators', [])
            content_goals = analysis.get('content_goals', [])
        
        if tone_indicators:
            summary_parts.append(f"INDICADORES DE TONO: {', '.join(tone_indicators)}")
        
        if content_goals:
            summary_parts.append(f"METAS DE CONTENIDO: {', '.join(content_goals)}")
        
        return "\n".join(summary_parts)
    
    async def define_brand_voice(self, analysis, post_type) -> BrandVoice:
        """
        Método auxiliar para definir la voz de marca
        
        Args:
            analysis: Análisis del prompt
            post_type: Tipo de post
            
        Returns:
            Voz de marca definida
        """
        try:
            analysis_summary = self._create_analysis_summary(analysis)
            prompt = BRAND_VOICE_TEMPLATE.format(
                analysis=analysis_summary,
                post_type=post_type.value
            )
            
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con voz de marca"
            )
            
            return BrandVoice(**response)
            
        except Exception as e:
            self.logger.error(f"Error definiendo voz de marca: {e}")
            raise

