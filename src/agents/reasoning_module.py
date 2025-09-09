"""
Agente Reasoning Module - Explica decisiones estratégicas tomadas
"""
import logging
import time
from typing import Dict, Any

from src.models.content_brief import ReasoningModule
from src.tools.llm_client import LLMClient
from src.config.prompts import get_prompt_template, AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class ReasoningModuleAgent:
    """
    Agente que explica las decisiones estratégicas tomadas para el post
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado y genera el razonamiento estratégico
        
        Args:
            state: Estado del workflow
            
        Returns:
            Estado actualizado con el razonamiento estratégico
        """
        start_time = time.time()
        
        try:
            self.logger.info("Iniciando generación de razonamiento estratégico")
            
            # Verificar que tenemos todos los elementos necesarios
            required_elements = ["prompt_analysis", "post_type", "brand_voice", "core_content", 
                               "engagement_elements", "visual_concept"]
            for element in required_elements:
                if not state.get(element):
                    raise ValueError(f"Elemento requerido no disponible: {element}")
            
            # 1. Preparar prompt específico según idioma
            language_config = state.get("language_config", {})
            language = language_config.get("language", "es")
            
            full_analysis = self._create_full_analysis_summary(state)
            final_brief_summary = self._create_final_brief_summary(state)
            
            template = get_prompt_template(AGENT_TEMPLATES["reasoning_module"], language)
            prompt = template.format(
                full_analysis=full_analysis,
                final_brief=final_brief_summary
            )
            
            # 2. Llamar al LLM
            self.logger.info("Generando razonamiento estratégico con LLM")
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con razonamiento estratégico"
            )
            
            # 3. Parsear respuesta
            self.logger.info("Parseando razonamiento estratégico del LLM")
            reasoning = ReasoningModule(**response)
            
            # 4. Validar y mejorar output
            self.logger.info("Validando y mejorando razonamiento estratégico")
            reasoning = self._validate_and_enhance_reasoning(reasoning)
            
            # 5. Actualizar estado
            state["reasoning"] = reasoning
            state["current_step"] = "final_assembly"
            state["completed_steps"].append("reasoning")
            
            # 6. Log del proceso
            generation_time = time.time() - start_time
            self.logger.info(f"Razonamiento estratégico generado en {generation_time:.2f}s")
            self.logger.info(f"Decisiones estratégicas: {len(reasoning.strategic_decisions)}")
            
            # Verificar elementos requeridos (engagement_elements es opcional)
            required_elements = ["prompt_analysis", "post_type", "brand_voice"]
            missing_elements = []
            
            for element in required_elements:
                if not state.get(element):
                    missing_elements.append(element)
            
            if missing_elements:
                error_msg = f"Elemento requerido no disponible: {', '.join(missing_elements)}"
                self.logger.error(error_msg)
                
                # Actualizar estado con error
                state["errors"].append(f"[reasoning_module]: {error_msg}")
                state["current_step"] = "error"
            
            # Registrar tiempo del agente
            state["agent_timings"]["reasoning_module"] = generation_time
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Error en ReasoningModuleAgent: {str(e)}"
            self.logger.error(error_msg)
            
            # Actualizar estado con error
            state["errors"].append(f"[reasoning_module]: {error_msg}")
            state["current_step"] = "error"
            state["is_error"] = True
            
            # Registrar tiempo del agente
            state["agent_timings"]["reasoning_module"] = generation_time
        
        return state
    
    def _create_full_analysis_summary(self, state) -> str:
        """Crea resumen completo del análisis para el prompt"""
        summary_parts = []
        
        # Análisis del prompt
        if state.get("prompt_analysis"):
            analysis = state["prompt_analysis"]
            summary_parts.append("ANÁLISIS DEL PROMPT:")
            
            # Manejar tanto dict como objeto PromptAnalysis
            if hasattr(analysis, 'objective'):
                objective = analysis.objective
                audience = analysis.audience
                brand_cues = analysis.brand_cues
                key_facts = analysis.key_facts
                content_goals = analysis.content_goals
            else:
                objective = analysis.get('objective')
                audience = analysis.get('audience')
                brand_cues = analysis.get('brand_cues', [])
                key_facts = analysis.get('key_facts', [])
                content_goals = analysis.get('content_goals', [])
            
            if objective:
                summary_parts.append(f"- Objetivo: {objective}")
            if audience:
                summary_parts.append(f"- Audiencia: {audience}")
            if brand_cues:
                summary_parts.append(f"- Indicadores de marca: {', '.join(brand_cues)}")
            if key_facts:
                summary_parts.append(f"- Hechos clave: {', '.join(key_facts)}")
            if content_goals:
                summary_parts.append(f"- Metas de contenido: {', '.join(content_goals)}")
        
        # Tipo de post
        if state.get("post_type"):
            summary_parts.append(f"TIPO DE POST: {state['post_type'].value}")
        
        # Voz de marca
        if state.get("brand_voice"):
            brand_voice = state["brand_voice"]
            summary_parts.append("VOZ DE MARCA:")
            
            # Manejar tanto dict como objeto BrandVoice
            if hasattr(brand_voice, 'tone'):
                tone = brand_voice.tone
                personality = brand_voice.personality
            else:
                tone = brand_voice.get('tone')
                personality = brand_voice.get('personality')
            
            if tone:
                summary_parts.append(f"- Tono: {tone}")
            if personality:
                summary_parts.append(f"- Personalidad: {personality}")
        
        return "\n".join(summary_parts)
    
    def _create_final_brief_summary(self, state) -> str:
        """Crea resumen del brief final para el prompt"""
        summary_parts = []
        
        # Contenido principal
        if state.get("core_content"):
            summary_parts.append(f"CONTENIDO: {state['core_content'][:200]}...")
        
        # Elementos de engagement
        if state.get("engagement_elements"):
            engagement = state["engagement_elements"]
            
            # Manejar tanto dict como objeto EngagementElements
            if hasattr(engagement, 'caption'):
                caption = engagement.caption
                call_to_action = engagement.call_to_action
                hashtags = engagement.hashtags
            else:
                caption = engagement.get('caption', '')
                call_to_action = engagement.get('call_to_action', '')
                hashtags = engagement.get('hashtags', [])
            
            summary_parts.append(f"CAPTION: {caption}")
            summary_parts.append(f"CTA: {call_to_action}")
            summary_parts.append(f"HASHTAGS: {', '.join(hashtags[:5])}")
        
        # Concepto visual
        if state.get("visual_concept"):
            visual = state["visual_concept"]
            
            # Manejar tanto dict como objeto VisualConcept
            if hasattr(visual, 'mood'):
                mood = visual.mood
                color_palette = visual.color_palette
            else:
                mood = visual.get('mood', '')
                color_palette = visual.get('color_palette', [])
            
            summary_parts.append(f"MOOD VISUAL: {mood}")
            summary_parts.append(f"PALETA: {', '.join(color_palette[:3])}")
        
        return "\n".join(summary_parts)
    
    def _validate_and_enhance_reasoning(self, reasoning: ReasoningModule) -> ReasoningModule:
        """
        Valida y mejora el razonamiento estratégico
        
        Args:
            reasoning: Razonamiento a validar
            
        Returns:
            Razonamiento validado y mejorado
        """
        # Validar decisiones estratégicas
        if not reasoning.strategic_decisions:
            reasoning.strategic_decisions = [
                "Se seleccionó el tipo de post basándose en el objetivo y audiencia",
                "La voz de marca se definió considerando los brand cues del prompt",
                "Los elementos de engagement se optimizaron para maximizar la interacción"
            ]
        
        # Validar consideraciones de audiencia
        if not reasoning.audience_considerations or len(reasoning.audience_considerations.strip()) < 10:
            reasoning.audience_considerations = "Se consideró la demografía y psicografía identificadas en el prompt para optimizar el contenido"
        
        # Validar optimización de plataforma
        if not reasoning.platform_optimization or len(reasoning.platform_optimization.strip()) < 10:
            reasoning.platform_optimization = "El contenido se optimizó para redes sociales con elementos visuales atractivos y engagement"
        
        # Validar análisis competitivo
        if not reasoning.competitive_analysis:
            reasoning.competitive_analysis = "Se consideró el contexto del mercado para diferenciar el contenido"
        
        # Validar evaluación de riesgos
        if not reasoning.risk_assessment or len(reasoning.risk_assessment.strip()) < 10:
            reasoning.risk_assessment = "Se evaluaron riesgos de engagement bajo y se implementaron elementos de captura de atención"
        
        return reasoning
    
    async def create_reasoning(self, state) -> ReasoningModule:
        """
        Método auxiliar para crear razonamiento estratégico
        
        Args:
            state: Estado completo del workflow
            
        Returns:
            Razonamiento estratégico creado
        """
        try:
            full_analysis = self._create_full_analysis_summary(state)
            final_brief_summary = self._create_final_brief_summary(state)
            
            prompt = REASONING_MODULE_TEMPLATE.format(
                full_analysis=full_analysis,
                final_brief=final_brief_summary
            )
            
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con razonamiento estratégico"
            )
            
            reasoning = ReasoningModule(**response)
            return self._validate_and_enhance_reasoning(reasoning)
            
        except Exception as e:
            self.logger.error(f"Error creando razonamiento estratégico: {e}")
            raise

