"""
Script de Prueba Completa del Sistema de Marketing AI
Valida todos los componentes antes de usar Streamlit
Version simplificada para Windows
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
        logging.FileHandler('test_system.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

from graph.workflow import create_marketing_workflow
from config.settings import settings
from tools.marketing_rag_system import check_rag_dependencies

class SystemTester:
    """Clase para probar todo el sistema de marketing"""
    
    def __init__(self):
        self.workflow = None
        self.test_results = {}
        self.start_time = None
        
    async def initialize_system(self):
        """Inicializa el sistema de marketing"""
        logger.info("Inicializando Sistema de Marketing AI")
        logger.info(f"Configuracion: LLM Provider = {settings.llm_provider}")
        
        # Verificar dependencias RAG
        try:
            rag_deps = check_rag_dependencies()
            logger.info(f"Dependencias RAG: {rag_deps}")
        except Exception as e:
            logger.warning(f"Error verificando dependencias RAG: {e}")
        
        try:
            self.workflow = create_marketing_workflow()
            logger.info("Sistema inicializado correctamente")
            return True
        except Exception as e:
            logger.error(f"Error inicializando sistema: {e}")
            return False
    
    def get_test_prompts(self) -> List[Dict[str, Any]]:
        """Obtiene prompts de prueba en diferentes idiomas y tipos"""
        return [
            {
                "name": "B2B SaaS Launch (English)",
                "language": "en",
                "prompt": """Create a marketing campaign for launching our new AI-powered project management SaaS tool called "TaskFlow Pro". 
                Target audience: Mid-size companies (50-200 employees) looking to improve team productivity.
                Key features: AI task prioritization, automated reporting, team collaboration tools.
                Brand voice: Professional, innovative, trustworthy.
                Goal: Generate awareness and drive free trial signups.""",
                "expected_elements": ["professional tone", "B2B focus", "SaaS benefits", "call to action"]
            },
            {
                "name": "E-commerce Flash Sale (Spanish)",
                "language": "es", 
                "prompt": """Crear una campaña de marketing para una venta flash de 48 horas en nuestra tienda de ropa deportiva "FitStyle".
                Audiencia objetivo: Jóvenes de 18-35 años interesados en fitness y moda deportiva.
                Productos destacados: Zapatillas running, ropa de yoga, accesorios fitness.
                Voz de marca: Energética, motivacional, juvenil.
                Objetivo: Maximizar ventas durante el período de oferta.""",
                "expected_elements": ["tono energético", "urgencia", "productos específicos", "llamada a la acción"]
            }
        ]
    
    async def test_single_prompt(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba un prompt individual y valida la respuesta"""
        logger.info(f"Probando: {test_case['name']}")
        
        start_time = time.time()
        
        try:
            # Procesar el prompt
            result = await self.workflow.process_prompt(test_case['prompt'])
            
            processing_time = time.time() - start_time
            
            # Validar resultado
            validation = self.validate_result(result, test_case)
            
            test_result = {
                "name": test_case['name'],
                "language": test_case['language'],
                "success": validation['success'],
                "processing_time": processing_time,
                "validation": validation,
                "result_summary": self.summarize_result(result) if result else None,
                "error": None
            }
            
            if validation['success']:
                logger.info(f"EXITO: {test_case['name']} - Completado en {processing_time:.2f}s")
            else:
                logger.warning(f"PROBLEMAS: {test_case['name']} - Revisar issues")
                for issue in validation['issues']:
                    logger.warning(f"   - {issue}")
            
            return test_result
            
        except Exception as e:
            logger.error(f"ERROR: {test_case['name']} - {e}")
            return {
                "name": test_case['name'],
                "language": test_case['language'],
                "success": False,
                "processing_time": time.time() - start_time,
                "validation": {"success": False, "issues": [str(e)]},
                "result_summary": None,
                "error": str(e)
            }
    
    def validate_result(self, result: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Valida que el resultado cumpla con los requisitos esperados"""
        issues = []
        
        if not result:
            return {"success": False, "issues": ["No se obtuvo resultado"]}
        
        # Verificar que existe final_brief
        if 'final_brief' not in result:
            issues.append("No se encontro 'final_brief' en el resultado")
            return {"success": False, "issues": issues}
        
        brief = result['final_brief']
        
        # Verificar campos obligatorios del brief
        required_fields = ['campaign_overview', 'target_audience', 'key_messages', 'content_suggestions']
        for field in required_fields:
            if field not in brief or not brief[field]:
                issues.append(f"Campo obligatorio faltante o vacio: {field}")
        
        # Verificar que hay contenido generado
        if 'content_suggestions' in brief:
            content = brief['content_suggestions']
            if not any(content.get(key) for key in ['social_posts', 'captions', 'visual_concepts']):
                issues.append("No se genero contenido (posts, captions o conceptos visuales)")
        
        # Verificar longitud mínima del contenido
        if 'campaign_overview' in brief and len(str(brief['campaign_overview'])) < 50:
            issues.append("Campaign overview demasiado corto")
        
        return {
            "success": len(issues) == 0,
            "issues": issues,
            "score": max(0, 100 - len(issues) * 20)
        }
    
    def summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un resumen del resultado para análisis"""
        if not result or 'final_brief' not in result:
            return {"error": "No valid result to summarize"}
        
        brief = result['final_brief']
        
        summary = {
            "has_campaign_overview": bool(brief.get('campaign_overview')),
            "has_target_audience": bool(brief.get('target_audience')),
            "has_key_messages": bool(brief.get('key_messages')),
            "content_types_generated": [],
            "total_content_pieces": 0,
            "processing_metadata": brief.get('processing_metadata', {})
        }
        
        # Analizar contenido generado
        if 'content_suggestions' in brief:
            content = brief['content_suggestions']
            
            if content.get('social_posts'):
                summary['content_types_generated'].append('social_posts')
                summary['total_content_pieces'] += len(content['social_posts'])
            
            if content.get('captions'):
                summary['content_types_generated'].append('captions')
                summary['total_content_pieces'] += len(content['captions'])
            
            if content.get('visual_concepts'):
                summary['content_types_generated'].append('visual_concepts')
                summary['total_content_pieces'] += len(content['visual_concepts'])
        
        return summary
    
    async def run_comprehensive_test(self):
        """Ejecuta pruebas completas del sistema"""
        logger.info("Iniciando Pruebas Completas del Sistema")
        self.start_time = time.time()
        
        # 1. Inicializar sistema
        if not await self.initialize_system():
            logger.error("Fallo en inicializacion del sistema")
            return False
        
        # 2. Probar workflow básico
        logger.info("Probando workflow basico...")
        try:
            workflow_test = await self.workflow.test_workflow()
            if not workflow_test.get('success'):
                logger.error("Fallo en prueba basica del workflow")
                return False
        except Exception as e:
            logger.error(f"Error en prueba de workflow: {e}")
            return False
        
        # 3. Probar con diferentes prompts
        test_prompts = self.get_test_prompts()
        test_results = []
        
        for test_case in test_prompts:
            result = await self.test_single_prompt(test_case)
            test_results.append(result)
            
            # Pausa entre pruebas para evitar rate limiting
            await asyncio.sleep(2)
        
        # 4. Generar reporte final
        self.generate_final_report(test_results)
        
        return True
    
    def generate_final_report(self, test_results: List[Dict[str, Any]]):
        """Genera un reporte final de todas las pruebas"""
        total_time = time.time() - self.start_time
        successful_tests = sum(1 for r in test_results if r['success'])
        total_tests = len(test_results)
        
        logger.info("REPORTE FINAL DE PRUEBAS")
        logger.info("=" * 50)
        logger.info(f"Tiempo total de pruebas: {total_time:.2f}s")
        logger.info(f"Pruebas exitosas: {successful_tests}/{total_tests}")
        logger.info(f"Tasa de exito: {(successful_tests/total_tests)*100:.1f}%")
        
        # Detalles por prueba
        logger.info("Detalles por prueba:")
        for result in test_results:
            status = "EXITO" if result['success'] else "FALLO"
            logger.info(f"{status}: {result['name']} ({result['language']}) - {result['processing_time']:.2f}s")
            
            if not result['success'] and result['validation']['issues']:
                for issue in result['validation']['issues']:
                    logger.info(f"   PROBLEMA: {issue}")
        
        # Métricas de rendimiento
        processing_times = [r['processing_time'] for r in test_results if r['success']]
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            max_time = max(processing_times)
            min_time = min(processing_times)
            
            logger.info("Metricas de rendimiento:")
            logger.info(f"   Tiempo promedio: {avg_time:.2f}s")
            logger.info(f"   Tiempo maximo: {max_time:.2f}s")
            logger.info(f"   Tiempo minimo: {min_time:.2f}s")
        
        # Guardar reporte detallado
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_time": total_time,
            "success_rate": (successful_tests/total_tests)*100,
            "test_results": test_results,
            "system_config": {
                "llm_provider": settings.llm_provider,
                "model": getattr(settings, f"{settings.llm_provider}_model", "unknown")
            }
        }
        
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info("Reporte detallado guardado en: test_report.json")
        
        # Recomendaciones
        if successful_tests == total_tests:
            logger.info("EXCELENTE: Todas las pruebas pasaron! El sistema esta listo para Streamlit.")
        elif successful_tests >= total_tests * 0.75:
            logger.info("BUENO: La mayoria de pruebas pasaron. Revisar issues menores antes de Streamlit.")
        else:
            logger.info("ATENCION: Multiples fallas detectadas. Corregir problemas antes de continuar.")

async def main():
    """Función principal del script de pruebas"""
    tester = SystemTester()
    
    try:
        success = await tester.run_comprehensive_test()
        
        if success:
            logger.info("Pruebas completas finalizadas exitosamente")
            logger.info("El sistema esta listo para ser integrado con Streamlit")
        else:
            logger.error("Las pruebas fallaron. Revisar logs para mas detalles.")
            
    except KeyboardInterrupt:
        logger.info("Pruebas interrumpidas por el usuario")
    except Exception as e:
        logger.error(f"Error durante las pruebas: {e}")
        raise

if __name__ == "__main__":
    print("Sistema de Pruebas Completas - AI Marketing Strategist")
    print("=" * 60)
    print("Este script validara todo el sistema antes de usar Streamlit")
    print("Presiona Ctrl+C para cancelar en cualquier momento")
    print("=" * 60)
    
    asyncio.run(main())
