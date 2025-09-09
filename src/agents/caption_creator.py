"""
Agente Caption Creator - Crea caption, CTA y hashtags para el post
"""
import logging
import time
from typing import Dict, Any

from models.content_brief import EngagementElements
from tools.llm_client import LLMClient
from config.prompts import get_prompt_template, AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class CaptionCreator:
    """
    Agente que crea elementos de engagement para el post
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado y crea elementos de engagement
        
        Args:
            state: Estado del workflow
            
        Returns:
            Estado actualizado con elementos de engagement
        """
        start_time = time.time()
        
        try:
            self.logger.info("Iniciando creación de elementos de engagement")
            
            # Verificar que tenemos todos los elementos necesarios
            required_elements = ["core_content", "post_type", "brand_voice", "prompt_analysis"]
            for element in required_elements:
                if not state.get(element):
                    raise ValueError(f"Elemento requerido no disponible: {element}")
            
            # 1. Preparar prompt específico según idioma
            language_config = state.get("language_config", {})
            language = language_config.get("language", "es")
            
            core_content = state["core_content"]
            post_type = state["post_type"].value
            brand_voice_summary = self._create_brand_voice_summary(state["brand_voice"])
            
            # Manejar tanto dict como objeto PromptAnalysis
            prompt_analysis = state["prompt_analysis"]
            if hasattr(prompt_analysis, 'objective'):
                objective = prompt_analysis.objective
            else:
                objective = prompt_analysis.get('objective', 'Generar contenido atractivo')
            
            template = get_prompt_template(AGENT_TEMPLATES["caption_creator"], language)
            prompt = template.format(
                core_content=core_content,
                post_type=post_type,
                brand_voice=brand_voice_summary,
                objective=objective
            )
            
            # 2. Llamar al LLM
            self.logger.info("Generando elementos de engagement con LLM")
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con elementos de engagement"
            )
            
            # 3. Parsear respuesta
            self.logger.info("Parseando elementos de engagement del LLM")
            engagement_elements = EngagementElements(**response)
            
            # 4. Validar y mejorar output
            self.logger.info("Validando y mejorando elementos de engagement")
            engagement_elements = self._validate_and_enhance_engagement(engagement_elements)
            
            # 5. Actualizar estado
            state["engagement_elements"] = engagement_elements
            state["current_step"] = "visual_concept"
            state["completed_steps"].append("caption_creation")
            
            # 6. Log del proceso
            generation_time = time.time() - start_time
            self.logger.info(f"Elementos de engagement creados en {generation_time:.2f}s")
            self.logger.info(f"Caption creado: {len(engagement_elements.caption)} caracteres")
            self.logger.info(f"Hashtags: {len(engagement_elements.hashtags)}")
            
            # Registrar tiempo del agente
            state["agent_timings"]["caption_creator"] = generation_time
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Error en CaptionCreator: {str(e)}"
            self.logger.error(error_msg)
            
            # Actualizar estado con error
            state["errors"].append(f"[caption_creator]: {error_msg}")
            state["current_step"] = "error"
            state["is_error"] = True
            
            # Registrar tiempo del agente
            state["agent_timings"]["caption_creator"] = generation_time
        
        return state
    
    def _create_brand_voice_summary(self, brand_voice) -> str:
        """Crea resumen de la voz de marca para el prompt"""
        summary_parts = []
        
        # Manejar tanto dict como objeto BrandVoice
        if hasattr(brand_voice, 'tone'):
            tone = brand_voice.tone
            personality = brand_voice.personality
            communication_style = brand_voice.communication_style
        else:
            tone = brand_voice.get('tone')
            personality = brand_voice.get('personality')
            communication_style = brand_voice.get('communication_style')
        
        if tone:
            summary_parts.append(f"TONO: {tone}")
        
        if personality:
            summary_parts.append(f"PERSONALIDAD: {personality}")
        
        if communication_style:
            summary_parts.append(f"ESTILO: {communication_style}")
        
        return " | ".join(summary_parts) if summary_parts else "Voz de marca no especificada"
    
    def _validate_and_enhance_engagement(self, engagement: EngagementElements) -> EngagementElements:
        """
        Valida y mejora los elementos de engagement
        
        Args:
            engagement: Elementos de engagement a validar
            
        Returns:
            Elementos de engagement validados y mejorados
        """
        # Validar caption
        if not engagement.caption or len(engagement.caption.strip()) < 10:
            engagement.caption = "Descubre más sobre este increíble contenido"
        
        # Validar CTA
        if not engagement.call_to_action or len(engagement.call_to_action.strip()) < 5:
            engagement.call_to_action = "¡Comparte tu opinión!"
        
        # Validar hashtags
        if not engagement.hashtags:
            engagement.hashtags = ["#marketing", "#contenido", "#engagement"]
        else:
            # Limpiar hashtags
            cleaned_hashtags = []
            for hashtag in engagement.hashtags:
                cleaned = hashtag.strip()
                if cleaned and not cleaned.startswith("#"):
                    cleaned = "#" + cleaned
                if cleaned and len(cleaned) > 1:
                    cleaned_hashtags.append(cleaned)
            
            # Limitar a máximo 10 hashtags
            engagement.hashtags = cleaned_hashtags[:10]
        
        # Validar engagement hooks
        if not engagement.engagement_hooks:
            engagement.engagement_hooks = ["¿Qué opinas?", "¿Te ha gustado?"]
        
        # Validar preguntas
        if not engagement.questions:
            engagement.questions = ["¿Qué te parece este contenido?"]
        
        return engagement
    
    async def create_engagement_elements(self, core_content: str, post_type, brand_voice, objective: str) -> EngagementElements:
        """
        Método auxiliar para crear elementos de engagement
        
        Args:
            core_content: Contenido principal del post
            post_type: Tipo de post
            brand_voice: Voz de marca
            objective: Objetivo del post
            
        Returns:
            Elementos de engagement creados
        """
        try:
            brand_voice_summary = self._create_brand_voice_summary(brand_voice)
            
            prompt = CAPTION_CREATOR_TEMPLATE.format(
                core_content=core_content,
                post_type=post_type.value,
                brand_voice=brand_voice_summary,
                objective=objective
            )
            
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con elementos de engagement"
            )
            
            engagement = EngagementElements(**response)
            return self._validate_and_enhance_engagement(engagement)
            
        except Exception as e:
            self.logger.error(f"Error creando elementos de engagement: {e}")
            raise

