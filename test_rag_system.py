"""
Test script para verificar que el sistema RAG funciona correctamente
"""

import sys
import os
sys.path.append('src')

from tools.marketing_rag_system import MarketingRAGSystem, check_rag_dependencies

def test_rag_dependencies():
    """Verifica que todas las dependencias RAG estén instaladas"""
    print("Verificando dependencias RAG...")
    deps = check_rag_dependencies()
    
    for dep, available in deps.items():
        status = "OK" if available else "FALTA"
        print(f"  {status} {dep}: {'Disponible' if available else 'No disponible'}")
    
    all_available = all(deps.values())
    print(f"\nEstado general: {'Todas las dependencias disponibles' if all_available else 'Faltan dependencias'}")
    return all_available

def test_rag_system():
    """Prueba el sistema RAG completo"""
    print("\nProbando sistema RAG...")
    
    try:
        # Inicializar sistema RAG
        rag_system = MarketingRAGSystem(enable_rag=True)
        print("OK Sistema RAG inicializado correctamente")
        
        # Probar consulta de benchmarks
        print("\nProbando consulta de benchmarks...")
        benchmarks = rag_system.query_performance_data(
            query="Instagram video engagement",
            platform="Instagram",
            industry="E-commerce"
        )
        
        if benchmarks:
            print(f"OK Encontrados {len(benchmarks)} benchmarks relevantes")
            for i, benchmark in enumerate(benchmarks[:2]):
                print(f"  Benchmark {i+1}: {benchmark.get('format', 'N/A')} - {benchmark.get('engagement_rate', 'N/A')}% engagement")
        else:
            print("ERROR No se encontraron benchmarks")
            return False
        
        # Probar contexto en tiempo real
        print("\nProbando contexto en tiempo real...")
        context = rag_system.get_real_time_context(
            brand_context="sustainable fashion",
            platform="Instagram",
            industry="fashion"
        )
        
        if context:
            print("OK Contexto obtenido correctamente")
            print(f"  Hashtags trending: {context.get('hashtags', [])[:3]}")
            print(f"  Temas trending: {len(context.get('trending_topics', []))} encontrados")
        else:
            print("ERROR obteniendo contexto")
            return False
        
        # Probar recomendación completa
        print("\nProbando recomendacion completa...")
        recommendation = rag_system.generate_enhanced_recommendation(
            prompt="Launch post for our new sustainable fashion line targeting Gen Z",
            platform="Instagram",
            industry="fashion",
            goal="brand_awareness"
        )
        
        if recommendation and not recommendation.get('error'):
            print("OK Recomendacion generada exitosamente")
            print(f"  Formato recomendado: {recommendation.get('recommended_format', 'N/A')}")
            print(f"  Confianza: {recommendation.get('expected_performance', {}).get('confidence', 'N/A')}")
            print(f"  RAG habilitado: {recommendation.get('rag_enabled', False)}")
        else:
            print(f"ERROR en recomendacion: {recommendation.get('error', 'Unknown error')}")
            return False
        
        print("\nTodas las pruebas del sistema RAG pasaron exitosamente!")
        return True
        
    except Exception as e:
        print(f"ERROR en sistema RAG: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("Iniciando pruebas del sistema RAG...")
    
    # Verificar dependencias
    deps_ok = test_rag_dependencies()
    
    if not deps_ok:
        print("\nNo se pueden ejecutar las pruebas RAG sin todas las dependencias")
        print("Instala con: pip install chromadb sentence-transformers duckduckgo-search")
        return False
    
    # Probar sistema RAG
    rag_ok = test_rag_system()
    
    if rag_ok:
        print("\nSistema RAG completamente funcional!")
        print("Ahora puedes usar el toggle 'Enable RAG System' en Streamlit")
        return True
    else:
        print("\nEl sistema RAG tiene problemas")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
