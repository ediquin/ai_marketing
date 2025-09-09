#!/usr/bin/env python3
"""
Script de validación rápida del sistema de marketing
Evita Streamlit para debugging más directo
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from graph.workflow import create_marketing_workflow

async def test_marketing_system():
    """Test rápido del sistema completo"""
    print("Iniciando validacion del sistema de marketing...")
    
    # Prompts de prueba
    test_prompts = [
        "Generate a launch post on LinkedIn for our new SaaS tool, 'Nexus Taskboard'. The goal is to drive product awareness and trial signups.",
        "Create a social media campaign for a local restaurant's new vegan menu launch",
        "Develop content for a flash sale announcement for an e-commerce fashion brand"
    ]
    
    try:
        # Crear workflow con RAG deshabilitado
        print("Creando workflow de marketing...")
        workflow = create_marketing_workflow(
            enable_rag=False
        )
        
        if not workflow:
            print("Error: No se pudo crear el workflow")
            return False
            
        print("Workflow creado exitosamente")
        
        # Probar con el primer prompt
        prompt = test_prompts[0]
        print(f"\nProbando prompt: {prompt[:50]}...")
        
        start_time = time.time()
        result = await workflow.process_prompt(prompt)
        processing_time = time.time() - start_time
        
        print(f"Tiempo de procesamiento: {processing_time:.2f}s")
        
        # Verificar resultado
        if result:
            print(f"Resultado obtenido - Tipo: {type(result)}")
            
            # Verificar atributos del resultado
            if hasattr(result, '__dict__'):
                attrs = list(result.__dict__.keys())
                print(f"Atributos disponibles: {attrs}")
                
                # Verificar si tiene final_brief
                if hasattr(result, 'final_brief') and result.final_brief:
                    brief = result.final_brief
                    print("Final brief encontrado")
                    
                    # Verificar componentes del brief
                    if hasattr(brief, 'core_content') and brief.core_content:
                        print(f"Core content: {brief.core_content[:100]}...")
                    
                    if hasattr(brief, 'captions') and brief.captions:
                        print(f"Captions generados: {len(brief.captions)}")
                    
                    if hasattr(brief, 'visual_concepts') and brief.visual_concepts:
                        print(f"Conceptos visuales: {len(brief.visual_concepts)}")
                        
                    return True
                else:
                    print("No se encontro final_brief en el resultado")
                    return False
            else:
                print("Resultado no tiene atributos esperados")
                return False
        else:
            print("No se obtuvo resultado del workflow")
            return False
            
    except Exception as e:
        print(f"Error durante la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_individual_components():
    """Test de componentes individuales"""
    print("\nProbando componentes individuales...")
    
    try:
        # Test del cliente LLM
        from tools.llm_client import create_llm_client
        
        client = create_llm_client()
        print("Cliente LLM inicializado")
        
        # Test simple de generación
        test_prompt = "Generate a short marketing message for a new product"
        response = await client.generate(test_prompt, max_tokens=100)
        
        if response:
            print(f"Generacion de texto exitosa: {response.content[:50]}...")
            print(f"Proveedor usado: {response.provider}")
            return True
        else:
            print("No se pudo generar texto")
            return False
            
    except Exception as e:
        print(f"Error en test de componentes: {str(e)}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("VALIDACION RAPIDA DEL SISTEMA DE MARKETING")
    print("=" * 60)
    
    # Test del sistema completo
    success = asyncio.run(test_marketing_system())
    
    if not success:
        print("\nProbando componentes individuales...")
        component_success = asyncio.run(test_individual_components())
        
        if component_success:
            print("\nComponentes individuales funcionan - problema en workflow")
        else:
            print("\nProblemas en componentes basicos")
    
    print("\n" + "=" * 60)
    if success:
        print("SISTEMA VALIDADO EXITOSAMENTE")
    else:
        print("SISTEMA REQUIERE CORRECCIONES")
    print("=" * 60)

if __name__ == "__main__":
    main()
