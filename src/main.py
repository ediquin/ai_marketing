"""
Sistema Agéntico de Marketing - Main Entry Point
"""
import asyncio
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('marketing_system.log')
    ]
)

logger = logging.getLogger(__name__)

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent))

from graph.workflow import create_marketing_workflow
from config.settings import settings

async def main():
    """Función principal del sistema"""
    try:
        logger.info("🚀 Iniciando Sistema Agéntico de Marketing")
        logger.info(f"Configuración: LLM Provider = {settings.llm_provider}")
        logger.info(f"Modelo objetivo: {settings.openai_model if settings.llm_provider == 'openai' else settings.anthropic_model}")
        
        # Crear el workflow
        logger.info("📋 Creando workflow de marketing...")
        workflow = create_marketing_workflow()
        
        # Mostrar estado del workflow
        status = workflow.get_workflow_status()
        logger.info(f"✅ Workflow creado exitosamente")
        logger.info(f"   Agentes: {status['total_agents']}")
        logger.info(f"   LLM Provider: {status['llm_provider']}")
        
        # Ejecutar prueba del workflow
        logger.info("🧪 Ejecutando prueba del workflow...")
        test_result = await workflow.test_workflow()
        
        if test_result['success']:
            logger.info("✅ Prueba del workflow exitosa")
            logger.info(f"   Duración: {test_result['duration']:.2f}s")
            logger.info(f"   Brief generado: {'Sí' if test_result['has_final_brief'] else 'No'}")
        else:
            logger.warning("⚠️ Prueba del workflow con advertencias")
            logger.warning(f"   Errores: {test_result['errors']}")
            logger.warning(f"   Advertencias: {test_result['warnings']}")
        
        # Ejemplo de uso
        logger.info("📝 Ejemplo de uso del sistema:")
        logger.info("   workflow = create_marketing_workflow()")
        logger.info("   result = await workflow.process_prompt('Tu prompt aquí')")
        logger.info("   brief = result['final_brief']")
        
        logger.info("🎉 Sistema inicializado correctamente")
        
        return workflow
        
    except Exception as e:
        logger.error(f"❌ Error inicializando el sistema: {e}")
        raise

def run_sync():
    """Ejecuta el sistema de forma síncrona"""
    try:
        return asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Sistema interrumpido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_sync()

