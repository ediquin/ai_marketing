"""
Script de Prueba Directo del Workflow
Usa el workflow existente tal como está implementado
"""
import asyncio
import logging
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_workflow_direct.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

class WorkflowTester:
    """Tester que usa el workflow existente directamente"""
    
    def __init__(self):
        self.workflow = None
        self.test_results = []
        self.start_time = None
        
    async def initialize_workflow(self):
        """Inicializa el workflow usando la función existente"""
        logger.info("Inicializando workflow de marketing")
        
        try:
            from graph.workflow import create_marketing_workflow
            self.workflow = create_marketing_workflow(enable_rag=False)
            logger.info("Workflow inicializado correctamente (RAG deshabilitado)")
            return True
        except Exception as e:
            logger.error(f"Error inicializando workflow: {e}")
            return False
    
    def get_test_prompts(self) -> List[Dict[str, Any]]:
        """Prompts de prueba simples"""
        return [
            {
                "name": "Test Simple B2B",
                "prompt": "Create a LinkedIn post for our new project management software targeting small businesses. Highlight time-saving benefits and professional efficiency.",
                "language": "en"
            },
            {
                "name": "Test Simple E-commerce",
                "prompt": "Crear un post de Instagram para promocionar una venta flash de zapatos deportivos. Audiencia joven, tono energético.",
                "language": "es"
            }
        ]
    
    async def test_workflow_with_prompt(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba el workflow con un prompt específico"""
        logger.info(f"Probando workflow: {test_case['name']}")
        
        start_time = time.time()
        
        try:
            # Usar el método process_prompt del workflow
            result = await self.workflow.process_prompt(test_case["prompt"])
            
            processing_time = time.time() - start_time
            
            # Validar resultado básico
            success = (result is not None and 
                      isinstance(result, dict) and 
                      'final_brief' in result)
            
            test_result = {
                "name": test_case['name'],
                "language": test_case['language'],
                "success": success,
                "processing_time": processing_time,
                "has_final_brief": 'final_brief' in result if result else False,
                "result_keys": list(result.keys()) if result else [],
                "error": None
            }
            
            if success:
                logger.info(f"EXITO: {test_case['name']} - {processing_time:.2f}s")
                
                # Log detalles del brief si existe
                if result and 'final_brief' in result:
                    brief = result['final_brief']
                    if hasattr(brief, 'campaign_overview'):
                        logger.info(f"Brief generado con overview: {str(brief.campaign_overview)[:100]}...")
                    elif isinstance(brief, dict) and 'campaign_overview' in brief:
                        logger.info(f"Brief dict generado con overview: {str(brief['campaign_overview'])[:100]}...")
            else:
                logger.warning(f"PROBLEMA: {test_case['name']} - No se generó resultado válido")
            
            return test_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"ERROR: {test_case['name']} - {e}")
            
            return {
                "name": test_case['name'],
                "language": test_case['language'],
                "success": False,
                "processing_time": processing_time,
                "has_final_brief": False,
                "result_keys": [],
                "error": str(e)
            }
    
    async def test_workflow_basic_functionality(self):
        """Prueba funcionalidad básica del workflow"""
        logger.info("Probando funcionalidad básica del workflow")
        
        try:
            # Verificar que el workflow tiene los métodos esperados
            if not hasattr(self.workflow, 'process_prompt'):
                logger.error("Workflow no tiene método process_prompt")
                return False
            
            # Verificar estado del workflow
            if hasattr(self.workflow, 'get_workflow_status'):
                status = self.workflow.get_workflow_status()
                logger.info(f"Estado del workflow: {status}")
            
            # Probar método test_workflow si existe
            if hasattr(self.workflow, 'test_workflow'):
                logger.info("Ejecutando test interno del workflow")
                test_result = await self.workflow.test_workflow()
                logger.info(f"Resultado test interno: {test_result}")
                return test_result.get('success', False)
            
            return True
            
        except Exception as e:
            logger.error(f"Error en prueba básica: {e}")
            return False
    
    async def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        logger.info("INICIANDO PRUEBAS DIRECTAS DEL WORKFLOW")
        self.start_time = time.time()
        
        # 1. Inicializar workflow
        if not await self.initialize_workflow():
            logger.error("Fallo en inicialización del workflow")
            return False
        
        # 2. Probar funcionalidad básica
        logger.info("Fase 1: Probando funcionalidad básica")
        basic_test_passed = await self.test_workflow_basic_functionality()
        
        if not basic_test_passed:
            logger.warning("Prueba básica falló, continuando con pruebas de prompts")
        
        # 3. Probar con prompts reales
        logger.info("Fase 2: Probando con prompts reales")
        test_prompts = self.get_test_prompts()
        
        for test_case in test_prompts:
            result = await self.test_workflow_with_prompt(test_case)
            self.test_results.append(result)
            
            # Pausa entre pruebas
            await asyncio.sleep(2)
        
        # 4. Generar reporte
        self.generate_report()
        
        return True
    
    def generate_report(self):
        """Genera reporte final"""
        total_time = time.time() - self.start_time
        successful_tests = sum(1 for r in self.test_results if r['success'])
        total_tests = len(self.test_results)
        
        logger.info("REPORTE FINAL - PRUEBAS DIRECTAS DEL WORKFLOW")
        logger.info("=" * 55)
        logger.info(f"Tiempo total: {total_time:.2f}s")
        logger.info(f"Pruebas exitosas: {successful_tests}/{total_tests}")
        
        if total_tests > 0:
            success_rate = (successful_tests / total_tests) * 100
            logger.info(f"Tasa de éxito: {success_rate:.1f}%")
        
        # Detalles por prueba
        logger.info("DETALLES POR PRUEBA:")
        for result in self.test_results:
            status = "EXITO" if result['success'] else "FALLO"
            logger.info(f"  {status}: {result['name']} ({result['language']}) - {result['processing_time']:.2f}s")
            
            if result['success']:
                logger.info(f"    Brief generado: {'Sí' if result['has_final_brief'] else 'No'}")
                logger.info(f"    Claves resultado: {result['result_keys']}")
            else:
                logger.info(f"    Error: {result['error']}")
        
        # Métricas de rendimiento
        if successful_tests > 0:
            processing_times = [r['processing_time'] for r in self.test_results if r['success']]
            avg_time = sum(processing_times) / len(processing_times)
            logger.info(f"Tiempo promedio exitoso: {avg_time:.2f}s")
        
        # Guardar reporte
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_time": total_time,
            "success_rate": (successful_tests/total_tests)*100 if total_tests > 0 else 0,
            "test_results": self.test_results
        }
        
        try:
            with open("test_workflow_report.json", "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info("Reporte guardado en: test_workflow_report.json")
        except Exception as e:
            logger.error(f"Error guardando reporte: {e}")
        
        # Evaluación final
        if successful_tests == total_tests and total_tests > 0:
            logger.info("EXCELENTE: Todas las pruebas pasaron!")
            logger.info("El workflow está funcionando correctamente")
            logger.info("LISTO PARA STREAMLIT")
        elif successful_tests >= total_tests * 0.5:
            logger.info("PARCIAL: Algunas pruebas pasaron")
            logger.info("Revisar errores antes de continuar")
        else:
            logger.info("PROBLEMAS: Pocas o ninguna prueba pasó")
            logger.info("Necesita corrección antes de usar Streamlit")

async def main():
    """Función principal"""
    tester = WorkflowTester()
    
    try:
        success = await tester.run_all_tests()
        
        if success:
            logger.info("PRUEBAS COMPLETADAS")
        else:
            logger.error("PRUEBAS FALLARON EN INICIALIZACIÓN")
            
    except KeyboardInterrupt:
        logger.info("Pruebas interrumpidas por el usuario")
    except Exception as e:
        logger.error(f"Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Pruebas Directas del Workflow - AI Marketing Strategist")
    print("=" * 60)
    print("Probando el workflow tal como está implementado")
    print("=" * 60)
    
    asyncio.run(main())
