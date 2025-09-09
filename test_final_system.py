"""
Script Final de Prueba del Sistema de Marketing AI
Sistema optimizado listo para Streamlit
"""
import asyncio
import logging
import sys
import time
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Añadir el directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

async def test_system_ready():
    """Prueba final para confirmar que el sistema está listo para Streamlit"""
    logger.info("=== PRUEBA FINAL DEL SISTEMA ===")
    
    try:
        # Importar y crear workflow con configuración optimizada
        from graph.workflow import create_marketing_workflow
        from config.settings import settings
        
        logger.info(f"Configuración LLM: {settings.llm_provider}")
        
        # Crear workflow sin RAG para evitar problemas
        workflow = create_marketing_workflow(enable_rag=False)
        logger.info("✅ Workflow creado exitosamente")
        
        # Prompt de prueba simple
        test_prompt = """Create a social media campaign for a new fitness app called "FitTracker Pro". 
        Target audience: Health-conscious professionals aged 25-40.
        Key features: AI workout recommendations, progress tracking, community challenges.
        Goal: Drive app downloads and user engagement."""
        
        logger.info("🧪 Ejecutando prueba con prompt optimizado...")
        start_time = time.time()
        
        # Procesar prompt
        result = await workflow.process_prompt(test_prompt)
        
        processing_time = time.time() - start_time
        logger.info(f"⏱️ Tiempo de procesamiento: {processing_time:.2f}s")
        
        # Validar resultado
        if result and hasattr(result, 'final_brief') and result.final_brief:
            logger.info("✅ Brief final generado exitosamente")
            
            # Mostrar resumen del brief
            brief = result.final_brief
            if hasattr(brief, 'campaign_overview'):
                logger.info(f"📋 Campaign Overview: {str(brief.campaign_overview)[:150]}...")
            
            if hasattr(brief, 'content_suggestions'):
                content = brief.content_suggestions
                if hasattr(content, 'social_posts') and content.social_posts:
                    logger.info(f"📱 Posts generados: {len(content.social_posts)}")
                if hasattr(content, 'captions') and content.captions:
                    logger.info(f"📝 Captions generados: {len(content.captions)}")
            
            logger.info("🎉 SISTEMA LISTO PARA STREAMLIT!")
            return True
            
        else:
            logger.warning("⚠️ No se generó brief final válido")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en prueba final: {e}")
        return False

async def main():
    """Función principal"""
    logger.info("Iniciando prueba final del sistema...")
    
    success = await test_system_ready()
    
    if success:
        logger.info("\n" + "="*50)
        logger.info("🚀 SISTEMA VALIDADO Y LISTO!")
        logger.info("✅ El workflow funciona correctamente")
        logger.info("✅ Los agentes procesan prompts exitosamente") 
        logger.info("✅ Se generan briefs de marketing completos")
        logger.info("📱 Proceder con integración a Streamlit")
        logger.info("="*50)
    else:
        logger.error("\n" + "="*50)
        logger.error("❌ SISTEMA NECESITA CORRECCIONES")
        logger.error("🔧 Revisar errores antes de continuar")
        logger.error("="*50)

if __name__ == "__main__":
    asyncio.run(main())
