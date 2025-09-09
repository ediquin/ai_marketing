"""
Prompts específicos y optimizados para cada agente del sistema de marketing
Incluye versiones en español e inglés para optimizar tokens
"""

# ========== PROMPT ANALYZER ==========
# Versión en español
PROMPT_ANALYZER_TEMPLATE_ES = """
Analiza este prompt de marketing y extrae información estructurada:

PROMPT: "{prompt}"

Extrae y estructura la siguiente información:

1. OBJETIVO: ¿Qué quiere lograr? (ventas, awareness, engagement, etc.)
2. AUDIENCIA: ¿A quién se dirige? (demografía, psychografía)
3. BRAND CUES: ¿Qué indica sobre la marca? (tono, personalidad, valores)
4. HECHOS CLAVE: Datos específicos mencionados (nombres, fechas, números)
5. URGENCIA: ¿Hay elementos de urgencia temporal?
6. PLATAFORMA: ¿Se menciona alguna plataforma específica?
7. TONO: Indicadores de tono de comunicación
8. METAS: Objetivos específicos de contenido

Responde SOLO en formato JSON válido con esta estructura:
{{
    "objective": "string",
    "audience": "string", 
    "brand_cues": ["string"],
    "key_facts": ["string"],
    "urgency": "string o null",
    "platform": "string o null",
    "tone_indicators": ["string"],
    "content_goals": ["string"]
}}

IMPORTANTE: Solo responde con el JSON, sin texto adicional.
"""

# Versión en inglés
PROMPT_ANALYZER_TEMPLATE_EN = """
Analyze this marketing prompt and extract structured information:

PROMPT: "{prompt}"

Extract and structure the following information:

1. OBJECTIVE: What does it want to achieve? (sales, awareness, engagement, etc.)
2. AUDIENCE: Who is it targeting? (demographics, psychographics)
3. BRAND CUES: What does it indicate about the brand? (tone, personality, values)
4. KEY FACTS: Specific data mentioned (names, dates, numbers)
5. URGENCY: Are there temporal urgency elements?
6. PLATFORM: Is any specific platform mentioned?
7. TONE: Communication tone indicators
8. GOALS: Specific content objectives

Respond ONLY in valid JSON format with this structure:
{{
    "objective": "string",
    "audience": "string", 
    "brand_cues": ["string"],
    "key_facts": ["string"],
    "urgency": "string or null",
    "platform": "string or null",
    "tone_indicators": ["string"],
    "content_goals": ["string"]
}}

IMPORTANT: Only respond with the JSON, no additional text.
"""

# ========== POST CLASSIFIER ==========
# Versión en español
POST_CLASSIFIER_TEMPLATE_ES = """
Basándote en este análisis, clasifica el tipo de post más efectivo:

ANÁLISIS DEL PROMPT:
{analysis}

TIPOS DISPONIBLES:
- Launch: Lanzamiento de producto/servicio
- Educational: Educar sobre beneficios/procesos
- Promotional: Ofertas, descuentos, promociones
- Storytelling: Narrativa de marca, testimonios
- Engagement: Preguntas, polls, contenido interactivo

Responde SOLO con el tipo más apropiado y una breve justificación en formato JSON:
{{
    "post_type": "Launch|Educational|Promotional|Storytelling|Engagement",
    "justification": "Breve explicación de por qué este tipo es el más apropiado"
}}

IMPORTANTE: Solo responde con el JSON, sin texto adicional.
"""

# Versión en inglés
POST_CLASSIFIER_TEMPLATE_EN = """
Based on this analysis, classify the most effective post type:

PROMPT ANALYSIS:
{analysis}

AVAILABLE TYPES:
- Launch: Product/service launch
- Educational: Educate about benefits/processes
- Promotional: Offers, discounts, promotions
- Storytelling: Brand narrative, testimonials
- Engagement: Questions, polls, interactive content

Respond ONLY with the most appropriate type and brief justification in JSON format:
{{
    "post_type": "Launch|Educational|Promotional|Storytelling|Engagement",
    "justification": "Brief explanation of why this type is most appropriate"
}}

IMPORTANT: Only respond with the JSON, no additional text.
"""

