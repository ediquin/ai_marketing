#!/usr/bin/env python3
"""
Test específico del sistema de fallback a modelos locales
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tools.llm_client import create_llm_client
from agents.prompt_analyzer import PromptAnalyzer

async def test_fallback_system():
    """Test del sistema de fallback automático"""
    print("=" * 60)
    print("TEST DEL SISTEMA DE FALLBACK AUTOMATICO")
    print("=" * 60)
    
    try:
        # Crear cliente con fallback
        print("1. Creando cliente LLM con fallback...")
        client = create_llm_client()
        print("   Cliente LLM creado exitosamente")
        
        # Test de generación simple
        print("\n2. Probando generación simple...")
        simple_prompt = "Write a short product announcement"
        start_time = time.time()
        response = await client.generate(simple_prompt, max_tokens=150)
        gen_time = time.time() - start_time
        
        print(f"   Tiempo: {gen_time:.2f}s")
        print(f"   Proveedor usado: {response.provider}")
        print(f"   Contenido: {response.content[:100]}...")
        
        # Test de generación estructurada
        print("\n3. Probando generación estructurada...")
        struct_prompt = "Analyze this marketing prompt and return JSON with 'campaign_type' and 'target_audience'"
        start_time = time.time()
        struct_response = await client.generate_structured(
            struct_prompt, 
            '{"campaign_type": "string", "target_audience": "string"}',
            max_tokens=200
        )
        struct_time = time.time() - start_time
        
        print(f"   Tiempo: {struct_time:.2f}s")
        print(f"   Respuesta estructurada: {struct_response}")
        
        # Test con agente real
        print("\n4. Probando con agente PromptAnalyzer...")
        analyzer = PromptAnalyzer(client)
        
        test_state = {
            "input_prompt": "Generate a launch post on LinkedIn for our new SaaS tool, 'Nexus Taskboard'. The goal is to drive product awareness and trial signups.",
            "language_config": {"language": "en", "auto_detected": True}
        }
        
        start_time = time.time()
        result_state = await analyzer.process(test_state)
        agent_time = time.time() - start_time
        
        print(f"   Tiempo del agente: {agent_time:.2f}s")
        
        if result_state.get("prompt_analysis"):
            analysis = result_state["prompt_analysis"]
            print(f"   Análisis generado exitosamente")
            print(f"   Tipo de campaña: {getattr(analysis, 'campaign_type', 'N/A')}")
            print(f"   Audiencia objetivo: {getattr(analysis, 'target_audience', 'N/A')}")
            return True
        else:
            print("   ERROR: No se generó análisis del prompt")
            return False
            
    except Exception as e:
        print(f"\nERROR en test de fallback: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_ollama_direct():
    """Test directo del modelo Ollama"""
    print("\n" + "=" * 60)
    print("TEST DIRECTO DE OLLAMA")
    print("=" * 60)
    
    try:
        from tools.llm_client import OllamaClient
        
        print("1. Creando cliente Ollama directo...")
        ollama_client = OllamaClient(model="llama3.1:8b")
        
        print("2. Probando generación directa...")
        test_prompt = "Write a brief marketing message for a new tech product"
        
        start_time = time.time()
        response = await ollama_client.generate(test_prompt, max_tokens=100)
        direct_time = time.time() - start_time
        
        print(f"   Tiempo: {direct_time:.2f}s")
        print(f"   Modelo: {response.model}")
        print(f"   Proveedor: {response.provider}")
        print(f"   Contenido: {response.content[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"\nERROR en test directo de Ollama: {str(e)}")
        return False

def main():
    """Función principal"""
    print("Iniciando tests del sistema de fallback...")
    
    # Test del sistema de fallback
    fallback_success = asyncio.run(test_fallback_system())
    
    # Test directo de Ollama
    ollama_success = asyncio.run(test_ollama_direct())
    
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    print(f"Sistema de fallback: {'EXITOSO' if fallback_success else 'FALLIDO'}")
    print(f"Ollama directo: {'EXITOSO' if ollama_success else 'FALLIDO'}")
    
    if fallback_success and ollama_success:
        print("\nTODOS LOS TESTS PASARON - Sistema de fallback funcionando")
    else:
        print("\nALGUNOS TESTS FALLARON - Revisar configuración")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
