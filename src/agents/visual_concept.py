"""
Agente Visual Concept - Genera brief detallado para el diseñador
"""
import logging
import time
from typing import Dict, Any

from src.models.content_brief import VisualConcept
from tools.llm_client import LLMClient
from config.prompts import get_prompt_template, AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class VisualConceptAgent:
    """
    Agente que genera un concepto visual detallado para el diseñador
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado y genera el concepto visual
        
        Args:
            state: Estado del workflow
            
        Returns:
            Estado actualizado con el concepto visual
        """
        start_time = time.time()
        
        try:
            self.logger.info("Iniciando generación de concepto visual")
            
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
                objective = prompt_analysis.get('objective', 'Crear contenido visual atractivo')
            
            template = get_prompt_template(AGENT_TEMPLATES["visual_concept"], language)
            prompt = template.format(
                core_content=core_content,
                post_type=post_type,
                brand_voice=brand_voice_summary,
                objective=objective
            )
            
            # 2. Llamar al LLM
            self.logger.info("Generando concepto visual con LLM")
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con concepto visual"
            )
            
            # 3. Parsear respuesta
            self.logger.info("Parseando concepto visual del LLM")
            visual_concept = VisualConcept(**response)
            
            # 4. Validar y mejorar output
            self.logger.info("Validando y mejorando concepto visual")
            visual_concept = self._validate_and_enhance_visual_concept(visual_concept)
            
            # 5. Actualizar estado
            state["visual_concept"] = visual_concept
            state["current_step"] = "reasoning"
            state["completed_steps"].append("visual_concept")
            
            # 6. Log del proceso
            generation_time = time.time() - start_time
            self.logger.info(f"Concepto visual generado en {generation_time:.2f}s")
            self.logger.info(f"Mood: {visual_concept.mood}")
            self.logger.info(f"Colores: {len(visual_concept.color_palette)}")
            
            # Registrar tiempo del agente
            state["agent_timings"]["visual_concept"] = generation_time
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Error en VisualConceptAgent: {str(e)}"
            self.logger.error(error_msg)
            
            # Actualizar estado con error
            state["errors"].append(f"[visual_concept]: {error_msg}")
            state["current_step"] = "error"
            state["is_error"] = True
            
            # Registrar tiempo del agente
            state["agent_timings"]["visual_concept"] = generation_time
        
        return state
    
    def _create_brand_voice_summary(self, brand_voice) -> str:
        """Crea resumen de la voz de marca para el prompt"""
        summary_parts = []
        
        # Manejar tanto dict como objeto BrandVoice
        if hasattr(brand_voice, 'tone'):
            tone = brand_voice.tone
            personality = brand_voice.personality
            style = getattr(brand_voice, 'style', None)
            values = getattr(brand_voice, 'values', [])
        else:
            tone = brand_voice.get('tone')
            personality = brand_voice.get('personality')
            style = brand_voice.get('style')
            values = brand_voice.get('values', [])
        
        if tone:
            summary_parts.append(f"TONO: {tone}")
        
        if personality:
            summary_parts.append(f"PERSONALIDAD: {personality}")
        
        if style:
            summary_parts.append(f"ESTILO: {style}")
        
        if values:
            summary_parts.append(f"VALORES: {', '.join(values)}")
        
        return "\n".join(summary_parts)
    
    def _validate_and_enhance_visual_concept(self, visual_concept: VisualConcept) -> VisualConcept:
        """
        Valida y mejora el concepto visual
        
        Args:
            visual_concept: Concepto visual a validar
            
        Returns:
            Concepto visual validado y mejorado
        """
        # Validar mood
        if not visual_concept.mood or len(visual_concept.mood.strip()) < 3:
            visual_concept.mood = "Profesional y atractivo"
        
        # Validar paleta de colores
        if not visual_concept.color_palette:
            visual_concept.color_palette = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D"]
        else:
            # Limpiar colores
            cleaned_colors = []
            for color in visual_concept.color_palette:
                cleaned = color.strip()
                if cleaned and (cleaned.startswith("#") or cleaned.startswith("rgb")):
                    cleaned_colors.append(cleaned)
            
            # Asegurar al menos 3 colores
            if len(cleaned_colors) < 3:
                cleaned_colors.extend(["#2E86AB", "#A23B72", "#F18F01"])
            
            visual_concept.color_palette = cleaned_colors[:6]  # Máximo 6 colores
        
        # Validar tipo de imagen
        if not visual_concept.imagery_type or len(visual_concept.imagery_type.strip()) < 3:
            visual_concept.imagery_type = "Imágenes profesionales y atractivas"
        
        # Validar estilo de layout
        if not visual_concept.layout_style or len(visual_concept.layout_style.strip()) < 3:
            visual_concept.layout_style = "Layout limpio y moderno"
        
        # Validar elementos visuales
        if not visual_concept.visual_elements:
            visual_concept.visual_elements = ["Iconos", "Tipografía clara", "Espaciado consistente"]
        
        # Validar notas de diseño
        if not visual_concept.design_notes or len(visual_concept.design_notes.strip()) < 10:
            visual_concept.design_notes = "Mantener consistencia con la identidad de marca y asegurar legibilidad"
        
        return visual_concept
    
    async def create_visual_concept(self, core_content: str, post_type, brand_voice, objective: str) -> VisualConcept:
        """
        Método auxiliar para crear concepto visual
        
        Args:
            core_content: Contenido principal del post
            post_type: Tipo de post
            brand_voice: Voz de marca
            objective: Objetivo del post
            engagement_elements: Elementos de engagement
            
        Returns:
            Concepto visual creado
        """
        try:
            language_config = {"language": "es"}
            language = language_config.get("language", "es")
            
            brand_voice_summary = self._create_brand_voice_summary(brand_voice)
            engagement_summary = self._create_engagement_summary(engagement_elements)
            
            template = get_prompt_template(AGENT_TEMPLATES["visual_concept"], language)
            prompt = template.format(
                core_content=core_content,
                post_type=post_type.value,
                brand_voice=brand_voice_summary,
                engagement=engagement_summary
            )
            
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con concepto visual"
            )
            
            visual_concept = VisualConcept(**response)
            return self._validate_and_enhance_visual_concept(visual_concept)
            
        except Exception as e:
            self.logger.error(f"Error creando concepto visual: {e}")
            raise