# ========== BRAND VOICE AGENT ==========
# Versión en español
BRAND_VOICE_TEMPLATE_ES = """
Basándote en el análisis del prompt, define la voz de marca:

ANÁLISIS: {analysis}
TIPO DE POST: {post_type}

Define la voz de marca considerando:
1. TONO: General de comunicación
2. PERSONALIDAD: Características humanas de la marca
3. ESTILO: Forma de expresarse
4. VALORES: Principios fundamentales
5. NIVEL DE LENGUAJE: Formal, casual, técnico

Responde en formato JSON:
{{
    "tone": "string",
    "personality": "string",
    "style": "string", 
    "values": ["string"],
    "language_level": "string"
}}

IMPORTANTE: Solo responde con el JSON, sin texto adicional.
"""

# Versión en inglés
BRAND_VOICE_TEMPLATE_EN = """
Based on the prompt analysis, define the brand voice:

ANALYSIS: {analysis}
POST TYPE: {post_type}

Define the brand voice considering:
1. TONE: General communication tone
2. PERSONALITY: Human characteristics of the brand
3. STYLE: Way of expressing
4. VALUES: Fundamental principles
5. LANGUAGE LEVEL: Formal, casual, technical

Respond in JSON format:
{{
    "tone": "string",
    "personality": "string",
    "style": "string", 
    "values": ["string"],
    "language_level": "string"
}}

IMPORTANT: Only respond with the JSON, no additional text.
"""

# ========== FACT GROUNDING ==========
# Versión en español
FACT_GROUNDING_TEMPLATE_ES = """
Valida y estructura los hechos clave del prompt de marketing:

PROMPT: {prompt}
HECHOS IDENTIFICADOS: {key_facts}

Para cada hecho, proporciona:
1. VERIFICACIÓN: Estado de verificación
2. FUENTES: Posibles fuentes de datos
3. ESTADÍSTICAS: Datos numéricos relevantes
4. CONTEXTO: Información adicional necesaria

Responde en formato JSON:
{{
    "key_facts": ["string"],
    "data_sources": ["string"],
    "statistics": ["string"] o null,
    "verification_status": "string"
}}

IMPORTANTE: Solo responde con el JSON, sin texto adicional.
"""

# Versión en inglés
FACT_GROUNDING_TEMPLATE_EN = """
Validate and structure key facts from the marketing prompt:

PROMPT: {prompt}
IDENTIFIED FACTS: {key_facts}

For each fact, provide:
1. VERIFICATION: Verification status
2. SOURCES: Possible data sources
3. STATISTICS: Relevant numerical data
4. CONTEXT: Additional necessary information

Respond in JSON format:
{{
    "key_facts": ["string"],
    "data_sources": ["string"],
    "statistics": ["string"] or null,
    "verification_status": "string"
}}

IMPORTANT: Only respond with the JSON, no additional text.
"""

# ========== TEXT GENERATOR ==========
# Versión en español
TEXT_GENERATOR_TEMPLATE_ES = """
Genera el contenido principal de un post de marketing:

ANÁLISIS: {analysis}
TIPO: {post_type}
VOZ DE MARCA: {brand_voice}
HECHOS: {facts}

REQUISITOS:
- Contenido coherente y atractivo
- Alineado con la voz de marca
- Basado en hechos verificados
- Optimizado para engagement
- Longitud apropiada para redes sociales

Genera el contenido principal del post. Responde SOLO con el texto del post, sin formato adicional.
"""

# Versión en inglés
TEXT_GENERATOR_TEMPLATE_EN = """
Generate the main content for a marketing post:

ANALYSIS: {analysis}
TYPE: {post_type}
BRAND VOICE: {brand_voice}
FACTS: {facts}

REQUIREMENTS:
- Coherent and engaging content
- Aligned with brand voice
- Based on verified facts
- Optimized for engagement
- Appropriate length for social media

Generate the main post content. Respond ONLY with the post text, no additional formatting.
"""

