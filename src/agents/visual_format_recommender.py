"""
Visual Format Recommender - Recomienda el formato visual más efectivo
"""
import logging
import time
from typing import Dict, Any
from enum import Enum

from tools.llm_client import LLMClient
from config.prompts import get_prompt_template, AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class VisualFormat(Enum):
    """Tipos de formato visual"""
    IMAGE = "Image"
    VIDEO = "Video"
    CAROUSEL = "Carousel"
    INFOGRAPHIC = "Infographic"

class VisualFormatRecommender:
    """
    Agente que recomienda el formato visual más efectivo basado en el contenido y plataforma
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado y recomienda el formato visual óptimo
        
        Args:
            state: Estado del workflow con análisis previo
            
        Returns:
            Estado actualizado con recomendación de formato visual
        """
        start_time = time.time()
        
        try:
            self.logger.info("Iniciando recomendación de formato visual")
            
            # Verificar elementos necesarios
            required_elements = ["prompt_analysis", "post_type", "brand_voice"]
            for element in required_elements:
                if not state.get(element):
                    raise ValueError(f"Elemento requerido no disponible: {element}")
            
            # Preparar prompt específico según idioma
            language_config = state.get("language_config", {})
            language = language_config.get("language", "es")
            
            analysis_summary = self._create_analysis_summary(state["prompt_analysis"])
            post_type = state["post_type"].value
            platform = getattr(state["prompt_analysis"], 'platform', 'general')
            
            template = get_prompt_template(AGENT_TEMPLATES["visual_format_recommender"], language)
            prompt = template.format(
                analysis=analysis_summary,
                post_type=post_type,
                platform=platform
            )
            
            # Llamar al LLM
            self.logger.info("Generando recomendación de formato visual con LLM")
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con recomendación de formato visual"
            )
            
            # Parsear respuesta
            self.logger.info("Parseando recomendación de formato visual")
            format_recommendation = self._parse_format_recommendation(response)
            
            # Validar y mejorar recomendación
            format_recommendation = self._validate_and_enhance_recommendation(format_recommendation)
            
            # Actualizar estado usando función de estado
            from graph.state import update_state_with_visual_format, WorkflowState
            if isinstance(state, dict):
                workflow_state = WorkflowState(**state)
                workflow_state = update_state_with_visual_format(workflow_state, format_recommendation)
                state.update(workflow_state.dict())
            else:
                state = update_state_with_visual_format(state, format_recommendation)
            
            # Log del proceso
            processing_time = time.time() - start_time
            self.logger.info(f"Recomendación de formato visual generada en {processing_time:.2f}s")
            
            # Registrar tiempo del agente
            if isinstance(state, dict):
                if "agent_timings" not in state:
                    state["agent_timings"] = {}
                state["agent_timings"]["visual_format_recommender"] = processing_time
            else:
                if not hasattr(state, 'agent_timings'):
                    state.agent_timings = {}
                state.agent_timings["visual_format_recommender"] = processing_time
            
            return state
            
        except Exception as e:
            error_msg = f"Error en Visual Format Recommender: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
            return state
    
    def _create_analysis_summary(self, analysis) -> str:
        """Crea un resumen del análisis del prompt"""
        if hasattr(analysis, 'objective'):
            return f"Objetivo: {analysis.objective}, Audiencia: {analysis.audience}, Plataforma: {getattr(analysis, 'platform', 'general')}"
        else:
            return f"Objetivo: {analysis.get('objective', 'N/A')}, Audiencia: {analysis.get('audience', 'N/A')}"
    
    def _parse_format_recommendation(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea la respuesta del LLM"""
        return {
            "recommended_format": response.get("recommended_format", "Image"),
            "justification": response.get("justification", ""),
            "platform_optimization": response.get("platform_optimization", ""),
            "engagement_potential": response.get("engagement_potential", "medium"),
            "production_complexity": response.get("production_complexity", "low"),
            "alternative_formats": response.get("alternative_formats", [])
        }
    
    def _validate_and_enhance_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Valida y mejora la recomendación"""
        # Validar formato recomendado
        valid_formats = ["Image", "Video", "Carousel", "Infographic"]
        if recommendation["recommended_format"] not in valid_formats:
            recommendation["recommended_format"] = "Video"  # Default to Video for better engagement
        
        # Agregar confidence score basado en el análisis
        recommendation["confidence_score"] = self._calculate_confidence_score(recommendation)
        
        # Asegurar que hay justificación
        if not recommendation["justification"]:
            recommendation["justification"] = f"Format {recommendation['recommended_format']} recommended to optimize engagement"
        
        return recommendation
    
    def _calculate_confidence_score(self, recommendation: Dict[str, Any]) -> float:
        """Calcula un score de confianza para la recomendación"""
        base_score = 0.7
        
        # Aumentar confianza si es video (mejor engagement)
        if recommendation["recommended_format"] == "Video":
            base_score += 0.2
        
        # Ajustar por complejidad de producción
        complexity = recommendation.get("production_complexity", "medium")
        if complexity == "low":
            base_score += 0.1
        elif complexity == "high":
            base_score -= 0.1
            
        return min(base_score, 1.0)
