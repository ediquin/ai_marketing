# 🚀 AI Marketing Strategist

Sistema agéntico inteligente para generar estrategias de marketing completas usando LangGraph y múltiples LLMs.

## ✨ Características

### 🤖 **8 Agentes Especializados**
- **Prompt Analyzer**: Analiza y estructura el input del usuario
- **Post Classifier**: Clasifica el tipo de contenido requerido
- **Brand Voice Agent**: Define la voz y personalidad de marca
- **Fact Grounding Agent**: Valida y estructura información factual
- **Text Generator**: Genera el contenido principal
- **Caption Creator**: Crea elementos de engagement (hashtags, CTAs)
- **Visual Concept Agent**: Desarrolla conceptos visuales
- **Reasoning Module**: Proporciona análisis estratégico
- **Result Optimizer**: Optimiza recomendaciones con datos reales (RAG)

### 🌐 **Sistema Multiidioma**
- **Detección automática** de idioma del prompt
- **Switch manual** para forzar idioma específico
- Soporte para **Español** e **Inglés**
- Respuestas consistentes en el idioma seleccionado

### 🔧 **Tecnologías**
- **LangGraph**: Orquestación de workflow
- **Pydantic v2**: Validación de datos
- **Streamlit**: Interfaz web interactiva
- **Async/Await**: Procesamiento asíncrono
- **Multiple LLMs**: Groq, Google AI, OpenAI, Anthropic
- **RAG System**: ChromaDB + Sentence Transformers + DuckDuckGo Search

## 🚀 Instalación

### Prerrequisitos
```bash
Python 3.8+
pip install -r requirements.txt
```

### Configuración
1. Copia `.env.example` a `.env`
2. Configura tus API keys:
```env
# Proveedores principales (GRATIS)
GOOGLE_API_KEY=tu_api_key_aqui
GROQ_API_KEY=tu_api_key_aqui

# Configuración de idioma
LANGUAGE_DETECTION=auto
DEFAULT_LANGUAGE=es
```

3. **Instala dependencias RAG** (opcional pero recomendado):
```bash
pip install chromadb sentence-transformers duckduckgo-search
```

4. **Prueba el sistema RAG**:
```bash
python test_rag_system.py
```

### Ejecución
```bash
# Interfaz Streamlit
streamlit run src/streamlit_app.py

# Uso programático
python src/main.py
```

## 📊 Uso

### Interfaz Web
1. Abre http://localhost:8501
2. Selecciona idioma (Auto/Español/English)
3. **Activa "Enable RAG System"** para usar datos reales de marketing
4. Ingresa tu prompt de marketing
5. Obtén brief completo con datos reales en segundos

### API Programática
```python
from graph.workflow import create_marketing_workflow
from utils.language_detector import LanguageDetector, Language

# Crear workflow
workflow = create_marketing_workflow()

# Detectar idioma y configurar
detector = LanguageDetector()
lang_config = detector.get_language_config(
    detector.detect_language(prompt),
    Language.AUTO
)

# Procesar prompt
result = await workflow.process_prompt(prompt, lang_config)
```

## 🏗️ Arquitectura

```
Input Prompt → Language Detection → LangGraph Workflow
                                         ↓
┌─────────────────────────────────────────────────────────┐
│  Prompt → Classify → Brand → Facts → Content → Caption  │
│     ↓        ↓        ↓       ↓        ↓        ↓      │
│  Visual → Reasoning → Final Assembly → Content Brief    │
└─────────────────────────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
src/
├── agents/          # Agentes especializados
├── config/          # Configuración del sistema
├── graph/           # Workflow LangGraph
├── models/          # Modelos Pydantic
├── tools/           # Cliente LLM unificado
├── utils/           # Utilidades (detector de idioma)
├── main.py          # Entry point principal
└── streamlit_app.py # Interfaz web

tests/               # Tests automatizados
docs/                # Documentación
examples/            # Ejemplos de uso
```

## 🔧 Configuración Avanzada

### Modelos por Agente
```env
PROMPT_ANALYZER_MODEL=gemini
POST_CLASSIFIER_MODEL=groq
BRAND_VOICE_MODEL=gemini
FACT_GROUNDING_MODEL=groq
TEXT_GENERATOR_MODEL=gemini
CAPTION_CREATOR_MODEL=groq
VISUAL_CONCEPT_MODEL=gemini
REASONING_MODULE_MODEL=gemini
```

### Performance
```env
ENABLE_PARALLEL_PROCESSING=true
ENABLE_CACHING=true
TARGET_PROCESSING_TIME=10.0
```

## 🧠 Sistema RAG (Retrieval-Augmented Generation)

### Características Principales
- **100% Gratuito**: ChromaDB + Sentence Transformers + DuckDuckGo Search
- **Datos Reales**: Benchmarks de marketing de reportes 2024 (HubSpot, Hootsuite, etc.)
- **Tendencias Actuales**: Hashtags y temas trending en tiempo real
- **Fallback Inteligente**: Sistema robusto con degradación elegante

### Beneficios
- **Recomendaciones basadas en datos reales** vs simulados
- **Contexto actual del mercado** para decisiones informadas
- **Justificación histórica** de cada recomendación
- **Predicciones de performance** con niveles de confianza

📖 **Ver [RAG_SYSTEM_GUIDE.md](RAG_SYSTEM_GUIDE.md) para documentación completa**

## 📈 Métricas

- **Tiempo promedio**: ~8-10 segundos
- **Tasa de éxito**: >95%
- **Soporte multiidioma**: Español/Inglés
- **Agentes activos**: 9/9 (incluyendo Result Optimizer con RAG)
- **Datos RAG**: 50+ benchmarks reales de marketing

## 🚀 Deploy

### Streamlit Cloud
```bash
# Preparar para deploy
pip freeze > requirements.txt
git add .
git commit -m "Ready for deploy"
git push origin main
```

### Docker
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "src/streamlit_app.py"]
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push branch (`git push origin feature/nueva-funcionalidad`)
5. Abre Pull Request

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/ai-marketing-strategist/issues)
- **Documentación**: [Wiki](https://github.com/tu-usuario/ai-marketing-strategist/wiki)
- **Ejemplos**: Ver carpeta `examples/`

---

**Desarrollado con ❤️ usando LangGraph y Streamlit**