# ========== CAPTION CREATOR ==========
# Versión en español
CAPTION_CREATOR_TEMPLATE_ES = """
Crea elementos de engagement para el post:

CONTENIDO PRINCIPAL: {core_content}
TIPO DE POST: {post_type}
VOZ DE MARCA: {brand_voice}
OBJETIVO: {objective}

Crea:
1. CAPTION: Texto atractivo que acompañe el contenido
2. CTA: Llamada a la acción clara
3. HASHTAGS: Hashtags relevantes y populares
4. GANCHOS: Elementos para generar engagement
5. PREGUNTAS: Preguntas para interacción

Responde en formato JSON:
{{
    "caption": "string",
    "call_to_action": "string",
    "hashtags": ["string"],
    "engagement_hooks": ["string"],
    "questions": ["string"]
}}

IMPORTANTE: Solo responde con el JSON, sin texto adicional.
"""

# Versión en inglés
CAPTION_CREATOR_TEMPLATE_EN = """
Create engagement elements for the post:

MAIN CONTENT: {core_content}
POST TYPE: {post_type}
BRAND VOICE: {brand_voice}
OBJECTIVE: {objective}

Create:
1. CAPTION: Engaging text to accompany the content
2. CTA: Clear call to action
3. HASHTAGS: Relevant and popular hashtags
4. HOOKS: Elements to generate engagement
5. QUESTIONS: Questions for interaction

Respond in JSON format:
{{
    "caption": "string",
    "call_to_action": "string",
    "hashtags": ["string"],
    "engagement_hooks": ["string"],
    "questions": ["string"]
}}

IMPORTANT: Only respond with the JSON, no additional text.
"""

# ========== VISUAL CONCEPT ==========
# Versión en español
VISUAL_CONCEPT_TEMPLATE_ES = """
Genera un concepto visual detallado para el diseñador:

CONTENIDO: {core_content}
TIPO: {post_type}
VOZ DE MARCA: {brand_voice}
OBJETIVO: {objective}

Define:
1. MOOD: Estado de ánimo visual
2. PALETA: Colores apropiados
3. IMAGEN: Tipo de imágenes a usar
4. LAYOUT: Estilo de composición
5. ELEMENTOS: Componentes visuales específicos
6. NOTAS: Instrucciones para el diseñador

Responde en formato JSON:
{{
    "mood": "string",
    "color_palette": ["string"],
    "imagery_type": "string",
    "layout_style": "string",
    "visual_elements": ["string"],
    "design_notes": "string"
}}

IMPORTANTE: Solo responde con el JSON, sin texto adicional.
"""

# Versión en inglés
VISUAL_CONCEPT_TEMPLATE_EN = """
Generate a detailed visual concept for the designer:

CONTENT: {core_content}
TYPE: {post_type}
BRAND VOICE: {brand_voice}
OBJECTIVE: {objective}

Define:
1. MOOD: Visual mood
2. PALETTE: Appropriate colors
3. IMAGERY: Type of images to use
4. LAYOUT: Composition style
5. ELEMENTS: Specific visual components
6. NOTES: Instructions for the designer

Respond in JSON format:
{{
    "mood": "string",
    "color_palette": ["string"],
    "imagery_type": "string",
    "layout_style": "string",
    "visual_elements": ["string"],
    "design_notes": "string"
}}

IMPORTANT: Only respond with the JSON, no additional text.
"""

# ========== REASONING MODULE ==========
# Versión en español
REASONING_MODULE_TEMPLATE_ES = """
Explica las decisiones estratégicas tomadas para este post:

ANÁLISIS COMPLETO: {full_analysis}
BRIEF FINAL: {final_brief}

Proporciona:
1. DECISIONES: Decisiones estratégicas clave
2. AUDIENCIA: Consideraciones sobre la audiencia
3. PLATAFORMA: Optimización para la plataforma
4. COMPETITIVO: Análisis competitivo (si aplica)
5. RIESGOS: Evaluación de riesgos y mitigaciones

Responde en formato JSON:
{{
    "strategic_decisions": ["string"],
    "audience_considerations": "string",
    "platform_optimization": "string",
    "competitive_analysis": "string" o null,
    "risk_assessment": "string"
}}

IMPORTANTE: Solo responde con el JSON, sin texto adicional.
"""

