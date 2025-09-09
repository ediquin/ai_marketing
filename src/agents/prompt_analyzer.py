"""
Agente Prompt Analyzer - Extrae información estructurada del prompt de marketing
"""
import json
import logging
import time
from typing import Dict, Any

from src.models.content_brief import PromptAnalysis
from tools.llm_client import LLMClient
from config.prompts import get_prompt_template, AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class PromptAnalyzer:
    """
    Agente que analiza el prompt de marketing y extrae información estructurada
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado y actualiza con el análisis del prompt
        
        Args:
            state: Estado del workflow
            
        Returns:
            Estado actualizado con el análisis del prompt
        """
        start_time = time.time()
        
        try:
            self.logger.info("Iniciando análisis del prompt")
            
            # 1. Preparar prompt específico según idioma
            language_config = state.get("language_config", {})
            language = language_config.get("language", "es")
            
            template = get_prompt_template(AGENT_TEMPLATES["prompt_analyzer"], language)
            prompt = template.format(prompt=state["input_prompt"])
            
            # 2. Llamar al LLM
            self.logger.info("Generando análisis estructurado")
            response = await self.llm.generate_structured(
                prompt,
                expected_format="JSON con análisis del prompt",
                max_tokens=800,
                temperature=0.3
            )
            
            # Validar y normalizar la respuesta antes de crear el objeto
            if isinstance(response, dict):
                # Asegurar que todos los campos requeridos estén presentes
                required_fields = {
                    'objective': 'Increase brand awareness and engagement',
                    'audience': 'General target audience',
                    'brand_cues': ['professional', 'innovative'],
                    'key_facts': ['New product launch'],
                    'urgency': 'medium',
                    'platform': 'social_media',
                    'tone_indicators': ['engaging', 'informative'],
                    'content_goals': ['awareness', 'engagement']
                }
                
                # Completar campos faltantes con valores por defecto
                for field, default_value in required_fields.items():
                    if field not in response or response[field] is None:
                        response[field] = default_value
                        self.logger.warning(f"Campo {field} faltante, usando valor por defecto")
                
                # Asegurar que las listas no estén vacías
                for field in ['brand_cues', 'key_facts', 'tone_indicators', 'content_goals']:
                    if field in response and not response[field]:
                        response[field] = required_fields[field]
            
            # Crear objeto PromptAnalysis
            analysis = PromptAnalysis(**response)
            
            # 4. Validar output
            self.logger.info("Validando análisis generado")
            if not analysis.objective or not analysis.audience:
                raise ValueError("Análisis incompleto: faltan objetivo o audiencia")
            
            # 5. Actualizar estado
            state["prompt_analysis"] = analysis
            state["current_step"] = "post_classification"
            
            # Inicializar completed_steps si no existe
            if "completed_steps" not in state:
                state["completed_steps"] = []
            state["completed_steps"].append("prompt_analysis")
            
            # 6. Log del proceso
            generation_time = time.time() - start_time
            self.logger.info(f"Análisis del prompt completado en {generation_time:.2f}s")
            self.logger.info(f"Objetivo identificado: {analysis.objective}")
            self.logger.info(f"Audiencia identificada: {analysis.audience}")
            
            # Registrar tiempo del agente
            state["agent_timings"]["prompt_analyzer"] = generation_time
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Error en PromptAnalyzer: {str(e)}"
            self.logger.error(error_msg)
            
            # Inicializar listas de errores si no existen
            if "errors" not in state:
                state["errors"] = []
            if "agent_timings" not in state:
                state["agent_timings"] = {}
            
            # Actualizar estado con error
            state["errors"].append(f"[prompt_analyzer]: {error_msg}")
            state["current_step"] = "error"
            state["is_error"] = True
            
            # Registrar tiempo del agente
            state["agent_timings"]["prompt_analyzer"] = generation_time
        
        return state
    
    async def analyze_prompt(self, prompt: str) -> PromptAnalysis:
        """
        Método auxiliar para analizar un prompt específico
        
        Args:
            prompt: Prompt de marketing a analizar
            
        Returns:
            Análisis estructurado del prompt
        """
        try:
            formatted_prompt = PROMPT_ANALYZER_TEMPLATE.format(prompt=prompt)
            
            response = await self.llm.generate_structured(
                prompt=formatted_prompt,
                expected_format="JSON con análisis del prompt"
            )
            
            return PromptAnalysis(**response)
            
        except Exception as e:
            self.logger.error(f"Error analizando prompt: {e}")
            raise

