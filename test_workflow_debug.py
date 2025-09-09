#!/usr/bin/env python3
"""
Test de debug específico para identificar el error de 'time' en el workflow
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graph.workflow import create_marketing_workflow

async def test_workflow_step_by_step():
    """Test paso a paso del workflow para identificar el error"""
    print("=" * 60)
    print("DEBUG DEL WORKFLOW PASO A PASO")
    print("=" * 60)
    
    try:
        # 1. Crear workflow
        print("1. Creando workflow...")
        workflow = create_marketing_workflow(enable_rag=False)
        print("   Workflow creado exitosamente")
        
        # 2. Preparar estado inicial
        print("\n2. Preparando estado inicial...")
        initial_state = {
            "input_prompt": "Generate a launch post on LinkedIn for our new SaaS tool, 'Nexus Taskboard'. The goal is to drive product awareness and trial signups.",
            "language_config": {"language": "en", "auto_detected": True},
            "processing_start": time.time(),
            "agent_timings": {},
            "completed_steps": [],
            "errors": [],
            "warnings": [],
            "current_step": "prompt_analysis",
            "is_complete": False,
            "is_error": False
        }
        print("   Estado inicial preparado")
        
        # 3. Test de agentes individuales
        print("\n3. Probando agentes individuales...")
        
        # Test PromptAnalyzer
        try:
            print("   3.1 Probando PromptAnalyzer...")
            analyzer = workflow.agents["prompt_analyzer"]
            state_after_analyzer = await analyzer.process(initial_state.copy())
            print(f"       PromptAnalyzer: {'EXITOSO' if 'prompt_analysis' in state_after_analyzer else 'FALLIDO'}")
        except Exception as e:
            print(f"       PromptAnalyzer: ERROR - {str(e)}")
            return False
        
        # Test PostClassifier
        try:
            print("   3.2 Probando PostClassifier...")
            classifier = workflow.agents["post_classifier"]
            state_after_classifier = await classifier.process(state_after_analyzer.copy())
            print(f"       PostClassifier: {'EXITOSO' if 'post_type' in state_after_classifier else 'FALLIDO'}")
        except Exception as e:
            print(f"       PostClassifier: ERROR - {str(e)}")
        
        # 4. Test del workflow completo
        print("\n4. Probando workflow completo...")
        try:
            start_time = time.time()
            result = await workflow.process_prompt(initial_state["input_prompt"])
            processing_time = time.time() - start_time
            
            print(f"   Tiempo total: {processing_time:.2f}s")
            print(f"   Tipo de resultado: {type(result)}")
            
            if hasattr(result, 'final_brief') and result.final_brief:
                print("   Final brief: PRESENTE")
                return True
            else:
                print("   Final brief: AUSENTE")
                if hasattr(result, 'errors') and result.errors:
                    print(f"   Errores: {result.errors}")
                return False
                
        except Exception as e:
            print(f"   Workflow completo: ERROR - {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"\nERROR GENERAL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("Iniciando debug del workflow...")
    
    success = asyncio.run(test_workflow_step_by_step())
    
    print("\n" + "=" * 60)
    if success:
        print("WORKFLOW FUNCIONANDO CORRECTAMENTE")
    else:
        print("WORKFLOW TIENE PROBLEMAS - REVISAR LOGS")
    print("=" * 60)

if __name__ == "__main__":
    main()