# Versión en inglés
REASONING_MODULE_TEMPLATE_EN = """
Explain the strategic decisions made for this post:

COMPLETE ANALYSIS: {full_analysis}
FINAL BRIEF: {final_brief}

Provide:
1. DECISIONS: Key strategic decisions
2. AUDIENCE: Audience considerations
3. PLATFORM: Platform optimization
4. COMPETITIVE: Competitive analysis (if applicable)
5. RISKS: Risk assessment and mitigations

Respond in JSON format:
{{
    "strategic_decisions": ["string"],
    "audience_considerations": "string",
    "platform_optimization": "string",
    "competitive_analysis": "string" or null,
    "risk_assessment": "string"
}}

IMPORTANT: Only respond with the JSON, no additional text.
"""

# ========== HELPER FUNCTIONS ==========
def get_prompt_template(base_name: str, language: str = "es"):
    """
    Obtiene el template de prompt correcto según el idioma
    
    Args:
        base_name: Nombre base del template (ej: "PROMPT_ANALYZER")
        language: Idioma ("es" o "en")
    
    Returns:
        Template de prompt en el idioma especificado
    """
    template_name = f"{base_name}_TEMPLATE_{language.upper()}"
    return globals().get(template_name, globals().get(f"{base_name}_TEMPLATE_ES"))

# ========== VISUAL FORMAT RECOMMENDER ==========
# Versión en español
VISUAL_FORMAT_RECOMMENDER_TEMPLATE_ES = """
Recomienda el formato visual más efectivo para este contenido:

ANÁLISIS: {analysis}
TIPO DE POST: {post_type}
PLATAFORMA: {platform}

Evalúa y recomienda entre:
1. IMAGE: Imagen estática
2. VIDEO: Video corto/reel
3. CAROUSEL: Carrusel de imágenes
4. INFOGRAPHIC: Infografía

Considera:
- Engagement potencial por formato
- Complejidad de producción
- Optimización por plataforma
- Tipo de contenido

Responde en formato JSON:
{{
    "recommended_format": "string",
    "justification": "string",
    "platform_optimization": "string",
    "engagement_potential": "high/medium/low",
    "production_complexity": "high/medium/low",
    "alternative_formats": ["string"]
}}

IMPORTANTE: Solo responde con el JSON, sin texto adicional.
"""

# Versión en inglés
VISUAL_FORMAT_RECOMMENDER_TEMPLATE_EN = """
Recommend the most effective visual format for this content:

ANALYSIS: {analysis}
POST TYPE: {post_type}
PLATFORM: {platform}

Evaluate and recommend between:
1. VIDEO: Short video/reel (highest engagement)
2. CAROUSEL: Image carousel 
3. IMAGE: Static image
4. INFOGRAPHIC: Infographic

Consider:
- Video content typically gets 2-3x higher engagement
- Platform preferences (TikTok/Reels favor video)
- Production complexity vs engagement potential
- Target audience behavior

For video campaigns or Gen Z audiences, strongly favor VIDEO format.

Respond in JSON format:
{{
    "recommended_format": "Video",
    "justification": "Detailed reasoning in English",
    "platform_optimization": "Platform-specific tips in English",
    "engagement_potential": "high/medium/low",
    "production_complexity": "high/medium/low",
    "alternative_formats": ["string"]
}}

IMPORTANT: Only respond with the JSON, no additional text. All text must be in English.
"""

