"""
Video Scripter - Crea scripts estructurados para videos de formato corto
"""
import logging
import time
from typing import Dict, Any

from tools.llm_client import LLMClient
from config.prompts import get_prompt_template, AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class VideoScripter:
    """
    Agente que crea scripts estructurados para videos de formato corto (Reels, TikTok, Shorts)
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado y crea un script de video estructurado
        
        Args:
            state: Estado del workflow con análisis previo
            
        Returns:
            Estado actualizado con script de video
        """
        start_time = time.time()
        
        try:
            self.logger.info("Iniciando creación de script de video")
            
            # Get platform info early
            platform = getattr(state.get("prompt_analysis"), 'platform', 'Instagram') if state.get("prompt_analysis") else 'Instagram'
            
            # Verificar si se recomienda formato de video
            visual_format = state.get("visual_format_recommendation", {})
            recommended_format = visual_format.get("recommended_format", "Image")
            
            # Check if format supports video (more flexible check)
            video_formats = ["video", "reel", "tiktok", "short-form video", "instagram reel", "youtube short"]
            if not any(fmt in recommended_format.lower() for fmt in video_formats):
                self.logger.info(f"Formato '{recommended_format}' no es compatible con video, creando script básico")
                # Create a basic video script anyway for demonstration
                basic_script = {
                    "script_segments": [
                        {
                            "timestamp": "0-3s",
                            "narration": "Hook: Attention-grabbing opening",
                            "visual_cue": "Dynamic opening shot"
                        },
                        {
                            "timestamp": "3-10s", 
                            "narration": "Main content presentation",
                            "visual_cue": "Product/service showcase"
                        },
                        {
                            "timestamp": "10-15s",
                            "narration": "Call to action",
                            "visual_cue": "Clear CTA visual"
                        }
                    ],
                    "total_duration": "15 seconds",
                    "music_style": "Upbeat and engaging",
                    "platform_optimized": platform
                }
                
                # Actualizar estado usando función de estado
                from graph.state import update_state_with_video_script, WorkflowState
                if isinstance(state, dict):
                    workflow_state = WorkflowState(**state)
                    workflow_state = update_state_with_video_script(workflow_state, basic_script)
                    state.update(workflow_state.dict())
                else:
                    state = update_state_with_video_script(state, basic_script)
                
                # Registrar tiempo del agente
                processing_time = time.time() - start_time
                if isinstance(state, dict):
                    if "agent_timings" not in state:
                        state["agent_timings"] = {}
                    state["agent_timings"]["video_scripter"] = processing_time
                else:
                    if not hasattr(state, 'agent_timings'):
                        state.agent_timings = {}
                    state.agent_timings["video_scripter"] = processing_time
                
                return state
            else:
                self.logger.info(f"Formato '{recommended_format}' es compatible con video, generando script completo")
                
                # Verificar elementos necesarios
                required_elements = ["core_content", "prompt_analysis"]
                for element in required_elements:
                    if not state.get(element):
                        raise ValueError(f"Elemento requerido no disponible: {element}")
                
                # Preparar prompt específico según idioma
                language_config = state.get("language_config", {})
                language = language_config.get("language", "es")
                
                core_content = state["core_content"]
                platform = getattr(state["prompt_analysis"], 'platform', 'Instagram')
                duration = self._determine_duration(platform)
                
                template = get_prompt_template(AGENT_TEMPLATES["video_scripter"], language)
                prompt = template.format(
                    core_content=core_content,
                    visual_format=recommended_format,
                    platform=platform,
                    duration=duration
                )
                
                # Llamar al LLM
                self.logger.info("Generando script de video con LLM")
                response = await self.llm.generate_structured(
                    prompt=prompt,
                    expected_format="JSON con script de video"
                )
                
                # Parsear respuesta
                self.logger.info("Parseando script de video")
                video_script = self._parse_video_script(response)
            
            # Validar y mejorar script
            video_script = self._validate_and_enhance_script(video_script, platform)
            
            # Actualizar estado usando función de estado
            from graph.state import update_state_with_video_script, WorkflowState
            if isinstance(state, dict):
                workflow_state = WorkflowState(**state)
                workflow_state = update_state_with_video_script(workflow_state, video_script)
                state.update(workflow_state.dict())
            else:
                state = update_state_with_video_script(state, video_script)
            
            # Log del proceso
            processing_time = time.time() - start_time
            self.logger.info(f"Script de video generado en {processing_time:.2f}s")
            
            # Registrar tiempo del agente
            if isinstance(state, dict):
                if "agent_timings" not in state:
                    state["agent_timings"] = {}
                state["agent_timings"]["video_scripter"] = processing_time
            else:
                if not hasattr(state, 'agent_timings'):
                    state.agent_timings = {}
                state.agent_timings["video_scripter"] = processing_time
            
            return state
            
        except Exception as e:
            error_msg = f"Error en Video Scripter: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
            return state
    
    def _determine_duration(self, platform: str) -> str:
        """Determina la duración objetivo según la plataforma"""
        platform_durations = {
            "tiktok": "15-30s",
            "instagram": "15-30s", 
            "youtube": "30-60s",
            "linkedin": "30-60s",
            "twitter": "15-30s"
        }
        return platform_durations.get(platform.lower(), "15-30s")
    
    def _parse_video_script(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea la respuesta del LLM"""
        return {
            "script_segments": response.get("script_segments", []),
            "engagement_elements": response.get("engagement_elements", []),
            "music_style": response.get("music_style", "upbeat"),
            "hashtags": response.get("hashtags", []),
            "total_duration": self._calculate_total_duration(response.get("script_segments", [])),
            "production_notes": response.get("production_notes", "")
        }
    
    def _calculate_total_duration(self, segments: list) -> str:
        """Calcula la duración total del script"""
        if not segments:
            return "30s"
        
        # Extraer duración del último segmento
        last_segment = segments[-1] if segments else {}
        duration = last_segment.get("duration", "30s")
        
        # Extraer el número final
        if "-" in duration:
            return duration.split("-")[-1]
        return duration
    
    def _validate_and_enhance_script(self, script: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Valida y mejora el script"""
        # Asegurar que hay segmentos
        if not script["script_segments"]:
            script["script_segments"] = [
                {
                    "segment": "hook",
                    "duration": "0-3s",
                    "narration": "¡Atención! Descubre algo increíble...",
                    "visual_direction": "Close-up del producto",
                    "text_overlay": "¿Sabías que...?"
                }
            ]
        
        # Validar elementos de engagement
        if not script["engagement_elements"]:
            script["engagement_elements"] = ["Pregunta al inicio", "Call to action claro"]
        
        # Agregar hashtags específicos de plataforma
        platform_hashtags = {
            "tiktok": ["#FYP", "#Viral"],
            "instagram": ["#Reels", "#Trending"],
            "youtube": ["#Shorts", "#YouTube"],
            "linkedin": ["#Professional", "#Business"]
        }
        
        platform_specific = platform_hashtags.get(platform.lower(), [])
        script["hashtags"].extend(platform_specific)
        
        return script
