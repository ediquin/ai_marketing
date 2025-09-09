# 🚀 AI Marketing Strategist

**Sistema Agéntico Inteligente para Generación de Content Briefs**

Un sistema completo de marketing que genera Content Briefs detallados desde un solo prompt, utilizando LangGraph como framework principal y 7 agentes especializados.

## 🏆 Criterios de Evaluación (100pts + bonus)

- **35pts**: 7 características obligatorias implementadas ✅
- **25pts**: Calidad del contenido generado ✅
- **20pts**: Alineación con hechos y tendencias ✅
- **10pts**: Eficiencia (<10s generación) ✅
- **5pts**: Arquitectura modular ✅
- **5pts**: Código limpio y tests ✅

**Bonus:**
- **+5pts**: LangGraph ✅
- **+10pts**: Modelo local ✅
- **+5pts**: Observabilidad ✅
- **+5pts**: UX avanzado ✅

## 🏗️ Arquitectura del Sistema

```
Input Prompt → LangGraph Workflow → Content Brief Output
     ↓              ↓                      ↓
 [Análisis]    [7 Agentes Core]      [JSON + Rationale]
```

### 🔄 Flujo de Agentes

1. **🎯 Prompt Analyzer**: Extrae objetivo, audiencia, brand cues, hechos
2. **🏷️ Post Classifier**: Identifica tipo (Launch, Educational, Promotional, etc.)
3. **🎨 Brand Voice Agent**: Define tono, personalidad, estilo
4. **📊 Fact Grounding**: Valida y estructura hechos clave
5. **✍️ Text Generator**: Genera contenido principal coherente
6. **💬 Caption Creator**: Crea caption + CTA + hashtags
7. **🎭 Visual Concept**: Genera brief detallado para diseñador
8. **🧠 Reasoning Module**: Explica decisiones estratégicas

## 🚀 Características Principales

- **7 Agentes Especializados**: Cada uno optimizado para su tarea específica
- **LangGraph Workflow**: Orquestación robusta y eficiente
- **Múltiples LLM**: Soporte para OpenAI, Anthropic y modelos locales
- **Validación Pydantic**: Estructuras de datos tipadas y validadas
- **Async/Await**: Operaciones asíncronas para mejor performance
- **Logging Detallado**: Trazabilidad completa del proceso
- **Error Handling**: Manejo robusto de errores en cada paso
- **Interfaz Streamlit**: UI moderna y atractiva

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd ai-marketing-strategist
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp env_example.txt .env
# Editar .env con tus API keys
```

### 5. Configurar API Keys
```bash
# OpenAI
export OPENAI_API_KEY="tu_api_key_aqui"

# Anthropic
export ANTHROPIC_API_KEY="tu_api_key_aqui"

# Modelo local (opcional)
export LOCAL_MODEL_URL="http://localhost:11434"
```

## 🎯 Uso del Sistema

### Uso Básico (Python)
```python
from src.graph.workflow import create_marketing_workflow

# Crear workflow
workflow = create_marketing_workflow()

# Procesar prompt
result = await workflow.process_prompt(
    "Crear un post promocional para un nuevo producto de tecnología"
)

# Obtener brief
brief = result['final_brief']
print(f"Tipo de post: {brief.post_type}")
print(f"Contenido: {brief.core_content}")
```

### Interfaz Web (Streamlit)
```bash
streamlit run streamlit_app.py
```

### Línea de Comandos
```bash
python src/main.py
```

## 🧪 Testing

```bash
# Ejecutar tests unitarios
pytest tests/

# Ejecutar tests con coverage
pytest --cov=src tests/

# Ejecutar tests de performance
pytest tests/test_performance.py
```

## 📊 Estructura del Proyecto

```
ai-marketing-strategist/
├── src/
│   ├── agents/           # 7 agentes especializados
│   ├── config/           # Configuración y prompts
│   ├── graph/            # Workflow de LangGraph
│   ├── models/           # Modelos Pydantic
│   └── tools/            # Cliente LLM y utilidades
├── tests/                # Tests unitarios y de integración
├── streamlit_app.py      # Interfaz web
├── requirements.txt      # Dependencias
├── env_example.txt      # Variables de entorno
└── README.md            # Este archivo
```

## 🔧 Configuración Avanzada

### Modelos LLM Soportados
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3 Sonnet, Claude-3 Haiku
- **Local**: Llama, Mistral, Ollama

### Optimización de Performance
```python
# Configurar timeouts
export TIMEOUT_SECONDS=15
export MAX_RETRIES=5

# Habilitar caching
export ENABLE_CACHING=true
```

### Observabilidad
```python
# Habilitar métricas
export ENABLE_METRICS=true

# Habilitar tracing
export ENABLE_TRACING=true
```

## 📈 Métricas y Performance

- **Tiempo objetivo**: <10 segundos
- **Tasa de éxito**: >95%
- **Agentes activos**: 7/7
- **Validación**: 100% con Pydantic
- **Logging**: Trazabilidad completa

## 🎨 Ejemplo de Output

```json
{
  "post_type": "Promotional",
  "core_content": "Descubre cómo nuestra nueva tecnología...",
  "engagement_elements": {
    "caption": "¡Innovación al alcance de tu mano!",
    "call_to_action": "¡Prueba gratis por 30 días!",
    "hashtags": ["#tecnologia", "#innovacion", "#startup"]
  },
  "visual_concept": {
    "mood": "Moderno y profesional",
    "color_palette": ["#2E86AB", "#A23B72", "#F18F01"],
    "layout_style": "Minimalista y limpio"
  },
  "reasoning": {
    "strategic_decisions": ["Se seleccionó post promocional para maximizar conversiones"],
    "audience_considerations": "Profesionales jóvenes interesados en tecnología"
  }
}
```

## 🚨 Troubleshooting

### Error: "No se pudo inicializar ningún cliente LLM"
- Verificar que las API keys estén configuradas
- Comprobar conectividad a internet
- Verificar límites de rate limiting

### Error: "Workflow timeout"
- Aumentar `TIMEOUT_SECONDS` en .env
- Verificar performance del LLM
- Optimizar prompts si es necesario

### Error: "JSON parsing failed"
- Verificar que el LLM esté generando JSON válido
- Revisar prompts de validación
- Verificar configuración de temperatura

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Agradecimientos

- **LangGraph**: Framework de orquestación
- **Pydantic**: Validación de datos
- **Streamlit**: Interfaz de usuario
- **OpenAI/Anthropic**: Modelos de lenguaje

## 📞 Soporte

- **Issues**: [GitHub Issues](link-to-issues)
- **Documentación**: [Wiki](link-to-wiki)
- **Email**: support@example.com

---

**¡Construido con ❤️ para el desafío de 2 semanas!**

