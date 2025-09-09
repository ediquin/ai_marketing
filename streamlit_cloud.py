"""
Streamlit app optimizada para deployment en la nube
Solo usa modelos cloud (sin Ollama)
"""
import streamlit as st
import asyncio
import json
import time
from datetime import datetime
import logging
import os

# Configurar logging para producción
logging.basicConfig(level=logging.WARNING)

# Importar configuración cloud
from src.config.cloud_settings import get_cloud_settings
from src.graph.workflow import MarketingWorkflow

# Configuración de página
st.set_page_config(
    page_title="AI Marketing Strategist - Cloud",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def check_api_keys():
    """Verifica que las API keys estén configuradas"""
    settings = get_cloud_settings()
    
    has_google = bool(settings.google_api_key)
    has_groq = bool(settings.groq_api_key)
    has_openai = bool(settings.openai_api_key)
    has_anthropic = bool(settings.anthropic_api_key)
    
    return {
        'google': has_google,
        'groq': has_groq,
        'openai': has_openai,
        'anthropic': has_anthropic,
        'any_available': has_google or has_groq or has_openai or has_anthropic
    }

def display_api_status():
    """Muestra el estado de las APIs"""
    api_status = check_api_keys()
    
    st.sidebar.markdown("### 🔑 Estado de APIs")
    
    status_icons = {
        'google': '🟢' if api_status['google'] else '🔴',
        'groq': '🟢' if api_status['groq'] else '🔴',
        'openai': '🟢' if api_status['openai'] else '🔴',
        'anthropic': '🟢' if api_status['anthropic'] else '🔴'
    }
    
    st.sidebar.markdown(f"""
    - Google AI: {status_icons['google']}
    - Groq: {status_icons['groq']}
    - OpenAI: {status_icons['openai']}
    - Anthropic: {status_icons['anthropic']}
    """)
    
    if not api_status['any_available']:
        st.sidebar.error("⚠️ No hay APIs configuradas. Configura al menos una API key.")
        return False
    
    return True

async def process_marketing_prompt(prompt: str, language: str = None):
    """Procesa el prompt de marketing usando solo modelos cloud"""
    try:
        # Crear workflow con configuración cloud
        workflow = MarketingWorkflow(enable_rag=True, use_realtime_data=False)
        
        # Configurar idioma si se especifica
        language_config = {"language": language} if language else None
        
        # Procesar prompt
        result = await workflow.process_prompt(prompt, language_config)
        
        return result
        
    except Exception as e:
        st.error(f"Error procesando el prompt: {str(e)}")
        return None

def display_brief_results(result):
    """Muestra los resultados del brief de marketing"""
    if not result or result.is_error:
        st.error("❌ Error generando el brief de marketing")
        if hasattr(result, 'errors') and result.errors:
            for error in result.errors:
                st.error(f"• {error}")
        return
    
    # Información general
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("⏱️ Tiempo Total", f"{result.agent_timings.get('total', 0):.1f}s")
    
    with col2:
        st.metric("🤖 Agentes Ejecutados", len(result.completed_steps))
    
    with col3:
        success_rate = (1 - (len(result.errors) / max(len(result.completed_steps), 1))) * 100
        st.metric("✅ Tasa de Éxito", f"{success_rate:.0f}%")
    
    # Brief final
    if result.final_brief:
        st.markdown("## 📋 Brief de Marketing Completo")
        
        # Tabs para organizar la información
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Contenido", "🎨 Visual", "📊 Estrategia", "⚙️ Metadatos"])
        
        with tab1:
            st.markdown("### Contenido Principal")
            st.write(result.final_brief.core_content)
            
            if result.final_brief.engagement_elements:
                st.markdown("### Elementos de Engagement")
                st.write(f"**Hook:** {result.final_brief.engagement_elements.hook}")
                st.write(f"**CTA:** {result.final_brief.engagement_elements.call_to_action}")
                st.write(f"**Hashtags:** {', '.join(result.final_brief.engagement_elements.hashtags)}")
        
        with tab2:
            if result.final_brief.visual_concept:
                st.markdown("### Concepto Visual")
                st.write(f"**Tema:** {result.final_brief.visual_concept.theme}")
                st.write(f"**Paleta de Colores:** {', '.join(result.final_brief.visual_concept.color_palette)}")
                st.write(f"**Elementos:** {', '.join(result.final_brief.visual_concept.visual_elements)}")
        
        with tab3:
            if result.final_brief.reasoning:
                st.markdown("### Razonamiento Estratégico")
                st.write(result.final_brief.reasoning.strategic_rationale)
                
                if hasattr(result.final_brief.reasoning, 'performance_prediction'):
                    st.write(f"**Predicción de Performance:** {result.final_brief.reasoning.performance_prediction}")
        
        with tab4:
            if result.final_brief.metadata:
                st.markdown("### Metadatos de Procesamiento")
                st.json({
                    "tiempo_procesamiento": f"{result.final_brief.metadata.processing_time:.2f}s",
                    "modelo_usado": result.final_brief.metadata.model_used,
                    "timestamp": result.final_brief.metadata.timestamp.isoformat() if result.final_brief.metadata.timestamp else None,
                    "version": result.final_brief.metadata.version
                })

def main():
    """Función principal de la aplicación"""
    st.markdown('<h1 class="main-header">🚀 AI Marketing Strategist - Cloud</h1>', unsafe_allow_html=True)
    
    # Verificar APIs
    if not display_api_status():
        st.warning("⚠️ Configura las API keys en las variables de entorno para usar la aplicación.")
        st.markdown("""
        ### Variables de entorno requeridas:
        - `GOOGLE_API_KEY` - Para Google AI (Gemini)
        - `GROQ_API_KEY` - Para Groq
        - `OPENAI_API_KEY` - Para OpenAI (opcional)
        - `ANTHROPIC_API_KEY` - Para Anthropic (opcional)
        """)
        return
    
    # Sidebar con configuraciones
    st.sidebar.markdown("### ⚙️ Configuración")
    
    language = st.sidebar.selectbox(
        "Idioma de respuesta",
        ["Auto-detectar", "Español", "English"],
        index=0
    )
    
    enable_advanced = st.sidebar.checkbox("🔬 Características Avanzadas", value=True)
    
    # Área principal
    st.markdown("### 💬 Ingresa tu prompt de marketing")
    
    # Ejemplos predefinidos
    examples = {
        "Selecciona un ejemplo...": "",
        "🛍️ E-commerce": "Crear un post promocional para el lanzamiento de nuestra nueva colección de ropa sostenible dirigida a millennials conscientes del medio ambiente",
        "🍕 Restaurante": "Desarrollar contenido para promocionar nuestro nuevo menú de comida saludable en redes sociales, enfocado en familias jóvenes",
        "💼 B2B SaaS": "Generar contenido para LinkedIn promocionando nuestra plataforma de gestión de proyectos para equipos remotos",
        "🏋️ Fitness": "Crear campaña para lanzar nuestra nueva app de fitness con entrenamientos personalizados",
        "🎓 Educación": "Desarrollar contenido para promocionar nuestro curso online de marketing digital para emprendedores"
    }
    
    selected_example = st.selectbox("📋 Ejemplos rápidos:", list(examples.keys()))
    
    # Input del usuario
    if selected_example != "Selecciona un ejemplo...":
        default_prompt = examples[selected_example]
    else:
        default_prompt = ""
    
    user_prompt = st.text_area(
        "Describe tu objetivo de marketing:",
        value=default_prompt,
        height=100,
        placeholder="Ejemplo: Crear un post promocional para el lanzamiento de nuestro nuevo producto..."
    )
    
    # Botón de procesamiento
    if st.button("🚀 Generar Brief de Marketing", type="primary"):
        if not user_prompt.strip():
            st.warning("⚠️ Por favor ingresa un prompt de marketing.")
            return
        
        # Configurar idioma
        lang_config = None
        if language == "Español":
            lang_config = "es"
        elif language == "English":
            lang_config = "en"
        
        # Mostrar progreso
        with st.spinner("🤖 Procesando con agentes de IA..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simular progreso
            for i in range(100):
                progress_bar.progress(i + 1)
                if i < 20:
                    status_text.text("🔍 Analizando prompt...")
                elif i < 40:
                    status_text.text("📊 Clasificando contenido...")
                elif i < 60:
                    status_text.text("✍️ Generando contenido...")
                elif i < 80:
                    status_text.text("🎨 Creando concepto visual...")
                else:
                    status_text.text("🧠 Aplicando razonamiento estratégico...")
                time.sleep(0.05)
            
            # Procesar prompt
            result = asyncio.run(process_marketing_prompt(user_prompt, lang_config))
            
            progress_bar.empty()
            status_text.empty()
        
        # Mostrar resultados
        if result:
            display_brief_results(result)
        else:
            st.error("❌ No se pudo generar el brief. Intenta de nuevo.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        🤖 AI Marketing Strategist - Powered by Multi-Agent LLM System<br>
        🌟 12 Agentes Especializados | ⚡ Optimizado para la Nube
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
