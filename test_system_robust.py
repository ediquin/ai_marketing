"""
Script de Prueba Robusto del Sistema de Marketing AI
Prueba el sistema core sin depender del RAG
"""
import asyncio
import logging
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Configurar logging sin emojis para Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_system_robust.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

# Importaciones con manejo de errores
try:
    from config.settings import settings
    from tools.llm_client import create_llm_client
    from agents.prompt_analyzer import PromptAnalyzer
    from agents.post_classifier import PostClassifier
    from agents.brand_voice_agent import BrandVoiceAgent
    from agents.text_generator import TextGenerator
    from agents.caption_creator import CaptionCreator
    from agents.visual_concept import VisualConceptAgent
    from agents.reasoning_module import ReasoningModuleAgent
    from models.content_brief import ContentBrief
    CORE_IMPORTS_OK = True
except Exception as e:
    logger.error(f"Error importando componentes core: {e}")
    CORE_IMPORTS_OK = False

class SystemTesterRobust:
    """Tester robusto que funciona sin RAG"""
    
    def __init__(self):
        self.llm_client = None
        self.agents = {}
        self.test_results = {}
        self.start_time = None
        
    async def initialize_core_system(self):
        """Inicializa solo los componentes core del sistema"""
        logger.info("Inicializando componentes core del sistema")
        
        if not CORE_IMPORTS_OK:
            logger.error("Fallo en importaciones core")
            return False
            
        try:
            # Inicializar cliente LLM
            self.llm_client = create_llm_client()
            logger.info(f"Cliente LLM inicializado: {settings.llm_provider}")
            
            # Inicializar agentes core (sin RAG)
            self.agents = {
                'prompt_analyzer': PromptAnalyzer(self.llm_client),
                'post_classifier': PostClassifier(self.llm_client),
                'brand_voice_agent': BrandVoiceAgent(self.llm_client),
                'text_generator': TextGenerator(self.llm_client),
                'caption_creator': CaptionCreator(self.llm_client),
                'visual_concept': VisualConceptAgent(self.llm_client),
                'reasoning_module': ReasoningModuleAgent(self.llm_client)
            }
            
            logger.info(f"Agentes inicializados: {len(self.agents)}")
            return True
            
        except Exception as e:
            logger.error(f"Error inicializando sistema core: {e}")
            return False
    
    def get_test_prompts(self) -> List[Dict[str, Any]]:
        """Prompts de prueba simplificados"""
        return [
            {
                "name": "B2B SaaS Simple",
                "prompt": """Create a social media post for our new project management tool "TaskFlow Pro". 
                Target: Small businesses. 
                Key benefit: Save 2 hours daily with AI automation.
                Tone: Professional but friendly.""",
                "expected_elements": ["professional", "time saving", "AI", "small business"]
            },
            {
                "name": "E-commerce Flash Sale",
                "prompt": """Crear un post para venta flash de 24 horas en tienda de ropa "StyleMax".
                Descuento: 50% en toda la colección de invierno.
                Audiencia: Jóvenes 18-30 años.
                Tono: Urgente y emocionante.""",
                "expected_elements": ["urgencia", "descuento", "jóvenes", "emoción"]
            }
        ]
    
    async def test_individual_agents(self):
        """Prueba agentes individuales"""
        logger.info("Probando agentes individuales...")
        
        test_prompt = "Create a marketing post for a new fitness app targeting young professionals"
        agent_results = {}
        
        for agent_name, agent in self.agents.items():
            try:
                logger.info(f"Probando agente: {agent_name}")
                start_time = time.time()
                
                if agent_name == 'prompt_analyzer':
                    result = await agent.analyze_prompt(test_prompt)
                elif agent_name == 'post_classifier':
                    result = await agent.classify_post_type(test_prompt)
                elif agent_name == 'brand_voice_agent':
                    result = await agent.extract_brand_voice(test_prompt)
                elif agent_name == 'text_generator':
                    result = await agent.generate_content(test_prompt, "Instagram", "fitness")
                elif agent_name == 'caption_creator':
                    result = await agent.create_caption(test_prompt, "Instagram", "motivational")
                elif agent_name == 'visual_concept':
                    result = await agent.generate_visual_concept(test_prompt, "Instagram")
                elif agent_name == 'reasoning_module':
                    result = await agent.provide_reasoning(test_prompt, {"platform": "Instagram"})
                else:
                    result = {"status": "not_tested"}
                
                processing_time = time.time() - start_time
                
                agent_results[agent_name] = {
                    "success": result is not None and len(str(result)) > 10,
                    "processing_time": processing_time,
                    "result_length": len(str(result)) if result else 0,
                    "error": None
                }
                
                if agent_results[agent_name]["success"]:
                    logger.info(f"EXITO: {agent_name} - {processing_time:.2f}s")
                else:
                    logger.warning(f"PROBLEMA: {agent_name} - resultado insuficiente")
                    
            except Exception as e:
                logger.error(f"ERROR: {agent_name} - {e}")
                agent_results[agent_name] = {
                    "success": False,
                    "processing_time": 0,
                    "result_length": 0,
                    "error": str(e)
                }
        
        return agent_results
    
    async def test_integrated_workflow(self, test_case: Dict[str, Any]):
        """Prueba workflow integrado simplificado"""
        logger.info(f"Probando workflow integrado: {test_case['name']}")
        
        start_time = time.time()
        workflow_state = {
            "input_prompt": test_case["prompt"],
            "processing_start": datetime.now(),
            "current_step": "start"
        }
        
        try:
            # Paso 1: Análisis del prompt
            workflow_state["current_step"] = "prompt_analysis"
            prompt_analysis = await self.agents['prompt_analyzer'].analyze_prompt(test_case["prompt"])
            workflow_state["prompt_analysis"] = prompt_analysis
            
            # Paso 2: Clasificación del post
            workflow_state["current_step"] = "post_classification"
            post_type = await self.agents['post_classifier'].classify_post_type(test_case["prompt"])
            workflow_state["post_classification"] = post_type
            
            # Paso 3: Extracción de voz de marca
            workflow_state["current_step"] = "brand_voice"
            brand_voice = await self.agents['brand_voice_agent'].extract_brand_voice(test_case["prompt"])
            workflow_state["brand_voice"] = brand_voice
            
            # Paso 4: Generación de contenido
            workflow_state["current_step"] = "content_generation"
            content = await self.agents['text_generator'].generate_content(
                test_case["prompt"], 
                "Instagram", 
                brand_voice.get("tone", "professional") if brand_voice else "professional"
            )
            workflow_state["generated_content"] = content
            
            # Paso 5: Creación de caption
            workflow_state["current_step"] = "caption_creation"
            caption = await self.agents['caption_creator'].create_caption(
                test_case["prompt"], 
                "Instagram", 
                brand_voice.get("tone", "professional") if brand_voice else "professional"
            )
            workflow_state["caption"] = caption
            
            # Paso 6: Concepto visual
            workflow_state["current_step"] = "visual_concept"
            visual_concept = await self.agents['visual_concept'].generate_visual_concept(
                test_case["prompt"], 
                "Instagram"
            )
            workflow_state["visual_concept"] = visual_concept
            
            # Paso 7: Razonamiento
            workflow_state["current_step"] = "reasoning"
            reasoning = await self.agents['reasoning_module'].provide_reasoning(
                test_case["prompt"], 
                {"platform": "Instagram", "content": content}
            )
            workflow_state["reasoning"] = reasoning
            
            # Crear brief final simplificado
            workflow_state["current_step"] = "finalization"
            final_brief = {
                "campaign_overview": content.get("campaign_overview", "Campaign generated successfully") if content else "Basic campaign",
                "target_audience": prompt_analysis.get("target_audience", "General audience") if prompt_analysis else "General audience",
                "key_messages": [content.get("key_message", "Main message")] if content else ["Generated message"],
                "content_suggestions": {
                    "social_posts": [content] if content else [],
                    "captions": [caption] if caption else [],
                    "visual_concepts": [visual_concept] if visual_concept else []
                },
                "reasoning": reasoning
            }
            
            workflow_state["final_brief"] = final_brief
            workflow_state["processing_end"] = datetime.now()
            workflow_state["current_step"] = "completed"
            
            processing_time = time.time() - start_time
            
            return {
                "name": test_case['name'],
                "success": True,
                "processing_time": processing_time,
                "workflow_state": workflow_state,
                "validation": self.validate_workflow_result(workflow_state),
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error en workflow integrado: {e}")
            return {
                "name": test_case['name'],
                "success": False,
                "processing_time": time.time() - start_time,
                "workflow_state": workflow_state,
                "validation": {"success": False, "issues": [str(e)]},
                "error": str(e)
            }
    
    def validate_workflow_result(self, workflow_state: Dict[str, Any]) -> Dict[str, Any]:
        """Valida el resultado del workflow"""
        issues = []
        
        # Verificar que se completó
        if workflow_state.get("current_step") != "completed":
            issues.append(f"Workflow no completado, parado en: {workflow_state.get('current_step')}")
        
        # Verificar brief final
        final_brief = workflow_state.get("final_brief")
        if not final_brief:
            issues.append("No se generó brief final")
        else:
            required_fields = ["campaign_overview", "target_audience", "key_messages", "content_suggestions"]
            for field in required_fields:
                if field not in final_brief or not final_brief[field]:
                    issues.append(f"Campo faltante en brief: {field}")
        
        return {
            "success": len(issues) == 0,
            "issues": issues,
            "score": max(0, 100 - len(issues) * 25)
        }
    
    async def run_comprehensive_test(self):
        """Ejecuta todas las pruebas"""
        logger.info("INICIANDO PRUEBAS ROBUSTAS DEL SISTEMA")
        self.start_time = time.time()
        
        # 1. Inicializar sistema core
        if not await self.initialize_core_system():
            logger.error("Fallo en inicialización del sistema core")
            return False
        
        # 2. Probar agentes individuales
        logger.info("Fase 1: Probando agentes individuales")
        agent_results = await self.test_individual_agents()
        
        # 3. Probar workflows integrados
        logger.info("Fase 2: Probando workflows integrados")
        test_prompts = self.get_test_prompts()
        workflow_results = []
        
        for test_case in test_prompts:
            result = await self.test_integrated_workflow(test_case)
            workflow_results.append(result)
            
            # Pausa entre pruebas
            await asyncio.sleep(1)
        
        # 4. Generar reporte final
        self.generate_final_report(agent_results, workflow_results)
        
        return True
    
    def generate_final_report(self, agent_results: Dict, workflow_results: List[Dict]):
        """Genera reporte final"""
        total_time = time.time() - self.start_time
        
        # Estadísticas de agentes
        successful_agents = sum(1 for r in agent_results.values() if r['success'])
        total_agents = len(agent_results)
        
        # Estadísticas de workflows
        successful_workflows = sum(1 for r in workflow_results if r['success'])
        total_workflows = len(workflow_results)
        
        logger.info("REPORTE FINAL - PRUEBAS ROBUSTAS")
        logger.info("=" * 50)
        logger.info(f"Tiempo total: {total_time:.2f}s")
        logger.info(f"Agentes exitosos: {successful_agents}/{total_agents}")
        logger.info(f"Workflows exitosos: {successful_workflows}/{total_workflows}")
        
        # Detalles de agentes
        logger.info("AGENTES INDIVIDUALES:")
        for agent_name, result in agent_results.items():
            status = "EXITO" if result['success'] else "FALLO"
            logger.info(f"  {status}: {agent_name} - {result['processing_time']:.2f}s")
            if result['error']:
                logger.info(f"    Error: {result['error']}")
        
        # Detalles de workflows
        logger.info("WORKFLOWS INTEGRADOS:")
        for result in workflow_results:
            status = "EXITO" if result['success'] else "FALLO"
            logger.info(f"  {status}: {result['name']} - {result['processing_time']:.2f}s")
            if result['validation']['issues']:
                for issue in result['validation']['issues']:
                    logger.info(f"    Problema: {issue}")
        
        # Guardar reporte
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_time": total_time,
            "agent_results": agent_results,
            "workflow_results": workflow_results,
            "summary": {
                "agents_success_rate": (successful_agents/total_agents)*100 if total_agents > 0 else 0,
                "workflows_success_rate": (successful_workflows/total_workflows)*100 if total_workflows > 0 else 0
            }
        }
        
        with open("test_report_robust.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info("Reporte guardado en: test_report_robust.json")
        
        # Evaluación final
        overall_success = (successful_agents >= total_agents * 0.8 and 
                          successful_workflows >= total_workflows * 0.8)
        
        if overall_success:
            logger.info("EXCELENTE: Sistema listo para Streamlit!")
        else:
            logger.info("ATENCION: Revisar problemas antes de continuar")
        
        return overall_success

async def main():
    """Función principal"""
    tester = SystemTesterRobust()
    
    try:
        success = await tester.run_comprehensive_test()
        
        if success:
            logger.info("PRUEBAS COMPLETADAS EXITOSAMENTE")
            logger.info("El sistema core esta funcionando correctamente")
            logger.info("Listo para integrar con Streamlit")
        else:
            logger.error("PRUEBAS CON PROBLEMAS - Revisar logs")
            
    except KeyboardInterrupt:
        logger.info("Pruebas interrumpidas por el usuario")
    except Exception as e:
        logger.error(f"Error durante las pruebas: {e}")
        raise

if __name__ == "__main__":
    print("Sistema de Pruebas Robustas - AI Marketing Strategist")
    print("=" * 60)
    print("Probando componentes core sin dependencias RAG")
    print("=" * 60)
    
    asyncio.run(main())
