"""
Agente Text Generator - Genera contenido principal coherente del post
"""
import logging
import time
from typing import Dict, Any
from src.models.content_brief import ContentBrief
from src.tools.llm_client import LLMClient
from src.config.prompts import get_prompt_template, AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class TextGenerator:
    """
    Agente que genera el contenido principal coherente del post de marketing
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado y genera el contenido principal
        
        Args:
            state: Estado del workflow
            
        Returns:
            Estado actualizado con el contenido principal
        """
        start_time = time.time()
        
        try:
            self.logger.info("Iniciando generación de contenido principal")
            
            # Verificar que tenemos todos los elementos necesarios
            required_elements = ["prompt_analysis", "post_type", "brand_voice", "factual_grounding"]
            for element in required_elements:
                if not state.get(element):
                    raise ValueError(f"Elemento requerido no disponible: {element}")
            
            # 1. Preparar prompt específico según idioma
            language_config = state.get("language_config", {})
            language = language_config.get("language", "es")
            
            analysis_summary = self._create_analysis_summary(state["prompt_analysis"])
            post_type = state["post_type"].value
            brand_voice_summary = self._create_brand_voice_summary(state["brand_voice"])
            facts_summary = self._create_facts_summary(state["factual_grounding"])
            
            template = get_prompt_template(AGENT_TEMPLATES["text_generator"], language)
            prompt = template.format(
                analysis=analysis_summary,
                post_type=post_type,
                brand_voice=brand_voice_summary,
                facts=facts_summary
            )
            
            # 2. Llamar al LLM
            self.logger.info("Generando contenido principal con LLM")
            response = await self.llm.generate(prompt)
            
            # 3. Limpiar y validar respuesta
            self.logger.info("Limpiando y validando contenido generado")
            core_content = self._clean_and_validate_content(response.content)
            
            # 4. Validar output
            self.logger.info("Validando contenido generado")
            if not core_content or len(core_content.strip()) < 50:
                raise ValueError("Contenido generado demasiado corto o vacío")
            
            # 5. Actualizar estado
            state["core_content"] = core_content
            state["current_step"] = "caption_creation"
            state["completed_steps"].append("text_generation")
            
            # 6. Log del proceso
            generation_time = time.time() - start_time
            self.logger.info(f"Contenido principal generado en {generation_time:.2f}s")
            self.logger.info(f"Longitud del contenido: {len(core_content)} caracteres")
            
            # Registrar tiempo del agente
            state["agent_timings"]["text_generator"] = generation_time
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Error en TextGenerator: {str(e)}"
            self.logger.error(error_msg)
            
            # Actualizar estado con error
            state["errors"].append(f"[text_generator]: {error_msg}")
            state["current_step"] = "error"
            state["is_error"] = True
            
            # Registrar tiempo del agente
            state["agent_timings"]["text_generator"] = generation_time
        
        return state
    
    def _create_analysis_summary(self, analysis) -> str:
        """Crea resumen del análisis para el prompt"""
        summary_parts = []
        
        # Manejar tanto dict como objeto PromptAnalysis
        if hasattr(analysis, 'objective'):
            objective = analysis.objective
            audience = analysis.audience
            content_goals = analysis.content_goals
        else:
            objective = analysis.get('objective')
            audience = analysis.get('audience')
            content_goals = analysis.get('content_goals', [])
        
        if objective:
            summary_parts.append(f"OBJETIVO: {objective}")
        
        if audience:
            summary_parts.append(f"AUDIENCIA: {audience}")
        
        if content_goals:
            summary_parts.append(f"METAS: {', '.join(content_goals)}")
        
        return "\n".join(summary_parts)
    
    def _create_brand_voice_summary(self, brand_voice) -> str:
        """Crea resumen de la voz de marca para el prompt"""
        summary_parts = []
        
        # Manejar tanto dict como objeto BrandVoice
        if hasattr(brand_voice, 'tone'):
            tone = brand_voice.tone
            personality = brand_voice.personality
            style = brand_voice.style
            language_level = brand_voice.language_level
        else:
            tone = brand_voice.get('tone')
            personality = brand_voice.get('personality')
            style = brand_voice.get('style')
            language_level = brand_voice.get('language_level')
        
        if tone:
            summary_parts.append(f"TONO: {tone}")
        
        if personality:
            summary_parts.append(f"PERSONALIDAD: {personality}")
        
        if style:
            summary_parts.append(f"ESTILO: {style}")
        
        if language_level:
            summary_parts.append(f"NIVEL DE LENGUAJE: {language_level}")
        
        return "\n".join(summary_parts)
    
    def _create_facts_summary(self, factual_grounding) -> str:
        """Crea resumen de los hechos para el prompt"""
        # Manejar tanto dict como objeto FactualGrounding
        if hasattr(factual_grounding, 'key_facts'):
            key_facts = factual_grounding.key_facts
        else:
            key_facts = factual_grounding.get('key_facts', [])
        
        if key_facts:
            return f"HECHOS CLAVE: {', '.join(key_facts)}"
        return "HECHOS: Información del prompt analizada"
    
    def _clean_and_validate_content(self, content: str) -> str:
        """
        Limpia y valida el contenido generado
        
        Args:
            content: Contenido generado por el LLM
            
        Returns:
            Contenido limpio y validado
        """
        if not content:
            return ""
        
        # Limpiar contenido
        cleaned = content.strip()
        
        # Remover marcadores de formato si existen
        cleaned = cleaned.replace("```", "").replace("**", "").replace("*", "")
        
        # Remover líneas vacías múltiples
        import re
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        
        # Asegurar que no empiece con números o guiones
        cleaned = re.sub(r'^[\d\-\.\s]+', '', cleaned)
        
        # Limitar longitud máxima (para redes sociales)
        max_length = 2000
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        
        return cleaned
    
    async def generate_content(self, analysis, post_type, brand_voice, facts) -> str:
        """
        Método auxiliar para generar contenido específico
        
        Args:
            analysis: Análisis del prompt
            post_type: Tipo de post
            brand_voice: Voz de marca
            facts: Base factual
            
        Returns:
            Contenido generado
        """
        try:
            analysis_summary = self._create_analysis_summary(analysis)
            brand_voice_summary = self._create_brand_voice_summary(brand_voice)
            facts_summary = self._create_facts_summary(facts)
            
            prompt = TEXT_GENERATOR_TEMPLATE.format(
                analysis=analysis_summary,
                post_type=post_type.value,
                brand_voice=brand_voice_summary,
                facts=facts_summary
            )
            
            response = await self.llm.generate(prompt)
            return self._clean_and_validate_content(response)
            
        except Exception as e:
            self.logger.error(f"Error generando contenido: {e}")
            raise

