# AI Marketing Strategist - Cloud Deployment

## 🚀 Rama Cloud-Only

Esta rama está optimizada para deployment en plataformas cloud gratuitas usando **solo modelos en la nube** (sin Ollama).

## 📋 Características

- ✅ **Solo modelos cloud**: Google AI, Groq, OpenAI, Anthropic
- ✅ **Sin dependencias locales**: No requiere Ollama
- ✅ **Optimizado para hosting gratuito**: Railway, Render, Streamlit Cloud
- ✅ **12 agentes especializados** con RAG system
- ✅ **Interface mejorada** para producción

## 🔧 Configuración

### Variables de Entorno Requeridas

```bash
# API Keys (al menos una requerida)
GOOGLE_API_KEY=tu_google_api_key
GROQ_API_KEY=tu_groq_api_key
OPENAI_API_KEY=tu_openai_api_key  # Opcional
ANTHROPIC_API_KEY=tu_anthropic_key  # Opcional

# Configuración adicional
PORT=8501  # Puerto para el servidor
```

## 🌐 Plataformas de Deployment Gratuitas

### 1. **Railway** (Recomendado)
- ✅ 500 horas gratis/mes
- ✅ Variables de entorno fáciles
- ✅ Deployment automático desde Git

**Pasos:**
1. Conecta tu repo a Railway
2. Configura las variables de entorno
3. Deploy automático

### 2. **Render**
- ✅ 750 horas gratis/mes
- ✅ SSL automático
- ✅ Health checks incluidos

**Pasos:**
1. Conecta tu repo a Render
2. Usa `render.yaml` para configuración
3. Configura variables de entorno

### 3. **Streamlit Cloud**
- ✅ Gratis para proyectos públicos
- ✅ Integración directa con GitHub
- ✅ Optimizado para Streamlit

**Pasos:**
1. Sube tu repo a GitHub
2. Conecta en share.streamlit.io
3. Configura secrets para API keys

## 🚀 Deploy Rápido

### Opción 1: Railway
```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login y deploy
railway login
railway link
railway up
```

### Opción 2: Render
```bash
# 1. Conectar repo en render.com
# 2. Usar render.yaml automáticamente
# 3. Configurar variables de entorno
```

### Opción 3: Docker Local
```bash
# Build imagen
docker build -t ai-marketing-strategist .

# Run con variables de entorno
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY=tu_key \
  -e GROQ_API_KEY=tu_key \
  ai-marketing-strategist
```

## 📁 Archivos Específicos de Cloud

- `streamlit_cloud.py` - App optimizada para producción
- `requirements-cloud.txt` - Dependencias sin Ollama
- `src/config/cloud_settings.py` - Configuración cloud-only
- `Dockerfile` - Para deployment containerizado
- `railway.json` - Configuración Railway
- `render.yaml` - Configuración Render
- `.streamlit/config.toml` - Configuración Streamlit

## 🔑 Obtener API Keys

### Google AI (Gemini)
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea un nuevo proyecto
3. Genera API key
4. **Gratis**: 60 requests/minuto

### Groq
1. Ve a [Groq Console](https://console.groq.com/keys)
2. Crea cuenta gratuita
3. Genera API key
4. **Gratis**: 30 requests/minuto

### OpenAI (Opcional)
1. Ve a [OpenAI Platform](https://platform.openai.com/api-keys)
2. Crea API key
3. **Pago**: $5 mínimo de crédito

### Anthropic (Opcional)
1. Ve a [Anthropic Console](https://console.anthropic.com/)
2. Crea API key
3. **Pago**: Créditos requeridos

## ⚡ Optimizaciones Cloud

- **Timeout reducido**: 20s vs 30s local
- **Tokens limitados**: 1500 vs 2000 local
- **Cache optimizado**: 12h vs 24h local
- **Logging mínimo**: Solo warnings en producción
- **Sin procesamiento paralelo**: Evita rate limits

## 🧪 Prueba Local

```bash
# Instalar dependencias cloud
pip install -r requirements-cloud.txt

# Configurar variables de entorno
export GOOGLE_API_KEY=tu_key
export GROQ_API_KEY=tu_key

# Ejecutar app cloud
streamlit run streamlit_cloud.py
```

## 📊 Monitoreo

La app incluye:
- ✅ Health checks automáticos
- ✅ Estado de APIs en sidebar
- ✅ Métricas de performance
- ✅ Manejo de errores robusto

## 🔒 Seguridad

- ✅ API keys via variables de entorno
- ✅ Sin logs de keys sensibles
- ✅ Timeouts para prevenir ataques
- ✅ Validación de inputs

## 📈 Escalabilidad

Para mayor tráfico:
1. **Railway Pro**: $5/mes, más recursos
2. **Render Plus**: $7/mes, más memoria
3. **Heroku**: Dynos escalables
4. **Google Cloud Run**: Pay-per-use

## 🆘 Troubleshooting

### Error: "No API keys configured"
- Verifica que las variables de entorno estén configuradas
- Al menos una API key debe estar presente

### Error: "Rate limit exceeded"
- Las APIs gratuitas tienen límites
- Espera unos minutos o usa otra API

### Error: "Timeout"
- Reduce `timeout_seconds` en cloud_settings.py
- Verifica conexión a internet

### App lenta
- Usa APIs más rápidas (Groq > Google > OpenAI)
- Reduce `max_tokens` en configuración

## 🎯 Próximos Pasos

1. **Deploy en Railway/Render**
2. **Configurar dominio personalizado**
3. **Monitorear uso de APIs**
4. **Optimizar performance según métricas**

---

🚀 **¡Tu AI Marketing Strategist está listo para la nube!**
