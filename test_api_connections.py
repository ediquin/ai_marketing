"""
Test script para verificar conexiones API y configuración de fallback
"""
import os
import sys
import asyncio
from pathlib import Path

# Añadir src al path
sys.path.append(str(Path(__file__).parent / "src"))

from tools.llm_client import GoogleAIClient, GroqClient
from config.settings import get_settings

async def test_google_ai():
    """Test Google AI (Gemini) connection"""
    settings = get_settings()
    
    if not settings.google_api_key:
        print("ERROR Google AI: No API key configured")
        return False
    
    try:
        client = GoogleAIClient(settings.google_api_key, settings.google_model)
        response = await client.generate("Test prompt: Say 'Hello from Gemini'")
        print(f"OK Google AI ({settings.google_model}): {response.content[:50]}...")
        return True
    except Exception as e:
        print(f"ERROR Google AI: {e}")
        return False

async def test_groq():
    """Test Groq connection"""
    settings = get_settings()
    
    if not settings.groq_api_key:
        print("ERROR Groq: No API key configured")
        return False
    
    try:
        client = GroqClient(settings.groq_api_key, settings.groq_model)
        response = await client.generate("Test prompt: Say 'Hello from Groq'")
        print(f"OK Groq ({settings.groq_model}): {response.content[:50]}...")
        return True
    except Exception as e:
        print(f"ERROR Groq: {e}")
        return False

async def test_ollama():
    """Test Ollama local models"""
    settings = get_settings()
    
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [m["name"] for m in models]
                print(f"OK Ollama available models: {available_models}")
                
                # Check if configured models are available
                configured_models = [
                    settings.local_model_fast,
                    settings.local_model_balanced, 
                    settings.local_model_creative
                ]
                
                for model in configured_models:
                    if model in available_models:
                        print(f"  OK {model}: Available")
                    else:
                        print(f"  MISSING {model}: Not found")
                
                return len([m for m in configured_models if m in available_models]) > 0
            else:
                print(f"ERROR Ollama: Server responded with {response.status_code}")
                return False
                
    except Exception as e:
        print(f"ERROR Ollama: {e}")
        return False

def check_fallback_configuration():
    """Check fallback configuration"""
    settings = get_settings()
    
    print("\nFallback Configuration:")
    print(f"  MODEL_STRATEGY: {settings.MODEL_STRATEGY}")
    print(f"  prefer_local: {settings.prefer_local}")
    print(f"  fallback_to_cloud: {settings.fallback_to_cloud}")
    print(f"  model_preference: {settings.model_preference}")
    
    print("\nAgent Model Assignment:")
    print(f"  prompt_analyzer_model: {settings.prompt_analyzer_model}")
    print(f"  post_classifier_model: {settings.post_classifier_model}")
    print(f"  brand_voice_model: {settings.brand_voice_model}")
    print(f"  fact_grounding_model: {settings.fact_grounding_model}")
    print(f"  text_generator_model: {settings.text_generator_model}")
    print(f"  caption_creator_model: {settings.caption_creator_model}")
    print(f"  visual_concept_model: {settings.visual_concept_model}")
    print(f"  reasoning_module_model: {settings.reasoning_module_model}")

async def main():
    """Test all API connections and fallback configuration"""
    print("Testing API Connections and Fallback Configuration\n")
    
    # Test API connections
    google_ok = await test_google_ai()
    groq_ok = await test_groq()
    ollama_ok = await test_ollama()
    
    print(f"\nResults Summary:")
    print(f"  Google AI (Gemini): {'OK' if google_ok else 'FAIL'}")
    print(f"  Groq: {'OK' if groq_ok else 'FAIL'}")
    print(f"  Ollama (Local): {'OK' if ollama_ok else 'FAIL'}")
    
    # Check fallback configuration
    check_fallback_configuration()
    
    # Recommendations
    print(f"\nRecommendations:")
    if not google_ok and not groq_ok:
        print("  WARNING: No cloud APIs working - system will rely on local models only")
        if not ollama_ok:
            print("  ERROR: No working APIs found! Please configure at least one provider")
    elif ollama_ok:
        print("  SUCCESS: Local models available as fallback - optimal configuration!")
    else:
        print("  WARNING: Only cloud APIs working - consider setting up Ollama for fallback")
    
    if google_ok or groq_ok or ollama_ok:
        print("  SUCCESS: System ready to run!")
        return True
    else:
        print("  ERROR: System cannot run without at least one working API")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
