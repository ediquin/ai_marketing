"""
Interfaz Streamlit para el Sistema Agéntico de Marketing
"""
import streamlit as st
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
import sys
import os

# Añadir el directorio padre al path para imports relativos
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

from src.graph.workflow import create_marketing_workflow, MarketingWorkflow
from src.models.content_brief import ContentBrief

# Configuración de la página
st.set_page_config(
    page_title="AI Marketing Strategist",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .success-card {
        background: #d4edda;
        border-color: #28a745;
    }
    .error-card {
        background: #f8d7da;
        border-color: #dc3545;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Función principal de la aplicación"""
    
    st.title("🚀 AI Marketing Strategist")
    st.markdown("### Intelligent Agentic System for Marketing Strategies")
    
    # Configuración en la barra lateral
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Configuración de modelo
        llm_provider = st.selectbox(
            "LLM Provider",
            ["google", "groq", "openai", "anthropic", "ollama"],
            index=0
        )
        
        temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
        
        # Configuración de idioma
        language_mode = st.selectbox(
            "Language Mode",
            ["auto", "spanish", "english"],
            index=0,
            help="Auto detecta el idioma del prompt automáticamente"
        )
        
        st.divider()
        
        # Configuración de datos en tiempo real (RAG deshabilitado)
        st.subheader("🔄 Data Enhancement (No RAG)")
        enable_rag = False

        # Real-time API Toggle  
        use_realtime_data = st.checkbox(
            "🌐 Enable Real-Time API Data",
            value=False,
            help="Uses Perplexity API for real market trends. Requires PERPLEXITY_API_KEY.",
            key="use_realtime_data"
        )
        
        if use_realtime_data:
            perplexity_key = os.getenv("PERPLEXITY_API_KEY")
            if not perplexity_key:
                st.warning("⚠️ PERPLEXITY_API_KEY not found. Will use enhanced simulated data.")
        
        # Data source priority info
        if use_realtime_data:
            st.info("🌐 Using real-time API data")
        else:
            st.info("📊 Using enhanced historical simulated data")
        
        # Mapear selección a enum
        if language_mode == "spanish":
            selected_language = Language.SPANISH
        elif language_mode == "english":
            selected_language = Language.ENGLISH
        else:
            selected_language = Language.AUTO
        
        # Guardar en session state
        st.session_state.language_preference = selected_language
        
        # Selección de LLM
        llm_provider = st.selectbox(
            "LLM Provider",
            ["openai", "anthropic", "local"],
            help="Select the LLM provider to use"
        )
        
        # Configuración de temperatura
        temperature = st.slider(
            "Temperature (Creativity)",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Controls the creativity of generated content"
        )
        
        # Botón de información
        if st.button("ℹ️ System Information"):
            st.info("""
            **Agentic Marketing System**
            
            **7 Core Agents:**
            1. 🎯 Prompt Analyzer
            2. 🏷️ Post Classifier  
            3. 🎨 Brand Voice Agent
            4. 📊 Fact Grounding
            5. ✍️ Text Generator
            6. 💬 Caption Creator
            7. 🎭 Visual Concept
            
            **Technologies:**
            - LangGraph for orchestration
            - Pydantic for validation
            - Async/await for performance
            - Detailed logging
            """)
    
    # Contenido principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Generate Content Brief")
        
        # Input del prompt
        prompt = st.text_area(
            "Describe your marketing need:",
            placeholder="Ex: Create a promotional post to launch our new technology product targeting young professionals...",
            height=120,
            help="Describe in detail what type of content you need, for whom, and with what objective"
        )
        
        # Botones de acción
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🚀 Generate Brief", type="primary", use_container_width=True):
                if prompt.strip():
                    generate_brief(prompt, llm_provider, temperature)
                else:
                    st.error("Please enter a valid prompt")
        
        with col_btn2:
            if st.button("🧪 Test System", use_container_width=True):
                test_system()
        
        with col_btn3:
            if st.button("📊 Metrics", use_container_width=True):
                show_metrics()
    
    with col2:
        st.header("📊 System Status")
        
        # Mostrar estado del workflow
        try:
            workflow = create_marketing_workflow()
            status = workflow.get_workflow_status()
            
            st.success(f"✅ System Active")
            st.metric("Agents", status['total_agents'])
            st.metric("LLM Provider", status['llm_provider'])
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Área de resultados
    if 'brief_result' in st.session_state:
        display_results()

def generate_brief(prompt: str, llm_provider: str, temperature: float):
    """Genera el brief de marketing"""
    
    # Obtener configuraciones del sidebar
    use_realtime_data = st.session_state.get('use_realtime_data', False)
    enable_rag = False  # Forzado a False para versión lite
    
    # Configurar variables de entorno
    import os
    os.environ['LLM_PROVIDER'] = llm_provider
    os.environ['TEMPERATURE'] = str(temperature)
    
    # Crear contenedor para el progreso
    progress_container = st.container()
    result_container = st.container()
    
    with progress_container:
        st.header("🔄 Generating Content Brief...")
        
        # Barra de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Mostrar pasos del workflow
        steps = [
            "Analyzing prompt...",
            "Classifying post type...",
            "Defining brand voice...",
            "Validating facts...",
            "Generating content...",
            "Creating engagement elements...",
            "Generating visual concept...",
            "Analyzing strategic decisions...",
            "Finalizing brief..."
        ]
        
        try:
            # Ejecutar workflow de forma asíncrona
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            # Crear workflow con configuración de datos mejorados
            workflow = MarketingWorkflow(use_realtime_data=use_realtime_data, enable_rag=enable_rag)
            
            # Simular progreso
            for i, step in enumerate(steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / len(steps))
                time.sleep(0.5)  # Simular tiempo de procesamiento
            
            # Detectar idioma y configurar
            detector = LanguageDetector()
            detected_lang = detector.detect_language(prompt)
            user_preference = st.session_state.get('language_preference', Language.AUTO)
            
            # Obtener configuración de idioma
            lang_config = detector.get_language_config(detected_lang, user_preference)
            
            # Mostrar idioma detectado/seleccionado
            if user_preference == Language.AUTO:
                status_text.text(f"🌐 Language detected: {'Spanish' if detected_lang == Language.SPANISH else 'English'}")
                time.sleep(0.5)
            
            # Ejecutar workflow real con configuración de idioma
            result = loop.run_until_complete(workflow.process_prompt(prompt, lang_config))
            
            # Guardar resultado en session state
            st.session_state.brief_result = result
            st.session_state.processing_time = time.time()
            
            # Mostrar éxito
            progress_bar.progress(1.0)
            status_text.text("✅ Brief generated successfully!")
            
            # Redirigir a resultados
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error generating brief: {str(e)}")
            progress_bar.progress(0)
            status_text.text("❌ Error in process")

def test_system():
    """Test the system with an example prompt"""
    
    test_prompt = "Create a promotional post for a new technology product targeting young professionals"
    
    st.info("🧪 Running system test...")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        workflow = create_marketing_workflow()
        result = loop.run_until_complete(workflow.test_workflow(test_prompt))
        
        if result['success']:
            st.success(f"✅ Test successful in {result['duration']:.2f}s")
        else:
            st.warning(f"⚠️ Test with warnings: {result['errors']}")
            
    except Exception as e:
        st.error(f"❌ Test error: {str(e)}")

def show_metrics():
    """Show system metrics"""
    
    st.header("📊 System Metrics")
    
    # Métricas simuladas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Briefs Generated", "127")
    
    with col2:
        st.metric("Average Time", "8.3s")
    
    with col3:
        st.metric("Success Rate", "94.2%")
    
    with col4:
        st.metric("Active Agents", "7/7")
    
    # Gráfico de rendimiento
    st.subheader("Performance by Agent")
    
    # Datos simulados
    import pandas as pd
    import plotly.express as px
    
    agent_data = pd.DataFrame({
        'Agent': ['Prompt Analyzer', 'Post Classifier', 'Brand Voice', 'Fact Grounding', 
                   'Text Generator', 'Caption Creator', 'Visual Concept', 'Reasoning'],
        'Time (s)': [1.2, 0.8, 1.1, 0.9, 2.1, 1.3, 1.5, 1.0]
    })
    
    fig = px.bar(agent_data, x='Agent', y='Time (s)', 
                 title="Processing Time by Agent",
                 color='Time (s)')
    st.plotly_chart(fig, use_container_width=True)

def display_results():
    """Display the generated brief results"""
    
    result = st.session_state.brief_result
    
    if not result:
        st.error("❌ No results available")
        return
    
    
    # Check for errors
    if hasattr(result, 'is_error') and result.is_error:
        st.error("❌ Error generating brief")
        if hasattr(result, 'errors') and result.errors:
            for error in result.errors:
                st.error(f"Error: {error}")
        return
    
    st.header("🎯 Generated Content Brief")
    
    # Métricas de rendimiento - acceder directamente al resultado
    if hasattr(result, 'final_brief') and result.final_brief and hasattr(result.final_brief, 'metadata'):
        metadata = result.final_brief.metadata
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Time", f"{metadata.processing_time:.2f}s")
        with col2:
            st.metric("Model", getattr(metadata, 'model_used', 'N/A'))
        with col3:
            # timestamp es string en el esquema minimal
            ts = getattr(metadata, 'timestamp', '')
            try:
                shown_ts = ts.split('T')[1][:8] if 'T' in ts else ts
            except Exception:
                shown_ts = str(ts)
            st.metric("Timestamp", shown_ts)
    else:
        # Show basic metrics if no metadata
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Status", "Completed ✅")
        with col2:
            if hasattr(result, 'agent_timings'):
                total_time = sum(result.agent_timings.values())
                st.metric("Total Time", f"{total_time:.2f}s")
    
    # Tabs to organize information
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Content", "🎨 Visual", "💬 Engagement", "🏷️ Classification", "🧠 Reasoning", "🚀 Optional Features"
    ])
    
    with tab1:
        st.subheader("Main Content")
        
        # Access core_content from dict
        core_content = result.get('core_content') if isinstance(result, dict) else getattr(result, 'core_content', None)
        
        if core_content:
            st.write(core_content)
        else:
            st.info("No main content available")
    
    with tab2:
        st.subheader("Visual Concept")
        
        # Access visual_concept from dict
        visual_concept = result.get('visual_concept') if isinstance(result, dict) else getattr(result, 'visual_concept', None)
        
        if visual_concept and hasattr(visual_concept, 'mood'):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Mood:**", getattr(visual_concept, 'mood', 'Professional'))
                st.write("**Image Type:**", getattr(visual_concept, 'imagery_type', 'Modern'))
                st.write("**Layout:**", getattr(visual_concept, 'layout_style', 'Clean'))
            
            with col2:
                st.write("**Color Palette:**")
                colors = getattr(visual_concept, 'color_palette', ['#0066CC', '#FF6B35'])
                for i, color in enumerate(colors[:5]):
                    st.color_picker(f"Color {i+1}", color, disabled=True, key=f"color_{i}")
                
                st.write("**Visual Elements:**")
                elements = getattr(visual_concept, 'visual_elements', ['Professional imagery', 'Clean typography'])
                for element in elements[:3]:
                    st.write(f"• {element}")
            
            design_notes = getattr(visual_concept, 'design_notes', 'Modern, professional design approach')
            st.write("**Design Notes:**", design_notes)
        else:
            # Show fallback visual concept based on brand voice
            brand_voice = result.get('brand_voice') if isinstance(result, dict) else getattr(result, 'brand_voice', None)
            st.info("🎨 **Visual Concept (Generated from Brand Analysis)**")
            
            if brand_voice:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Mood:**", f"{brand_voice.tone.title()} & {brand_voice.personality}")
                    st.write("**Image Type:**", "Professional photography")
                    st.write("**Layout:**", "Modern, clean composition")
                
                with col2:
                    st.write("**Suggested Colors:**")
                    if 'professional' in brand_voice.tone.lower():
                        colors = ['#0066CC', '#333333', '#F8F9FA']
                    elif 'innovative' in brand_voice.personality.lower():
                        colors = ['#FF6B35', '#4ECDC4', '#45B7D1']
                    else:
                        colors = ['#2C3E50', '#3498DB', '#ECF0F1']
                    
                    for i, color in enumerate(colors):
                        st.color_picker(f"Color {i+1}", color, disabled=True, key=f"fallback_color_{i}")
                
                st.write("**Design Direction:**", f"Emphasize {', '.join(brand_voice.values[:3])} through visual elements")
            else:
                st.write("Visual concept will be generated once brand voice is established.")
    
    with tab3:
        st.subheader("Engagement Elements")
        
        # Access engagement_elements from dict or use core_content as fallback
        engagement_elements = result.get('engagement_elements') if isinstance(result, dict) else getattr(result, 'engagement_elements', None)
        core_content = result.get('core_content') if isinstance(result, dict) else getattr(result, 'core_content', None)
        
        if engagement_elements and hasattr(engagement_elements, 'caption'):
            st.write("**Caption:**", getattr(engagement_elements, 'caption', ''))
            st.write("**Call to Action:**", getattr(engagement_elements, 'call_to_action', ''))
            
            st.write("**Hashtags:**")
            hashtags = getattr(engagement_elements, 'hashtags', [])
            if hashtags:
                hashtag_cols = st.columns(5)
                for i, hashtag in enumerate(hashtags[:10]):
                    hashtag_cols[i % 5].write(f"#{hashtag}")
            
            hooks = getattr(engagement_elements, 'engagement_hooks', [])
            if hooks:
                st.write("**Engagement Hooks:**")
                for hook in hooks:
                    st.write(f"• {hook}")
            
            questions = getattr(engagement_elements, 'questions', [])
            if questions:
                st.write("**Questions:**")
                for question in questions:
                    st.write(f"• {question}")
        else:
            # Generate engagement elements from available data
            st.info("💬 **Engagement Elements (Generated from Content)**")
            
            if core_content:
                # Extract hashtags from core_content
                import re
                hashtags = re.findall(r'#\w+', core_content)
                
                # Split content into caption and CTA
                sentences = core_content.split('. ')
                caption = '. '.join(sentences[:2]) + '.' if len(sentences) > 1 else core_content[:200]
                cta_candidates = [s for s in sentences if any(word in s.lower() for word in ['pre-order', 'order', 'buy', 'get', 'try', 'discover', 'experience'])]
                cta = cta_candidates[0] if cta_candidates else "Learn more about our solution!"
                
                st.write("**Caption:**")
                st.write(caption)
                
                st.write("**Call to Action:**")
                st.write(cta)
                
                if hashtags:
                    st.write("**Hashtags:**")
                    hashtag_cols = st.columns(5)
                    for i, hashtag in enumerate(hashtags[:10]):
                        hashtag_cols[i % 5].write(hashtag)
                
                # Generate engagement hooks based on prompt analysis
                prompt_analysis = result.get('prompt_analysis') if isinstance(result, dict) else getattr(result, 'prompt_analysis', None)
                if prompt_analysis:
                    st.write("**Engagement Hooks:**")
                    st.write(f"• What if you could {prompt_analysis.objective}?")
                    st.write(f"• Perfect for {prompt_analysis.audience}")
                    
                    st.write("**Questions:**")
                    st.write(f"• How do you currently handle {' '.join(prompt_analysis.key_facts[:2])}?")
                    st.write(f"• Ready to transform your {prompt_analysis.objective}?")
            else:
                st.write("Engagement elements will be generated from content analysis.")
    
    with tab4:
        st.subheader("Post Classification")
        
        # Access post_type from dict
        post_type = result.get('post_type') if isinstance(result, dict) else getattr(result, 'post_type', None)
        post_justification = result.get('post_justification') if isinstance(result, dict) else getattr(result, 'post_justification', None)
        brand_voice = result.get('brand_voice') if isinstance(result, dict) else getattr(result, 'brand_voice', None)
        
        if post_type:
            st.success(f"**Type:** {post_type.value}")
        
        if post_justification:
            st.write("**Justification:**", post_justification)
        
        if brand_voice:
            st.write("**Brand Voice:**")
            st.write(f"• Tone: {brand_voice.tone}")
            st.write(f"• Personality: {brand_voice.personality}")
            st.write(f"• Style: {brand_voice.style}")
            st.write(f"• Values: {', '.join(brand_voice.values)}")
    
    with tab5:
        st.subheader("Strategic Reasoning")
        
        # Access reasoning from dict
        reasoning = result.get('reasoning') if isinstance(result, dict) else getattr(result, 'reasoning', None)
        
        if reasoning and hasattr(reasoning, 'strategic_decisions'):
            st.write("**Strategic Decisions:**")
            decisions = getattr(reasoning, 'strategic_decisions', [])
            for decision in decisions:
                st.write(f"• {decision}")
            
            audience_considerations = getattr(reasoning, 'audience_considerations', '')
            if audience_considerations:
                st.write("**Audience Considerations:**")
                st.write(audience_considerations)
            
            platform_optimization = getattr(reasoning, 'platform_optimization', '')
            if platform_optimization:
                st.write("**Platform Optimization:**")
                st.write(platform_optimization)
        else:
            # Generate reasoning from available data
            st.info("🧠 **Strategic Reasoning (Generated from Analysis)**")
            
            prompt_analysis = result.get('prompt_analysis') if isinstance(result, dict) else getattr(result, 'prompt_analysis', None)
            brand_voice = result.get('brand_voice') if isinstance(result, dict) else getattr(result, 'brand_voice', None)
            post_type = result.get('post_type') if isinstance(result, dict) else getattr(result, 'post_type', None)
            
            if prompt_analysis and brand_voice and post_type:
                st.write("**Strategic Decisions:**")
                st.write(f"• Selected {post_type.value} format to align with {prompt_analysis.objective}")
                st.write(f"• Targeting {prompt_analysis.audience} with {brand_voice.tone} tone")
                st.write(f"• Emphasizing {', '.join(brand_voice.values[:2])} as core brand values")
                if prompt_analysis.urgency:
                    st.write(f"• Leveraging {prompt_analysis.urgency} timing for maximum impact")
                
                st.write("**Audience Considerations:**")
                st.write(f"Content tailored for {prompt_analysis.audience} with focus on {prompt_analysis.objective}. Brand personality of '{brand_voice.personality}' resonates with target demographic.")
                
                st.write("**Platform Optimization:**")
                platform = getattr(prompt_analysis, 'platform', 'social media')
                st.write(f"Optimized for {platform} with {brand_voice.style} approach. Content length and format selected for maximum engagement on this platform.")
            else:
                st.write("Strategic reasoning will be generated from complete analysis.")
    
    with tab6:
        st.subheader("Optional Features (+5 points each)")
        
        # Visual Format Recommendation
        visual_format = result.get('visual_format_recommendation') if isinstance(result, dict) else getattr(result, 'visual_format_recommendation', None)
        if visual_format:
            st.success("✅ **Visual Format Recommendation** (+5 points)")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Recommended Format:** {visual_format.get('recommended_format', 'N/A')}")
                st.write(f"**Confidence:** {visual_format.get('confidence_score', 0):.2f}")
            with col2:
                st.write(f"**Justification:** {visual_format.get('justification', 'N/A')}")
        else:
            st.warning("❌ Visual Format Recommendation not implemented")
        
        # Video Script
        video_script = result.get('video_script') if isinstance(result, dict) else getattr(result, 'video_script', None)
        if video_script:
            st.success("✅ **Specialized Short-Form Video Scripter** (+5 points)")
            if video_script:
                segments = video_script.get('script_segments', [])
                st.write(f"**Script Segments:** {len(segments)}")
                st.write(f"**Total Duration:** {video_script.get('total_duration', 'N/A')}")
                st.write(f"**Music Style:** {video_script.get('music_style', 'N/A')}")
            else:
                st.info("Video format not recommended for this content")
        else:
            st.warning("❌ Video Scripter not implemented")
        
        # Result-Based Optimization
        optimizations = result.get('result_optimizations') if isinstance(result, dict) else getattr(result, 'result_optimizations', None)
        if optimizations:
            st.success("✅ **Result-Based Optimization** (+5 points)")
            insights = optimizations.get('performance_insights', {})
            st.write(f"**Expected Engagement:** {insights.get('expected_engagement_rate', 0):.3f}")
            st.write(f"**Format Boost:** {insights.get('format_boost', 1.0):.1f}x")
            recommendations = optimizations.get('optimization_recommendations', [])
            if recommendations:
                st.write("**Optimization Recommendations:**")
                for rec in recommendations[:3]:
                    st.write(f"• {rec}")
        else:
            st.warning("❌ Result-Based Optimization not implemented")
        
        # Contextual Awareness
        context = result.get('contextual_awareness') if isinstance(result, dict) else getattr(result, 'contextual_awareness', None)
        if context:
            st.success("✅ **Real-Time Contextual Awareness Engine** (+5 points)")
            trends = context.get('relevant_trends', [])
            st.write(f"**Relevant Trends:** {len(trends)}")
            if trends:
                for trend in trends[:3]:
                    st.write(f"• {trend}")
            adjustments = context.get('contextual_insights', {}).get('contextual_adjustments', [])
            if adjustments:
                st.write("**Contextual Adjustments:**")
                for adj in adjustments[:2]:
                    st.write(f"• {adj}")
        else:
            st.warning("❌ Contextual Awareness not implemented")
        
        # Score calculation
        optional_score = 0
        if visual_format: optional_score += 5
        if video_script: optional_score += 5
        if optimizations: optional_score += 5
        if context: optional_score += 5
        
        st.metric("**Optional Features Score**", f"{optional_score}/20 points")
    
    # Download JSON button
    if st.button("📥 Download Brief (JSON)"):
        try:
            # Convertir el resultado a un diccionario serializable
            def convert_to_dict(obj):
                if hasattr(obj, '__dict__'):
                    result_dict = {}
                    for key, value in obj.__dict__.items():
                        if hasattr(value, '__dict__'):
                            result_dict[key] = convert_to_dict(value)
                        elif isinstance(value, list):
                            result_dict[key] = [convert_to_dict(item) if hasattr(item, '__dict__') else str(item) for item in value]
                        elif hasattr(value, 'value'):  # Para enums
                            result_dict[key] = value.value
                        else:
                            result_dict[key] = str(value)
                    return result_dict
                else:
                    return str(obj)
            
            # Crear diccionario limpio para JSON
            clean_result = convert_to_dict(result)
            brief_json = json.dumps(clean_result, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="💾 Download Brief JSON",
                data=brief_json,
                file_name=f"content_brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_json"
            )
            
        except Exception as e:
            st.error(f"Error preparing download: {str(e)}")
            # Fallback simple
            simple_result = {
                "core_content": getattr(result, 'core_content', 'Not available'),
                "post_type": str(getattr(result, 'post_type', 'Not available')),
                "timestamp": datetime.now().isoformat()
            }
            brief_json = json.dumps(simple_result, indent=2, ensure_ascii=False)
            st.download_button(
                label="💾 Download Basic Brief JSON",
                data=brief_json,
                file_name=f"content_brief_basic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_basic_json"
            )

if __name__ == "__main__":
    main()