# ========== VIDEO SCRIPTER ==========
# Versión en español
VIDEO_SCRIPTER_TEMPLATE_ES = """
Crea un script estructurado para video de formato corto:

CONTENIDO PRINCIPAL: {core_content}
FORMATO RECOMENDADO: {visual_format}
PLATAFORMA: {platform}
DURACIÓN OBJETIVO: {duration}

Crea un script con:
1. HOOK (0-3s): Captar atención inmediata
2. SETUP (3-8s): Establecer contexto
3. CONTENT (8-25s): Mensaje principal
4. CTA (25-30s): Llamada a la acción

Incluye:
- Texto/narración por segmento
- Indicaciones visuales
- Transiciones
- Elementos de engagement

Responde en formato JSON:
{{
    "script_segments": [
        {{
            "segment": "hook/setup/content/cta",
            "duration": "0-3s",
            "narration": "string",
            "visual_direction": "string",
            "text_overlay": "string"
        }}
    ],
    "engagement_elements": ["string"],
    "music_style": "string",
    "hashtags": ["string"]
}}
"""

# Versión en inglés
VIDEO_SCRIPTER_TEMPLATE_EN = """
Create a structured script for short-form video:

MAIN CONTENT: {core_content}
RECOMMENDED FORMAT: {visual_format}
PLATFORM: {platform}
TARGET DURATION: {duration}

Create a script with:
1. HOOK (0-3s): Capture immediate attention
2. SETUP (3-8s): Establish context
3. CONTENT (8-25s): Main message
4. CTA (25-30s): Call to action

Include:
- Text/narration per segment
- Visual directions
- Transitions
- Engagement elements

Respond in JSON format:
{{
    "script_segments": [
        {{
            "segment": "hook/setup/content/cta",
            "duration": "0-3s",
            "narration": "English narration text",
            "visual_direction": "English visual direction",
            "text_overlay": "English text overlay"
        }}
    ],
    "engagement_elements": ["English engagement elements"],
    "music_style": "English music style description",
    "hashtags": ["English hashtags"]
}}

IMPORTANT: All content must be in English only.
"""

# ========== RESULT OPTIMIZER ==========
# Versión en español
RESULT_OPTIMIZER_TEMPLATE_ES = """
Optimiza la estrategia basándote en datos de performance:

DATOS DE PERFORMANCE: {performance_data}
ESTRATEGIA ACTUAL: {current_strategy}
OPORTUNIDADES: {optimization_opportunities}

Analiza y optimiza:
1. Contenido para mayor engagement
2. Timing óptimo de publicación
3. Ajustes de formato visual
4. Tácticas de engagement específicas
5. Mitigación de riesgos

Responde en formato JSON:
{{
    "content_optimizations": ["string"],
    "timing_recommendations": ["string"],
    "format_adjustments": ["string"],
    "engagement_tactics": ["string"],
    "risk_mitigation": ["string"]
}}
"""

# Versión en inglés
RESULT_OPTIMIZER_TEMPLATE_EN = """
Act as a digital marketing strategist optimizing campaigns by integrating historical performance data and current contextual data.

HISTORICAL PERFORMANCE DATA: {performance_data}
CURRENT STRATEGY: {current_strategy}
OPTIMIZATION OPPORTUNITIES: {optimization_opportunities}

Provide a structured recommendation following this format:

1. RECOMMENDED FORMAT: Clearly state the optimal format (image, video, carousel, etc.)

2. HISTORICAL JUSTIFICATION: 
   - Compare performance metrics between formats (CTR, engagement rates)
   - Reference specific data points from similar past campaigns
   - Explain why this format outperformed others

3. CONTEXTUAL JUSTIFICATION:
   - Consider current trends, hashtags, seasonal factors
   - Integrate real-time opportunities
   - Explain timing advantages

4. CREATIVE PROPOSAL:
   - Suggest a specific creative concept adapted to current context
   - Include relevant trending hashtags
   - Propose visual/audio elements that leverage current trends

Respond in JSON format:
{{
    "recommended_format": "Specific format recommendation",
    "historical_justification": "Detailed comparison with past campaign data and metrics",
    "contextual_justification": "Current trends and real-time opportunities analysis",
    "creative_proposal": "Specific creative concept with trending elements",
    "performance_comparison": "Clear metrics comparison between formats",
    "trending_hashtags": ["#relevant", "#hashtags"],
    "optimal_timing": "Best posting time based on data"
}}

IMPORTANT: Use realistic simulated data if exact metrics aren't available. All content must be in English.
"""

