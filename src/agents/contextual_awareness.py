"""
Contextual Awareness Engine - Incorpora contexto externo y tendencias en tiempo real
"""
import logging
import time
from typing import Dict, Any
import random
from datetime import datetime

from tools.llm_client import LLMClient
from config.prompts import get_prompt_template, AGENT_TEMPLATES

logger = logging.getLogger(__name__)

class ContextualAwarenessEngine:
    """
    Agente que incorpora contexto externo y tendencias actuales para optimizar la estrategia
    """
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
        self.external_data = self._initialize_external_data()
    
    def _generate_current_external_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Genera datos externos simulados actuales con hashtags y tendencias específicas"""
        import random
        from datetime import datetime
        
        current_month = datetime.now().month
        current_day = datetime.now().day
        
        # Datos estacionales con hashtags específicos
        seasonal_data = {
            1: {
                "trends": ["New Year resolutions", "Winter sales", "Health trends", "Dry January"],
                "hashtags": ["#NewYearNewMe", "#2025Goals", "#HealthyLiving", "#WinterSale", "#FitnessMotivation"],
                "context": "Post-holiday health focus and fresh starts"
            },
            2: {
                "trends": ["Valentine's Day", "Winter fashion", "Self-love", "Cozy vibes"],
                "hashtags": ["#ValentinesDay", "#SelfLove", "#WinterFashion", "#CozyVibes", "#LoveYourself"],
                "context": "Romance and self-care emphasis"
            },
            3: {
                "trends": ["Spring cleaning", "Easter prep", "Outdoor activities", "Fresh starts"],
                "hashtags": ["#SpringCleaning", "#FreshStart", "#OutdoorLife", "#SpringVibes", "#Renewal"],
                "context": "Renewal and outdoor activity increase"
            },
            9: {
                "trends": ["Fall fashion", "Back to school", "Autumn aesthetics", "Cozy season"],
                "hashtags": ["#FallFashion", "#BackToSchool", "#AutumnVibes", "#CozyStyle", "#FallTrends"],
                "context": "Transition to autumn and educational focus"
            }
        }
        
        # Tendencias actuales de redes sociales con métricas
        trending_content = {
            "video_trends": {
                "formats": ["15-second tutorials", "Before/after reveals", "Day-in-the-life", "Product demos"],
                "engagement_boost": 2.3,
                "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"]
            },
            "hashtag_trends": {
                "general": ["#Authentic", "#Sustainable", "#SmallBusiness", "#Innovation", "#Community"],
                "engagement_rate": 0.045,
                "reach_multiplier": 1.4
            },
            "content_themes": {
                "trending": ["Sustainability", "Authenticity", "Behind-the-scenes", "Educational content"],
                "declining": ["Overly polished content", "Generic stock photos"]
            }
        }
        
        # Obtener datos del mes actual
        month_data = seasonal_data.get(current_month, {
            "trends": ["General seasonal trends"],
            "hashtags": ["#Trending", "#Popular", "#Viral"],
            "context": "General seasonal context"
        })
        
        # Simular eventos actuales basados en industria
        industry_events = self._get_industry_specific_events(state)
        
        return {
            "seasonal_trends": month_data["trends"],
            "trending_hashtags": month_data["hashtags"] + trending_content["hashtag_trends"]["general"][:3],
            "seasonal_context": month_data["context"],
            "market_sentiment": random.choice(["Optimistic", "Stable", "Growth-focused"]),
            "social_media_trends": trending_content["video_trends"]["formats"],
            "industry_events": industry_events,
            "engagement_opportunities": {
                "video_boost": trending_content["video_trends"]["engagement_boost"],
                "hashtag_reach": trending_content["hashtag_trends"]["reach_multiplier"],
                "optimal_formats": trending_content["video_trends"]["formats"][:2]
            },
            "weather_context": self._get_weather_context(current_month),
            "competitive_landscape": "Increased focus on authentic, value-driven content"
        }
    
    def _get_industry_specific_events(self, state: Dict[str, Any]) -> list:
        """Genera eventos específicos de la industria"""
        # Analizar el prompt para determinar industria
        prompt = state.get("input_prompt", "").lower()
        
        if any(word in prompt for word in ["fitness", "health", "wellness", "gym"]):
            return ["Fitness September challenge", "Wellness awareness month", "Healthy lifestyle trends"]
        elif any(word in prompt for word in ["tech", "app", "software", "digital"]):
            return ["Tech innovation week", "Digital transformation trends", "App launch season"]
        elif any(word in prompt for word in ["fashion", "style", "clothing"]):
            return ["Fashion Week", "Seasonal style transitions", "Sustainable fashion movement"]
        else:
            return ["Industry growth trends", "Market expansion", "Consumer behavior shifts"]
    
    def _get_weather_context(self, month: int) -> str:
        """Genera contexto climático apropiado"""
        weather_contexts = {
            1: "Cold winter weather, indoor activities preferred",
            2: "Late winter, anticipation for spring",
            3: "Early spring, outdoor activities resuming",
            9: "Early fall, comfortable outdoor weather",
            10: "Mid fall, cozy indoor preferences increasing",
            11: "Late fall, holiday preparation weather",
            12: "Winter holiday season, indoor gatherings"
        }
        return weather_contexts.get(month, "Seasonal weather appropriate for outdoor activities")
    
    def _initialize_external_data(self) -> Dict[str, Any]:
        """Inicializa datos externos simulados"""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Simular datos externos relevantes
        seasonal_trends = {
            1: ["New Year resolutions", "Health & fitness", "Productivity"],
            2: ["Valentine's Day", "Love & relationships", "Self-care"],
            3: ["Spring cleaning", "Renewal", "Fresh starts"],
            4: ["Easter", "Spring fashion", "Outdoor activities"],
            5: ["Mother's Day", "Graduation", "Summer prep"],
            6: ["Father's Day", "Summer vacation", "Outdoor sports"],
            7: ["Summer sales", "Vacation", "Beach activities"],
            8: ["Back to school", "Productivity", "Organization"],
            9: ["Fall fashion", "Autumn", "Cozy vibes"],
            10: ["Halloween", "Spooky content", "Autumn activities"],
            11: ["Black Friday", "Thanksgiving", "Gratitude"],
            12: ["Christmas", "Holiday shopping", "Year-end"]
        }
        
        return {
            "current_trends": seasonal_trends.get(current_month, ["General trends"]),
            "market_sentiment": random.choice(["bullish", "bearish", "neutral"]),
            "competitor_activity": "high",
            "economic_indicators": {
                "consumer_confidence": random.uniform(0.6, 0.9),
                "spending_trend": random.choice(["increasing", "stable", "decreasing"])
            },
            "social_media_trends": [
                "Short-form video content",
                "Authentic storytelling",
                "User-generated content",
                "Sustainability focus"
            ],
            "current_events": [
                "Technology innovation focus",
                "Remote work trends",
                "Digital transformation"
            ]
        }
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado e incorpora contexto externo y tendencias
        
        Args:
            state: Estado del workflow con análisis previo
            
        Returns:
            Estado actualizado con contexto externo
        """
        start_time = time.time()
        
        try:
            self.logger.info("Iniciando análisis de contexto externo")
            
            # Generar datos externos actualizados
            external_data = self._generate_current_external_data(state)
            
            # Identificar tendencias relevantes
            relevant_trends = self._identify_relevant_trends(state, external_data)
            
            # Preparar prompt específico según idioma
            language_config = state.get("language_config", {})
            language = language_config.get("language", "es")
            
            base_strategy = self._summarize_base_strategy(state)
            
            template = get_prompt_template(AGENT_TEMPLATES["contextual_awareness"], language)
            prompt = template.format(
                base_strategy=base_strategy,
                external_data=str(external_data),
                trends=str(relevant_trends)
            )
            
            # Llamar al LLM
            self.logger.info("Generando ajustes contextuales con LLM")
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con ajustes contextuales"
            )
            
            # Parsear respuesta
            contextual_insights = self._parse_contextual_insights(response)
            
            # Crear recomendaciones finales
            final_recommendations = self._create_final_recommendations(state, contextual_insights)
            
            # Crear estructura completa de datos contextuales
            contextual_data = {
                "external_data": external_data,
                "relevant_trends": relevant_trends,
                "contextual_insights": contextual_insights,
                "final_recommendations": final_recommendations,
            }
            
            # Actualizar estado usando función de estado
            from graph.state import update_state_with_context, WorkflowState
            if isinstance(state, dict):
                workflow_state = WorkflowState(**state)
                workflow_state = update_state_with_context(workflow_state, contextual_data)
                state.update(workflow_state.dict())
            else:
                state = update_state_with_context(state, contextual_data)
            
            # Log del proceso
            processing_time = time.time() - start_time
            self.logger.info(f"Análisis contextual completado en {processing_time:.2f}s")
            
            # Registrar tiempo del agente
            if isinstance(state, dict):
                if "agent_timings" not in state:
                    state["agent_timings"] = {}
                state["agent_timings"]["contextual_awareness"] = processing_time
            else:
                if not hasattr(state, 'agent_timings'):
                    state.agent_timings = {}
                state.agent_timings["contextual_awareness"] = processing_time
            
            return state
            
        except Exception as e:
            error_msg = f"Error en Contextual Awareness: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
            return state
    
    def _generate_current_external_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Genera datos externos actualizados"""
        # Simular llamada a APIs externas
        platform = getattr(state["prompt_analysis"], 'platform', 'general')
        industry = self._infer_industry(state)
        
        return {
            **self.external_data,
            "platform_specific": {
                platform: {
                    "trending_hashtags": self._get_trending_hashtags(platform),
                    "optimal_posting_time": self._get_optimal_time(platform),
                    "content_saturation": random.choice(["low", "medium", "high"])
                }
            },
            "industry_insights": {
                industry: {
                    "growth_rate": random.uniform(0.02, 0.15),
                    "competition_level": random.choice(["low", "medium", "high"]),
                    "innovation_focus": random.choice(["AI", "sustainability", "user experience"])
                }
            }
        }
    
    def _identify_relevant_trends(self, state: Dict[str, Any], external_data: Dict[str, Any]) -> list:
        """Identifica tendencias relevantes para el contenido"""
        post_type = state["post_type"].value
        brand_values = getattr(state.get("brand_voice"), 'values', [])
        
        relevant_trends = []
        
        # Tendencias estacionales
        relevant_trends.extend(external_data["current_trends"][:2])
        
        # Tendencias de redes sociales
        relevant_trends.extend(external_data["social_media_trends"][:2])
        
        # Tendencias específicas por tipo de post
        if post_type == "Launch":
            relevant_trends.append("Product launch strategies")
        elif post_type == "Educational":
            relevant_trends.append("Educational content engagement")
        
        return relevant_trends[:5]  # Limitar a 5 tendencias más relevantes
    
    def _infer_industry(self, state: Dict[str, Any]) -> str:
        """Infiere la industria basada en el contenido"""
        key_facts = getattr(state["prompt_analysis"], 'key_facts', [])
        
        # Análisis simple de palabras clave
        tech_keywords = ["saas", "app", "software", "tech", "digital"]
        health_keywords = ["fitness", "health", "wellness", "medical"]
        business_keywords = ["business", "corporate", "professional", "enterprise"]
        
        content_text = " ".join(key_facts).lower()
        
        if any(keyword in content_text for keyword in tech_keywords):
            return "technology"
        elif any(keyword in content_text for keyword in health_keywords):
            return "health_wellness"
        elif any(keyword in content_text for keyword in business_keywords):
            return "business_services"
        else:
            return "general"
    
    def _get_trending_hashtags(self, platform: str) -> list:
        """Obtiene hashtags trending simulados por plataforma"""
        hashtag_db = {
            "linkedin": ["#Innovation", "#Leadership", "#BusinessGrowth", "#Productivity"],
            "instagram": ["#Trending", "#Viral", "#Aesthetic", "#Lifestyle"],
            "tiktok": ["#FYP", "#Viral", "#Trending", "#Challenge"],
            "twitter": ["#Breaking", "#Trending", "#News", "#Discussion"]
        }
        return hashtag_db.get(platform.lower(), ["#Trending", "#Popular"])
    
    def _get_optimal_time(self, platform: str) -> str:
        """Obtiene tiempo óptimo de publicación por plataforma"""
        optimal_times = {
            "linkedin": "9-11 AM weekdays",
            "instagram": "6-9 PM daily",
            "tiktok": "7-9 PM daily",
            "twitter": "12-3 PM weekdays"
        }
        return optimal_times.get(platform.lower(), "6-9 PM daily")
    
    def _summarize_base_strategy(self, state: Dict[str, Any]) -> str:
        """Resume la estrategia base actual"""
        elements = []
        elements.append(f"Tipo: {state['post_type'].value}")
        
        if state.get("visual_format_recommendation"):
            elements.append(f"Formato: {state['visual_format_recommendation']['recommended_format']}")
        
        if state.get("core_content"):
            elements.append(f"Contenido: {state['core_content'][:100]}...")
        
        return " | ".join(elements)
    
    def _parse_contextual_insights(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea los insights contextuales del LLM"""
        return {
            "contextual_adjustments": response.get("contextual_adjustments", []),
            "trend_integration": response.get("trend_integration", []),
            "competitive_advantages": response.get("competitive_advantages", []),
            "timing_considerations": response.get("timing_considerations", []),
            "risk_factors": response.get("risk_factors", [])
        }
    
    def _create_final_recommendations(self, state: Dict[str, Any], insights: Dict[str, Any]) -> Dict[str, Any]:
        """Crea recomendaciones finales integradas"""
        return {
            "priority_actions": insights["contextual_adjustments"][:3],
            "trend_opportunities": insights["trend_integration"][:2],
            "competitive_edge": insights["competitive_advantages"][:2],
            "optimal_timing": insights["timing_considerations"][:1],
            "risk_mitigation": insights["risk_factors"][:2]
        }
