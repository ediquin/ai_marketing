#!/usr/bin/env python3
"""
Comprehensive System Test Script
Tests the complete AI Marketing Strategist workflow end-to-end
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.graph.workflow import MarketingWorkflow
from src.config.settings import get_settings
from src.tools.marketing_rag_system import check_rag_dependencies

def print_separator(title=""):
    """Print a clean separator"""
    print("\n" + "="*60)
    if title:
        print(f" {title}")
        print("="*60)

def print_subsection(title):
    """Print subsection header"""
    print(f"\n--- {title} ---")

async def test_system_dependencies():
    """Test all system dependencies"""
    print_separator("SYSTEM DEPENDENCIES CHECK")
    
    # Test settings loading
    try:
        settings = get_settings()
        print("OK Settings loaded successfully")
    except Exception as e:
        print(f"ERROR Settings loading failed: {e}")
        return False
    
    # Test RAG dependencies
    try:
        rag_available = check_rag_dependencies()
        if rag_available:
            print("OK RAG system dependencies available")
        else:
            print("WARNING RAG system dependencies missing (will use fallback)")
    except Exception as e:
        print(f"WARNING RAG dependency check failed: {e}")
    
    return True

async def test_workflow_initialization():
    """Test workflow initialization"""
    print_separator("WORKFLOW INITIALIZATION")
    
    try:
        workflow = MarketingWorkflow()
        print("OK Workflow initialized successfully")
        
        # Test graph compilation
        graph = workflow.create_graph()
        print("OK Graph compiled successfully")
        
        return workflow, graph
    except Exception as e:
        print(f"ERROR Workflow initialization failed: {e}")
        return None, None

async def test_spanish_prompt():
    """Test with Spanish marketing prompt"""
    print_separator("SPANISH PROMPT TEST")
    
    spanish_prompt = """
    Necesito crear contenido para el lanzamiento de mi nueva app de fitness "FitTracker Pro".
    
    Detalles del producto:
    - App móvil para seguimiento de ejercicios y nutrición
    - Dirigida a personas de 25-45 años que buscan un estilo de vida saludable
    - Características: planes personalizados, seguimiento de progreso, comunidad social
    - Precio: $9.99/mes con prueba gratuita de 7 días
    - Lanzamiento: próximo mes
    
    Tono de marca: Motivacional, accesible, profesional pero amigable
    
    Quiero crear posts para Instagram que generen expectativa sobre el lanzamiento.
    """
    
    try:
        workflow = MarketingWorkflow()
        graph = workflow.create_graph()
        
        print("Testing Spanish prompt...")
        print(f"Input: {spanish_prompt[:100]}...")
        
        start_time = time.time()
        result = await graph.ainvoke({
            "input_prompt": spanish_prompt,
            "enable_rag": True,
            "enable_real_time": False  # Disable for testing
        })
        processing_time = time.time() - start_time
        
        print(f"Processing time: {processing_time:.2f} seconds")
        
        # Check results
        if result.get("final_content"):
            print("OK Content generated successfully")
            print(f"Generated content length: {len(result['final_content'])} characters")
        else:
            print("ERROR No content generated")
            return False
            
        if result.get("visual_concept"):
            print("OK Visual concept generated")
        else:
            print("WARNING No visual concept generated")
            
        if result.get("reasoning"):
            print("OK Reasoning provided")
        else:
            print("WARNING No reasoning provided")
            
        return True
        
    except Exception as e:
        print(f"ERROR Spanish prompt test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_english_prompt():
    """Test with English marketing prompt"""
    print_separator("ENGLISH PROMPT TEST")
    
    english_prompt = """
    I need to create marketing content for my new SaaS product "CloudSync Pro".
    
    Product details:
    - Cloud storage and file synchronization service
    - Target audience: Small to medium businesses (10-100 employees)
    - Features: Real-time sync, team collaboration, advanced security
    - Pricing: $15/user/month with 30-day free trial
    - Launch: Next quarter
    
    Brand voice: Professional, trustworthy, innovative, solution-focused
    
    I want to create LinkedIn posts that highlight the business benefits and drive trial signups.
    """
    
    try:
        workflow = MarketingWorkflow()
        graph = workflow.create_graph()
        
        print("Testing English prompt...")
        print(f"Input: {english_prompt[:100]}...")
        
        start_time = time.time()
        result = await graph.ainvoke({
            "input_prompt": english_prompt,
            "enable_rag": True,
            "enable_real_time": False  # Disable for testing
        })
        processing_time = time.time() - start_time
        
        print(f"Processing time: {processing_time:.2f} seconds")
        
        # Check results
        if result.get("final_content"):
            print("OK Content generated successfully")
            print(f"Generated content length: {len(result['final_content'])} characters")
        else:
            print("ERROR No content generated")
            return False
            
        if result.get("visual_concept"):
            print("OK Visual concept generated")
        else:
            print("WARNING No visual concept generated")
            
        if result.get("reasoning"):
            print("OK Reasoning provided")
        else:
            print("WARNING No reasoning provided")
            
        return True
        
    except Exception as e:
        print(f"ERROR English prompt test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_rag_system():
    """Test RAG system functionality"""
    print_separator("RAG SYSTEM TEST")
    
    try:
        from src.tools.marketing_rag_system import MarketingRAGSystem
        
        rag_system = MarketingRAGSystem()
        
        # Test benchmark query
        print("Testing benchmark query...")
        benchmarks = await rag_system.query_benchmarks("social media engagement rates")
        if benchmarks:
            print(f"OK Retrieved {len(benchmarks)} benchmark results")
        else:
            print("WARNING No benchmarks retrieved")
        
        # Test real-time context (disabled for testing)
        print("Testing real-time context...")
        context = await rag_system.get_real_time_context("fitness app marketing", max_results=3)
        if context:
            print(f"OK Retrieved real-time context: {len(context)} items")
        else:
            print("WARNING No real-time context retrieved")
            
        return True
        
    except Exception as e:
        print(f"ERROR RAG system test failed: {e}")
        return False

async def test_agent_performance():
    """Test individual agent performance"""
    print_separator("AGENT PERFORMANCE TEST")
    
    try:
        workflow = MarketingWorkflow()
        
        # Test a simple prompt through each major agent
        test_prompt = "Create a social media post for a new coffee shop opening."
        
        # Initialize state
        state = {
            "input_prompt": test_prompt,
            "enable_rag": False,
            "enable_real_time": False
        }
        
        # Test prompt analyzer
        print_subsection("Prompt Analyzer")
        start_time = time.time()
        state = await workflow.prompt_analyzer.process(state)
        print(f"OK Completed in {time.time() - start_time:.2f}s")
        
        # Test post classifier
        print_subsection("Post Classifier")
        start_time = time.time()
        state = await workflow.post_classifier.process(state)
        print(f"OK Completed in {time.time() - start_time:.2f}s")
        
        # Test brand voice agent
        print_subsection("Brand Voice Agent")
        start_time = time.time()
        state = await workflow.brand_voice_agent.process(state)
        print(f"OK Completed in {time.time() - start_time:.2f}s")
        
        print("All core agents functioning correctly")
        return True
        
    except Exception as e:
        print(f"ERROR Agent performance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_comprehensive_test():
    """Run all tests"""
    print_separator("AI MARKETING STRATEGIST - COMPREHENSIVE TEST")
    print("Testing complete system functionality...")
    
    results = {}
    
    # Test 1: Dependencies
    results["dependencies"] = await test_system_dependencies()
    
    # Test 2: Workflow initialization
    workflow, graph = await test_workflow_initialization()
    results["workflow_init"] = workflow is not None
    
    if not workflow:
        print("\nERROR: Cannot continue without workflow initialization")
        return results
    
    # Test 3: Agent performance
    results["agent_performance"] = await test_agent_performance()
    
    # Test 4: RAG system
    results["rag_system"] = await test_rag_system()
    
    # Test 5: Spanish prompt
    results["spanish_prompt"] = await test_spanish_prompt()
    
    # Test 6: English prompt
    results["english_prompt"] = await test_english_prompt()
    
    # Summary
    print_separator("TEST RESULTS SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSUCCESS: All tests passed! System is ready for Streamlit deployment.")
    elif passed >= total * 0.8:
        print("\nWARNING: Most tests passed. System should work but may have minor issues.")
    else:
        print("\nERROR: Multiple test failures. System needs debugging before deployment.")
    
    return results

if __name__ == "__main__":
    # Run the comprehensive test
    try:
        results = asyncio.run(run_comprehensive_test())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