# ========== CONTEXTUAL AWARENESS ==========
# Versión en español
CONTEXTUAL_AWARENESS_TEMPLATE_ES = """
Incorpora contexto externo y tendencias actuales:

ESTRATEGIA BASE: {base_strategy}
DATOS EXTERNOS: {external_data}
TENDENCIAS: {trends}

Ajusta la estrategia considerando:
1. Tendencias actuales relevantes
2. Eventos del momento
3. Contexto competitivo
4. Oportunidades emergentes
5. Factores estacionales

Responde en formato JSON:
{{
    "contextual_adjustments": ["string"],
    "trend_integration": ["string"],
    "competitive_advantages": ["string"],
    "timing_considerations": ["string"],
    "risk_factors": ["string"]
}}
"""

# Versión en inglés
CONTEXTUAL_AWARENESS_TEMPLATE_EN = """
Act as a real-time marketing intelligence engine that integrates current contextual data to optimize campaign performance.

BASE STRATEGY: {base_strategy}
EXTERNAL DATA: {external_data}
CURRENT TRENDS: {trends}

Analyze current context and provide actionable insights:

1. TRENDING HASHTAGS ANALYSIS:
   - Identify relevant trending hashtags for the campaign
   - Explain engagement potential of each hashtag
   - Suggest optimal hashtag combinations

2. SEASONAL/TEMPORAL OPPORTUNITIES:
   - Current seasonal trends affecting the target audience
   - Time-sensitive opportunities (events, holidays, cultural moments)
   - Weather/climate considerations for content

3. COMPETITIVE LANDSCAPE:
   - Current market sentiment and competitor activity
   - Content gaps and opportunities
   - Differentiation strategies

4. REAL-TIME OPTIMIZATION:
   - Optimal posting times based on current engagement patterns
   - Platform-specific trend adaptations
   - Audience behavior insights

Respond in JSON format:
{{
    "trending_hashtags": ["#specific", "#trending", "#hashtags"],
    "hashtag_analysis": "Detailed explanation of hashtag selection and engagement potential",
    "seasonal_opportunities": "Current seasonal trends and time-sensitive opportunities",
    "competitive_insights": "Market gaps and differentiation opportunities",
    "optimal_timing": "Best posting times and scheduling recommendations",
    "creative_adaptations": "Specific content adjustments for current trends",
    "engagement_boosters": ["Specific tactics to increase engagement"],
    "contextual_elements": "Weather, events, or cultural factors to incorporate"
}}

IMPORTANT: Focus on actionable, time-sensitive insights. All content must be in English.
"""

# Mapeo de templates por agente
AGENT_TEMPLATES = {
    "prompt_analyzer": "PROMPT_ANALYZER",
    "post_classifier": "POST_CLASSIFIER", 
    "brand_voice": "BRAND_VOICE",
    "fact_grounding": "FACT_GROUNDING",
    "text_generator": "TEXT_GENERATOR",
    "caption_creator": "CAPTION_CREATOR",
    "visual_concept": "VISUAL_CONCEPT",
    "reasoning_module": "REASONING_MODULE",
    "visual_format_recommender": "VISUAL_FORMAT_RECOMMENDER",
    "video_scripter": "VIDEO_SCRIPTER",
    "result_optimizer": "RESULT_OPTIMIZER",
    "contextual_awareness": "CONTEXTUAL_AWARENESS"
}

# Prompt para validación de JSON
JSON_VALIDATION_TEMPLATE = """
Valida que la siguiente respuesta sea un JSON válido y esté en el formato correcto:

RESPUESTA: {response}

Si es JSON válido, responde con "VALID". Si no, responde con "INVALID" y explica el error.

IMPORTANTE: Solo responde con "VALID" o "INVALID: [explicación del error]".
"""
