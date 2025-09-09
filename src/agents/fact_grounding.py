"""
Agente Fact Grounding - Valida y estructura hechos clave del prompt
"""
import logging
import time
from typing import Dict, Any

from src.models.content_brief import FactualGrounding
from src.tools.llm_client import LLMClient
from src.config.prompts import get_prompt_template, AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class FactGroundingAgent:
    """
    Agente que valida y estructura los hechos clave del prompt de marketing
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado y valida los hechos clave
        
        Args:
            state: Estado del workflow
            
        Returns:
            Estado actualizado con la base factual
        """
        start_time = time.time()
        
        try:
            self.logger.info("Iniciando validación de hechos clave")
            
            # Verificar que tenemos el análisis del prompt
            if not state.get("prompt_analysis"):
                raise ValueError("No hay análisis del prompt disponible")
            
            # 1. Preparar prompt específico según idioma
            language_config = state.get("language_config", {})
            language = language_config.get("language", "es")
            
            analysis = state["prompt_analysis"]
            if hasattr(analysis, 'key_facts'):
                key_facts = analysis.key_facts or []
            else:
                key_facts = analysis.get('key_facts', [])
            
            template = get_prompt_template(AGENT_TEMPLATES["fact_grounding"], language)
            prompt = template.format(
                prompt=state["input_prompt"],
                key_facts=", ".join(key_facts) if key_facts else "No specific facts identified"
            )
            
            # 2. Llamar al LLM
            self.logger.info("Generando base factual con LLM")
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con base factual"
            )
            
            # 3. Parsear respuesta
            self.logger.info("Parseando base factual del LLM")
            # El esquema minimal no define from_llm_response; construimos directamente
            # Aseguramos claves esperadas
            if isinstance(response, dict):
                safe_response = {
                    "key_facts": response.get("key_facts", []) or [],
                    "data_sources": response.get("data_sources", []) or [],
                    "verification_status": response.get("verification_status", "pending")
                }
                factual_grounding = FactualGrounding(**safe_response)
            else:
                factual_grounding = FactualGrounding(
                    key_facts=["Información del prompt analizada"],
                    data_sources=[],
                    verification_status="pending"
                )
            
            # 4. Validar output
            self.logger.info("Validando base factual generada")
            if not factual_grounding.key_facts:
                # Si no hay hechos, crear una base mínima
                factual_grounding.key_facts = ["Información del prompt analizada"]
                factual_grounding.verification_status = "pending"
            
            # 5. Actualizar estado
            state["factual_grounding"] = factual_grounding
            state["current_step"] = "text_generation"
            state["completed_steps"].append("fact_grounding")
            
            # 6. Log del proceso
            generation_time = time.time() - start_time
            self.logger.info(f"Base factual validada en {generation_time:.2f}s")
            self.logger.info(f"Hechos clave: {len(factual_grounding.key_facts)}")
            self.logger.info(f"Estado de verificación: {factual_grounding.verification_status}")
            
            # Registrar tiempo del agente
            state["agent_timings"]["fact_grounding"] = generation_time
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Error en FactGroundingAgent: {str(e)}"
            self.logger.error(error_msg)
            
            # Actualizar estado con error
            state["errors"].append(f"[fact_grounding]: {error_msg}")
            state["current_step"] = "error"
            state["is_error"] = True
            
            # Registrar tiempo del agente
            state["agent_timings"]["fact_grounding"] = generation_time
        
        return state
    
    async def validate_facts(self, prompt: str, key_facts: list) -> FactualGrounding:
        """
        Método auxiliar para validar hechos específicos
        
        Args:
            prompt: Prompt original
            key_facts: Lista de hechos a validar
            
        Returns:
            Base factual validada
        """
        try:
            user_prompt = prompt
            analysis_summary = ""
            prompt_text = f"""
            Analyze the following marketing prompt and extract key factual information that should be verified:
            
            PROMPT: {user_prompt}
            
            PREVIOUS ANALYSIS: {analysis_summary}
            
            Identify and validate:
            1. Specific facts about products/services
            2. Marketing claims that require verification
            3. Demographic data or mentioned statistics
            4. Technical information or specific features
            
            Respond in JSON format with this exact structure:
            {{
                "key_facts": [
                    {{"fact": "fact description", "category": "product|demographic|technical|claim", "verification_needed": true}}
                ],
                "data_sources": ["source1", "source2"],
                "statistics": [
                    {{"claim": "mentioned statistic", "source_needed": true}}
                ],
                "verification_status": "needs_verification"
            }}
            """
            
            response = await self.llm.generate_structured(
                prompt=prompt_text,
                expected_format="JSON con base factual"
            )
            
            return FactualGrounding(**response)
            
        except Exception as e:
            self.logger.error(f"Error validando hechos: {e}")
            raise
    
    def _extract_facts_from_text(self, text: str) -> list:
        """
        Extrae hechos básicos del texto (fallback si el LLM falla)
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de hechos extraídos
        """
        facts = []
        
        # Buscar números y fechas
        import re
        
        # Buscar fechas
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}\b'
        dates = re.findall(date_pattern, text)
        if dates:
            facts.extend([f"Fecha mencionada: {date}" for date in dates])
        
        # Buscar números
        number_pattern = r'\b\d+(?:\.\d+)?%\b|\b\d+(?:\.\d+)?\b'
        numbers = re.findall(number_pattern, text)
        if numbers:
            facts.extend([f"Número mencionado: {num}" for num in numbers[:3]])  # Limitar a 3
        
        # Buscar nombres propios (palabras con mayúscula)
        name_pattern = r'\b[A-Z][a-z]+\b'
        names = re.findall(name_pattern, text)
        if names:
            facts.extend([f"Nombre mencionado: {name}" for name in names[:3]])  # Limitar a 3
        
        return facts if facts else ["Información del prompt analizada"]

