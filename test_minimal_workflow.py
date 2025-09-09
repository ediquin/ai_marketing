#!/usr/bin/env python3
"""
Test mínimo del workflow sin timing para identificar el error
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graph.workflow import create_marketing_workflow
from graph.state import WorkflowState
from datetime import datetime

async def test_minimal_workflow():
    """Test mínimo sin timing complejo"""
    print("=" * 50)
    print("TEST MINIMO DEL WORKFLOW")
    print("=" * 50)
    
    try:
        # 1. Crear workflow
        print("1. Creando workflow...")
        workflow = create_marketing_workflow(enable_rag=True)
        print("   Workflow creado")
        
        # 2. Crear estado inicial simple
        print("2. Creando estado inicial...")
        initial_state = WorkflowState(
            input_prompt="Generate a launch post on LinkedIn for our new SaaS tool, 'Nexus Taskboard'. The goal is to drive product awareness and trial signups.",
            processing_start=datetime.now(),
            current_step="initialize",
            language_config={"language": "en", "auto_detected": "true"}
        )
        print("   Estado inicial creado")
        
        # 3. Ejecutar workflow usando LangGraph directamente
        print("3. Ejecutando workflow con LangGraph...")
        try:
            # El grafo ya está compilado
            result = await workflow.graph.ainvoke(initial_state)
            
            print(f"   Workflow ejecutado - Tipo: {type(result)}")
            
            # Verificar resultado
            print(f"   Resultado keys: {list(result.keys()) if isinstance(result, dict) else 'No dict'}")
            
            if isinstance(result, dict):
                final_brief = result.get('final_brief')
                errors = result.get('errors', [])
                
                print(f"   Final brief: {final_brief is not None}")
                print(f"   Errores: {errors}")
                
                # Verificar componentes
                components = ['post_type', 'core_content', 'engagement_elements', 'visual_concept', 'brand_voice', 'factual_grounding', 'reasoning']
                for comp in components:
                    value = result.get(comp)
                    print(f"   {comp}: {value is not None}")
                
                if final_brief:
                    print("   Final brief generado exitosamente")
                    return True
                else:
                    print("   Final brief no generado")
                    return False
            else:
                print("   Resultado no es dict")
                return False
                
        except Exception as e:
            print(f"   Error en ejecucion: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"ERROR GENERAL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    success = asyncio.run(test_minimal_workflow())
    
    print("\n" + "=" * 50)
    if success:
        print("WORKFLOW FUNCIONAL")
    else:
        print("WORKFLOW CON PROBLEMAS")
    print("=" * 50)

if __name__ == "__main__":
    main()
