import os
import streamlit as st
from src.config.cloud_settings import CloudSettings
from src.graph.workflow import create_workflow
from src.graph.state import WorkflowState

# Configuración de la página
st.set_page_config(
    page_title="AI Marketing Strategist (Lite)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main .block-container {
        max-width: 1200px;
        padding: 2rem 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .agent-card {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border-left: 4px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Título y descripción
st.title("🤖 AI Marketing Strategist (Lite)")
st.markdown("""
Esta es una versión ligera del AI Marketing Strategist sin funcionalidades de RAG.
""")

# Sidebar para configuración
with st.sidebar:
    st.header("🔧 Configuración")
    
    # Mostrar estado de las APIs
    st.subheader("🔑 Estado de APIs")
    
    # Verificar APIs
    google_status = "🟢" if os.getenv("GOOGLE_API_KEY") else "🔴"
    groq_status = "🟢" if os.getenv("GROQ_API_KEY") else "🔴"
    openai_status = "🟢" if os.getenv("OPENAI_API_KEY") else "🔴"
    anthropic_status = "🟢" if os.getenv("ANTHROPIC_API_KEY") else "🔴"
    
    st.write(f"Google AI: {google_status}")
    st.write(f"Groq: {groq_status}")
    st.write(f"OpenAI: {openai_status}")
    st.write(f"Anthropic: {anthropic_status}")
    
    if not any([os.getenv("GOOGLE_API_KEY"), os.getenv("GROQ_API_KEY"), 
                os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]):
        st.error("⚠️ Configura al menos una API Key en las variables de entorno")
    
    # Selector de modelo
    st.subheader("🧠 Modelo Principal")
    model_provider = st.selectbox(
        "Proveedor de Modelo",
        ["google", "groq", "openai", "anthropic"],
        index=0
    )
    
    # Configuración avanzada
    with st.expander("⚙️ Configuración Avanzada"):
        temperature = st.slider("Temperatura", 0.0, 1.0, 0.7, 0.1)
        max_tokens = st.number_input("Tokens Máximos", 100, 4000, 1000)

# Entrada del usuario
prompt = st.text_area(
    "📝 Describe tu campaña de marketing (ej: 'Lanzamiento de app de fitness con IA personalizada')",
    height=150
)

# Botón de envío
if st.button("🚀 Generar Estrategia", type="primary") and prompt:
    with st.spinner("🚀 Generando tu estrategia de marketing..."):
        try:
            # Configuración
            settings = CloudSettings()
            settings.model_strategy = "cloud-only"  # Forzar solo modelos en la nube
            settings.rag_enabled = False  # Deshabilitar RAG
            
            # Crear estado inicial
            state = WorkflowState(
                user_prompt=prompt,
                model_provider=model_provider,
                temperature=temperature,
                max_tokens=max_tokens,
                rag_enabled=False  # Asegurar que RAG esté deshabilitado
            )
            
            # Crear y ejecutar workflow
            workflow = create_workflow(settings)
            
            # Mostrar progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Ejecutar workflow
            final_state = None
            for i, step in enumerate(workflow.stream(state)):
                status = step.get("__end__")
                if status:
                    final_state = status
                    break
                
                # Actualizar progreso
                progress = min((i + 1) / 12, 1.0)  # 12 agentes en total
                progress_bar.progress(progress)
                status_text.text(f"Procesando paso {i+1}/12: {step.get('current_agent', 'Iniciando...')}")
            
            # Mostrar resultados
            if final_state and final_state.final_brief:
                st.success("✅ Estrategia generada con éxito!")
                
                # Mostrar el brief completo
                with st.expander("📄 Ver Brief Completo", expanded=True):
                    st.markdown(final_state.final_brief)
                
                # Mostrar resumen de agentes
                st.subheader("🔍 Proceso de Generación")
                for agent, result in final_state.agent_outputs.items():
                    with st.expander(f"{agent}:", expanded=False):
                        st.markdown(f"```\n{result}\n```")
            
        except Exception as e:
            st.error(f"❌ Error al generar la estrategia: {str(e)}")

# Footer
st.markdown("---")
st.caption("AI Marketing Strategist Lite v1.0 - Sin dependencias de RAG")
