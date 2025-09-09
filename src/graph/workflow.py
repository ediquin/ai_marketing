"""
Workflow de LangGraph para el sistema de marketing
"""
import logging
import time
from typing import Dict, Any
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models.content_brief import ContentBrief, ProcessingMetadata
from graph.state import WorkflowState, finalize_state
from agents.prompt_analyzer import PromptAnalyzer
from agents.post_classifier import PostClassifier
from agents.brand_voice_agent import BrandVoiceAgent
from agents.fact_grounding import FactGroundingAgent
from agents.text_generator import TextGenerator
from agents.caption_creator import CaptionCreator
from agents.visual_concept import VisualConceptAgent
from agents.reasoning_module import ReasoningModuleAgent
from agents.visual_format_recommender import VisualFormatRecommender
from agents.video_scripter import VideoScripter
from agents.result_optimizer import ResultOptimizer
from agents.contextual_awareness import ContextualAwarenessEngine
from tools.llm_client import create_llm_client

logger = logging.getLogger(__name__)

class MarketingWorkflow:
    """
    Workflow principal del sistema de marketing usando LangGraph
    """
    
    def __init__(self, use_realtime_data: bool = False, enable_rag: bool = True):
        self.llm_client = create_llm_client()
        self.use_realtime_data = use_realtime_data
        self.enable_rag = enable_rag
        self.agents = self._initialize_agents()
        self.graph = self._create_workflow()
        
        logger.info(f"Workflow de marketing inicializado (real-time: {use_realtime_data}, RAG: {enable_rag})")
    
    def _wrap_agent_process(self, agent_name: str):
        """Envuelve el proceso del agente para manejar la conversión de estado"""
        async def wrapped_process(state):
            # Convertir estado Pydantic a diccionario
            if hasattr(state, 'model_dump'):
                state_dict = state.model_dump()
            elif hasattr(state, 'dict'):
                state_dict = state.dict()
            else:
                state_dict = state
            
            # Ejecutar el agente
            result = await self.agents[agent_name].process(state_dict)
            
            # Convertir resultado de vuelta a WorkflowState
            if isinstance(result, dict):
                return WorkflowState(**result)
            return result
        
        return wrapped_process
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Inicializa todos los agentes del sistema"""
        return {
            "prompt_analyzer": PromptAnalyzer(self.llm_client),
            "post_classifier": PostClassifier(self.llm_client),
            "brand_voice_agent": BrandVoiceAgent(self.llm_client),
            "fact_grounding": FactGroundingAgent(self.llm_client),
            "text_generator": TextGenerator(self.llm_client),
            "caption_creator": CaptionCreator(self.llm_client),
            "visual_concept": VisualConceptAgent(self.llm_client),
            "reasoning_module": ReasoningModuleAgent(self.llm_client),
            "visual_format_recommender": VisualFormatRecommender(self.llm_client),
            "video_scripter": VideoScripter(self.llm_client),
            "result_optimizer": ResultOptimizer(self.llm_client, use_realtime_data=self.use_realtime_data, enable_rag=self.enable_rag),
            "contextual_awareness": ContextualAwarenessEngine(self.llm_client)
        }
    
    def _create_workflow(self) -> StateGraph:
        """Crea el workflow de LangGraph"""
        # Crear el grafo de estado
        workflow = StateGraph(WorkflowState)
        
        # Añadir todos los agentes como nodos
        workflow.add_node("prompt_analyzer", self._wrap_agent_process("prompt_analyzer"))
        workflow.add_node("post_classifier", self._wrap_agent_process("post_classifier"))
        workflow.add_node("brand_voice_agent", self._wrap_agent_process("brand_voice_agent"))
        workflow.add_node("fact_grounding", self._wrap_agent_process("fact_grounding"))
        workflow.add_node("text_generator", self._wrap_agent_process("text_generator"))
        workflow.add_node("caption_creator", self._wrap_agent_process("caption_creator"))
        workflow.add_node("visual_concept", self._wrap_agent_process("visual_concept"))
        workflow.add_node("reasoning_module", self._wrap_agent_process("reasoning_module"))
        workflow.add_node("visual_format_recommender", self._wrap_agent_process("visual_format_recommender"))
        workflow.add_node("video_scripter", self._wrap_agent_process("video_scripter"))
        workflow.add_node("result_optimizer", self._wrap_agent_process("result_optimizer"))
        workflow.add_node("contextual_awareness", self._wrap_agent_process("contextual_awareness"))
        
        # Nodo para finalizar el workflow
        workflow.add_node("finalize", self._finalize_workflow)
        
        # Configurar el punto de entrada
        workflow.set_entry_point("prompt_analyzer")
        
        # Configurar el flujo secuencial con nuevos agentes opcionales
        workflow.add_edge("prompt_analyzer", "post_classifier")
        workflow.add_edge("post_classifier", "brand_voice_agent")
        workflow.add_edge("brand_voice_agent", "fact_grounding")
        workflow.add_edge("fact_grounding", "text_generator")
        workflow.add_edge("text_generator", "caption_creator")
        workflow.add_edge("caption_creator", "visual_concept")
        workflow.add_edge("visual_concept", "reasoning_module")
        workflow.add_edge("reasoning_module", "visual_format_recommender")
        workflow.add_edge("visual_format_recommender", "video_scripter")
        workflow.add_edge("video_scripter", "result_optimizer")
        workflow.add_edge("result_optimizer", "contextual_awareness")
        workflow.add_edge("contextual_awareness", "finalize")
        
        # Configurar el final del workflow
        workflow.add_edge("finalize", END)
        
        # Compilar el workflow
        return workflow.compile()
    
    async def _finalize_workflow(self, state) -> Dict[str, Any]:
        """
        Finaliza el workflow y crea el brief final
        
        Args:
            state: Estado del workflow
            
        Returns:
            Estado finalizado
        """
        try:
            logger.info("Finalizando workflow y creando brief final")
            
            # Finalizar el estado
            final_state = finalize_state(state)
            
            # Crear metadatos de procesamiento
            if hasattr(final_state, 'processing_start') and final_state.processing_start and hasattr(final_state, 'processing_end') and final_state.processing_end:
                total_time = (final_state.processing_end - final_state.processing_start).total_seconds()
                
                # Actualizar metadatos con información del modelo
                if hasattr(final_state, 'final_brief') and final_state.final_brief and hasattr(final_state.final_brief, 'metadata') and final_state.final_brief.metadata:
                    final_state.final_brief.metadata.processing_time = total_time
                    final_state.final_brief.metadata.model_used = self.llm_client.__class__.__name__
                    final_state.final_brief.metadata.timestamp = final_state.processing_end
                    final_state.final_brief.metadata.version = "1.0.0"
            
            if 'total_time' in locals():
                logger.info(f"Workflow completado en {total_time:.2f}s")
            else:
                logger.info("Workflow completado")
            return final_state
            
        except Exception as e:
            logger.error(f"Error finalizando workflow: {e}")
            if isinstance(state, dict):
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append(f"[finalize]: {str(e)}")
                state["is_error"] = True
            else:
                if hasattr(state, 'errors'):
                    state.errors.append(f"[finalize]: {str(e)}")
                if hasattr(state, 'is_error'):
                    state.is_error = True
            return state
    
    async def process_prompt(self, input_prompt: str, language_config: dict = None) -> Dict[str, Any]:
        """
        Procesa un prompt de marketing completo
        
        Args:
            input_prompt: Prompt de entrada del usuario
            language_config: Configuración de idioma para las respuestas
            
        Returns:
            Estado final del workflow con el brief completo
        """
        try:
            logger.info(f"Iniciando procesamiento del prompt: {input_prompt[:100]}...")
            
            # Crear estado inicial con detección automática de idioma
            from graph.state import create_initial_state
            initial_state = create_initial_state(input_prompt)
            
            # Sobrescribir configuración de idioma si se proporciona explícitamente
            if language_config:
                initial_state.language_config = language_config
                logger.info(f"Configuración de idioma (manual): {language_config.get('language', 'auto')}")
            else:
                logger.info(f"Configuración de idioma (auto-detectado): {initial_state.language_config.get('language', 'auto')}")
            
            # Ejecutar el workflow
            logger.info("Ejecutando workflow de LangGraph")
            final_state = await self.graph.ainvoke(initial_state)
            
            # Verificar si hubo errores
            if hasattr(final_state, 'is_error') and final_state.is_error:
                logger.error("Workflow completado con errores")
                logger.error(f"Errores: {getattr(final_state, 'errors', [])}")
            else:
                logger.info("Workflow completado exitosamente")
                
                # Log de métricas
                if hasattr(final_state, 'final_brief') and final_state.final_brief and hasattr(final_state.final_brief, 'metadata') and final_state.final_brief.metadata:
                    metadata = final_state.final_brief.metadata
                    logger.info(f"Tiempo total: {metadata.processing_time:.2f}s")
                    logger.info(f"Modelo usado: {metadata.model_used}")
                    
                    # Log de tiempos por agente
                    for agent, timing in metadata.agent_timings.items():
                        logger.info(f"  {agent}: {timing:.2f}s")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Error en el workflow principal: {e}")
            # Crear estado de error
            error_state = WorkflowState(
                input_prompt=input_prompt,
                processing_start=datetime.now(),
                processing_end=datetime.now(),
                current_step="error",
                is_error=True,
                errors=[f"Error del workflow: {str(e)}"]
            )
            return error_state
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Obtiene el estado del workflow"""
        return {
            "status": "active",
            "agents": list(self.agents.keys()),
            "total_agents": len(self.agents),
            "llm_provider": self.llm_client.__class__.__name__
        }
    
    async def test_workflow(self, test_prompt: str = "Crear un post promocional para un nuevo producto de tecnología") -> Dict[str, Any]:
        """
        Ejecuta una prueba del workflow
        
        Args:
            test_prompt: Prompt de prueba
            
        Returns:
            Resultado de la prueba
        """
        try:
            logger.info("Ejecutando prueba del workflow")
            start_time = datetime.now()
            
            result = await self.process_prompt(test_prompt)
            
            end_time = datetime.now()
            test_duration = (end_time - start_time).total_seconds()
            
            test_result = {
                "success": not (hasattr(result, 'is_error') and result.is_error),
                "duration": test_duration,
                "has_final_brief": hasattr(result, 'final_brief') and result.final_brief is not None,
                "errors": getattr(result, 'errors', []),
                "warnings": getattr(result, 'warnings', [])
            }
            
            logger.info(f"Prueba del workflow completada: {test_result}")
            return test_result
            
        except Exception as e:
            logger.error(f"Error en prueba del workflow: {e}")
            return {
                "success": False,
                "duration": 0,
                "has_final_brief": False,
                "errors": [str(e)],
                "warnings": []
            }

# Función de conveniencia para crear el workflow
def create_marketing_workflow(enable_rag: bool = False) -> MarketingWorkflow:
    """Crea y retorna una instancia del workflow de marketing"""
    return MarketingWorkflow(enable_rag=enable_rag)

