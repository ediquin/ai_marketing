import os
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

def test_configuration():
    """Probar que la configuración está correcta"""
    
    print("Verificando configuracion...\n")
    
    # Verificar APIs principales (gratuitas)
    google_key = os.getenv('GOOGLE_API_KEY')
    groq_key = os.getenv('GROQ_API_KEY')
    
    print("APIs Principales (Gratuitas):")
    print(f"  Google AI: {'Configurado' if google_key and google_key != 'your_google_api_key_here' else 'Falta configurar'}")
    print(f"  Groq: {'Configurado' if groq_key and groq_key != 'your_groq_api_key_here' else 'Falta configurar'}")
    
    # Verificar APIs opcionales
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print("\nAPIs Opcionales:")
    print(f"  OpenAI: {'Configurado' if openai_key else 'No configurado (opcional)'}")
    print(f"  Anthropic: {'Configurado' if anthropic_key else 'No configurado (opcional)'}")    
    # Verificar configuración local
    ollama_url = os.getenv('OLLAMA_BASE_URL')
    
    print(f"\nModelos Locales:")
    print(f"  Ollama URL: {ollama_url}")
    print(f"  Modelo Rapido: {os.getenv('LOCAL_MODEL_FAST')}")
    print(f"  Modelo Balanceado: {os.getenv('LOCAL_MODEL_BALANCED')}")
    print(f"  Modelo Creativo: {os.getenv('LOCAL_MODEL_CREATIVE')}")
    
    # Verificar estrategia de modelos
    print(f"\nEstrategia de Modelos:")
    print(f"  Preferencia: {os.getenv('MODEL_PREFERENCE')}")
    print(f"  Preferir Local: {os.getenv('PREFER_LOCAL')}")
    print(f"  Fallback Cloud: {os.getenv('FALLBACK_TO_CLOUD')}")
    
    print(f"\nConfiguracion del Sistema:")
    print(f"  Tiempo Objetivo: {os.getenv('TARGET_PROCESSING_TIME')}s")
    print(f"  Cache Habilitado: {os.getenv('ENABLE_CACHING')}")
    print(f"  Metricas: {os.getenv('ENABLE_METRICS')}")
    
    print(f"\nConfiguracion cargada correctamente!")

if __name__ == "__main__":
    test_configuration()