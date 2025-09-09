"""
Result-Based Optimizer - Optimiza recomendaciones basado en datos de performance simulados
"""
import logging
import time
from typing import Dict, Any
from src.tools.llm_client import LLMClient
from src.tools.realtime_data_client import RealTimeDataClient
from src.tools.marketing_rag_system import MarketingRAGSystem
from src.config.prompts import RESULT_OPTIMIZER_TEMPLATE_ES, RESULT_OPTIMIZER_TEMPLATE_EN
from src.config.settings import get_settings

logger = get_settings().getLogger(__name__)

class ResultOptimizer:
    """
    Agente que optimiza las recomendaciones usando datos de performance simulados
    """
    
    def __init__(self, llm_client: LLMClient, use_realtime_data: bool = False, enable_rag: bool = True):
        self.llm = llm_client
        self.logger = logging.getLogger(__name__)
        self.use_realtime_data = use_realtime_data
        self.enable_rag = enable_rag
        self.realtime_client = None
        
        # Inicializar sistema RAG
        self.rag_system = MarketingRAGSystem(enable_rag=enable_rag)
        try:
            from src.tools.marketing_rag_system import check_rag_dependencies
            self.rag_dependencies = check_rag_dependencies()
        except ImportError:
            self.rag_dependencies = {"chromadb": False, "sentence_transformers": False, "duckduckgo_search": False}
        
        # Base de datos de performance (fallback)
        self.performance_db = self._initialize_performance_db()
        
        # Log del estado del sistema
        if enable_rag and all(self.rag_dependencies.values()):
            self.logger.info("RAG system fully enabled with all dependencies")
        elif enable_rag:
            missing = [k for k, v in self.rag_dependencies.items() if not v]
            self.logger.warning(f"RAG system partially enabled. Missing: {missing}")
        else:
            self.logger.info("RAG system disabled, using traditional approach")
    
    def _initialize_performance_db(self) -> Dict[str, Any]:
        """Inicializa base de datos simulada de performance"""
        return {
            "post_types": {
                "Launch": {"avg_engagement": 0.045, "conversion_rate": 0.032},
                "Promotional": {"avg_engagement": 0.038, "conversion_rate": 0.028},
                "Educational": {"avg_engagement": 0.052, "conversion_rate": 0.019},
                "Testimonial": {"avg_engagement": 0.041, "conversion_rate": 0.035}
            },
            "visual_formats": {
                "Image": {"engagement_boost": 1.0, "production_cost": "low"},
                "Video": {"engagement_boost": 1.8, "production_cost": "high"},
                "Carousel": {"engagement_boost": 1.4, "production_cost": "medium"},
                "Infographic": {"engagement_boost": 1.2, "production_cost": "medium"}
            },
            "platforms": {
                "LinkedIn": {"business_conversion": 0.045, "peak_hours": "9-11 AM"},
                "Instagram": {"engagement_rate": 0.058, "peak_hours": "6-9 PM"},
                "TikTok": {"viral_potential": 0.012, "peak_hours": "7-9 PM"},
                "Twitter": {"reach_multiplier": 1.3, "peak_hours": "12-3 PM"}
            }
        }
    
    async def process(self, state) -> Dict[str, Any]:
        """
        Procesa el estado y optimiza las recomendaciones basado en datos de performance
        
        Args:
            state: Estado del workflow con análisis previo
            
        Returns:
            Estado actualizado con optimizaciones
        """
        start_time = time.time()
        try:
            self.logger.info("Iniciando optimización basada en resultados")
            
            # Obtener datos necesarios del estado
            post_type = getattr(state.get("post_classification", {}), 'post_type', 'promotional')
            platform = getattr(state.get("prompt_analysis", {}), 'platform', 'Instagram')
            visual_format = getattr(state.get("visual_format_recommendation", {}), 'recommended_format', 'Image')
            
            # Determinar industria del prompt para datos específicos
            industry = self._extract_industry_from_prompt(state.get("input_prompt", ""))
            
            # Generar insights de performance usando la mejor fuente disponible
            if self.enable_rag:
                insights = await self._get_rag_enhanced_insights(industry, platform, visual_format, post_type, state.get("input_prompt", ""))
            elif self.use_realtime_data:
                insights = await self._get_realtime_performance_insights(industry, platform, visual_format, post_type)
            else:
                insights = self._generate_performance_insights(post_type, platform, visual_format)
            
            # Crear recomendaciones de optimización
            recommendations = self._create_optimization_recommendations(state, insights)
            
            # Detectar idioma
            detected_language = state.get("detected_language", "es")
            
            # Preparar datos para el prompt con información de fuente
            data_source = self._get_data_source_description()
            performance_data = f"""
            Data Source: {data_source}
            Post Type: {post_type}
            Platform: {platform}
            Visual Format: {visual_format}
            Expected Engagement: {insights.get('expected_engagement_rate', insights.get('projected_metrics', {}).get('expected_engagement_rate', 0.045))}
            Confidence Score: {insights.get('confidence_score', 0.75)}
            Historical Performance: {insights.get('historical_performance', {})}
            Trending Hashtags: {insights.get('trending_hashtags', [])}
            RAG Enhanced: {insights.get('rag_enabled', False)}
            """
            
            current_strategy = f"""
            Generated Content: {getattr(state.get('generated_content', {}), 'main_text', 'N/A')}
            Caption: {getattr(state.get('caption_with_cta', {}), 'caption', 'N/A')}
            Visual Concept: {getattr(state.get('visual_concept', {}), 'concept_description', 'N/A')}
            """
            
            optimization_opportunities = "\n".join(recommendations)
            
            # Seleccionar template según idioma
            template = RESULT_OPTIMIZER_TEMPLATE_EN if is_english else RESULT_OPTIMIZER_TEMPLATE_ES
            
            prompt = template.format(
                performance_data=performance_data,
                current_strategy=current_strategy,
                optimization_opportunities=optimization_opportunities
            )
            
            # Generar optimizaciones
            response = await self.llm.generate_structured(
                prompt=prompt,
                expected_format="JSON con optimizaciones"
            )
            
            # Actualizar estado
            state = self._update_result_optimization_state(state, {
                "optimization_response": response,
                "performance_insights": insights,
                "recommendations": recommendations,
                "confidence_score": insights.get('confidence_score', 0.75),
                "data_source": data_source,
                "realtime_enabled": self.use_realtime_data,
                "rag_enabled": self.enable_rag,
                "rag_dependencies": self.rag_dependencies
            })
            
            self.logger.info(f"Optimización basada en resultados completada usando {data_source}")
            # Log del proceso
            processing_time = time.time() - start_time
            self.logger.info(f"Optimización completada en {processing_time:.2f}s")
            
            # Registrar tiempo del agente
            if isinstance(state, dict):
                if "agent_timings" not in state:
                    state["agent_timings"] = {}
                state["agent_timings"]["result_optimizer"] = processing_time
            else:
                if not hasattr(state, 'agent_timings'):
                    state.agent_timings = {}
                state.agent_timings["result_optimizer"] = processing_time
            
            return state
            
        except Exception as e:
            error_msg = f"Error en Result Optimizer: {str(e)}"
            self.logger.error(error_msg)
            state["errors"].append(error_msg)
            return state
    
    def _extract_industry_from_prompt(self, prompt: str) -> str:
        """Extrae la industria del prompt para datos específicos"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["fitness", "gym", "health", "wellness", "workout"]):
            return "fitness"
        elif any(word in prompt_lower for word in ["fashion", "clothing", "style", "apparel"]):
            return "fashion"
        elif any(word in prompt_lower for word in ["tech", "app", "software", "digital", "technology"]):
            return "tech"
        elif any(word in prompt_lower for word in ["food", "restaurant", "recipe", "cooking"]):
            return "food"
        elif any(word in prompt_lower for word in ["beauty", "cosmetics", "skincare"]):
            return "beauty"
        else:
            return "general"
    
    async def _get_realtime_performance_insights(self, industry: str, platform: str, visual_format: str, post_type: str) -> Dict[str, Any]:
        """Obtiene insights de performance usando datos en tiempo real"""
        try:
            if not self.realtime_client:
                self.realtime_client = RealTimeDataClient()
            
            async with self.realtime_client as client:
                # Obtener datos de mercado en tiempo real
                market_data = await client.get_real_time_marketing_data(
                    industry=industry,
                    platform=platform,
                    campaign_type=post_type
                )
                
                # Convertir a formato compatible con el sistema existente
                base_engagement = market_data.engagement_rates.get(visual_format, 0.045)
                platform_data = market_data.platform_metrics.get(platform, {})
                
                # Calcular format_boost basado en el formato visual
                format_boost = 1.0
                if visual_format == "Video":
                    format_boost = 1.8
                elif visual_format == "Carousel":
                    format_boost = 1.4
                
                return {
                    "historical_performance": {
                        "ctr": base_engagement * 0.7,  # CTR típicamente menor que engagement
                        "engagement": base_engagement,
                        "average_reach": int(base_engagement * 50000)  # Estimación basada en engagement
                    },
                    "projected_metrics": {
                        "expected_ctr": round(base_engagement * 0.8, 3),
                        "expected_engagement_rate": round(base_engagement, 3),
                        "estimated_reach": int(base_engagement * 60000)
                    },
                    "trending_hashtags": market_data.trending_hashtags[:5],
                    "platform_insights": {
                        "optimal_posting_time": platform_data.get("peak_hours", "7-9 PM"),
                        "platform_boost": platform_data.get("engagement_boost", 1.0),
                        "reach_potential": platform_data.get("reach_multiplier", 1.0)
                    },
                    "seasonal_trends": market_data.seasonal_trends,
                    "competitive_insights": market_data.competitive_insights,
                    "confidence_score": 0.85,  # Mayor confianza con datos reales
                    "data_timestamp": market_data.timestamp.isoformat(),
                    "data_source": "real_time",
                    "format_boost": format_boost
                }
                
        except Exception as e:
            self.logger.warning(f"Error obteniendo datos en tiempo real, usando simulados: {e}")
            # Fallback a datos simulados
            return self._generate_performance_insights(post_type, platform, visual_format)
    
    def _get_data_source_description(self) -> str:
        """Obtiene descripción de la fuente de datos activa"""
        if self.enable_rag and all(self.rag_dependencies.values()):
            return "RAG System with Real Marketing Benchmarks"
        elif self.enable_rag:
            missing = [k for k, v in self.rag_dependencies.items() if not v]
            return f"RAG System (Partial - Missing: {', '.join(missing)})"
        elif self.use_realtime_data:
            return "Real-time API Data"
        else:
            return "Enhanced Historical Simulated Data"
    
    async def _get_rag_enhanced_insights(self, industry: str, platform: str, visual_format: str, post_type: str, prompt: str) -> Dict[str, Any]:
        """Obtiene insights mejorados usando el sistema RAG"""
        try:
            # Usar el sistema RAG para obtener recomendación completa
            rag_recommendation = self.rag_system.generate_enhanced_recommendation(
                prompt=prompt,
                platform=platform,
                industry=industry,
                goal=post_type.lower()
            )
            
            if rag_recommendation.get('error'):
                self.logger.warning("RAG system returned error, falling back to traditional method")
                return self._generate_performance_insights(post_type, platform, visual_format)
            
            # Convertir recomendación RAG al formato esperado
            historical_justification = rag_recommendation.get('historical_justification', {})
            contextual_justification = rag_recommendation.get('contextual_justification', {})
            expected_performance = rag_recommendation.get('expected_performance', {})
            
            # Calcular format_boost basado en el formato visual
            format_boost = 1.0
            if visual_format == "Video":
                format_boost = 1.8
            elif visual_format == "Carousel":
                format_boost = 1.4
            
            return {
                "historical_performance": {
                    "source": historical_justification.get('source', 'RAG System'),
                    "context": historical_justification.get('context', ''),
                    "audience": historical_justification.get('audience', 'General')
                },
                "projected_metrics": {
                    "expected_ctr": expected_performance.get('estimated_ctr', 0.045) / 100 if expected_performance.get('estimated_ctr', 0) > 1 else expected_performance.get('estimated_ctr', 0.045),
                    "expected_engagement_rate": expected_performance.get('estimated_engagement', 0.045) / 100 if expected_performance.get('estimated_engagement', 0) > 1 else expected_performance.get('estimated_engagement', 0.045),
                    "estimated_reach": int(expected_performance.get('estimated_engagement', 4.5) * 1000)
                },
                "trending_hashtags": contextual_justification.get('suggested_hashtags', [])[:5],
                "seasonal_context": contextual_justification.get('seasonal_context', ''),
                "competitive_insights": rag_recommendation.get('competitive_advantage', {}),
                "confidence_score": 0.90 if expected_performance.get('confidence') == 'High' else 0.75,
                "data_source": "rag_enhanced",
                "rag_enabled": True,
                "data_freshness": rag_recommendation.get('data_freshness', ''),
                "format_boost": format_boost
            }
            
        except Exception as e:
            self.logger.error(f"Error en sistema RAG: {e}")
            # Fallback a método tradicional
            return self._generate_performance_insights(post_type, platform, visual_format)
    
    def _generate_performance_insights(self, post_type: str, platform: str, visual_format: str) -> Dict[str, Any]:
        """Genera insights de performance basados en datos históricos simulados"""
        # Base de datos simulada con métricas históricas más detalladas
        historical_data = {
            "promotional": {
                "Image": {"ctr": 0.029, "engagement": 0.035, "reach": 1200, "conversions": 0.024},
                "Video": {"ctr": 0.045, "engagement": 0.063, "reach": 2100, "conversions": 0.038},
                "Carousel": {"ctr": 0.037, "engagement": 0.042, "reach": 1650, "conversions": 0.031}
            },
            "educational": {
                "Image": {"ctr": 0.032, "engagement": 0.042, "reach": 1400, "conversions": 0.019},
                "Video": {"ctr": 0.051, "engagement": 0.076, "reach": 2400, "conversions": 0.029},
                "Carousel": {"ctr": 0.041, "engagement": 0.051, "reach": 1800, "conversions": 0.023}
            },
            "entertainment": {
                "Image": {"ctr": 0.038, "engagement": 0.048, "reach": 1600, "conversions": 0.015},
                "Video": {"ctr": 0.067, "engagement": 0.086, "reach": 3200, "conversions": 0.022},
                "Carousel": {"ctr": 0.044, "engagement": 0.058, "reach": 2000, "conversions": 0.018}
            }
        }
        
        platform_performance = {
            "Instagram": {"reach_multiplier": 1.0, "engagement_boost": 1.0, "peak_hours": "7-9 PM"},
            "TikTok": {"reach_multiplier": 1.4, "engagement_boost": 1.3, "peak_hours": "6-10 PM"},
            "Facebook": {"reach_multiplier": 0.8, "engagement_boost": 0.8, "peak_hours": "1-3 PM"},
            "LinkedIn": {"reach_multiplier": 0.6, "engagement_boost": 0.6, "peak_hours": "8-10 AM"},
            "Twitter": {"reach_multiplier": 0.9, "engagement_boost": 0.9, "peak_hours": "9 AM-12 PM"}
        }
        
        # Obtener datos históricos
        post_data = historical_data.get(post_type.lower(), historical_data["promotional"])
        format_data = post_data.get(visual_format, post_data["Image"])
        platform_data = platform_performance.get(platform, platform_performance["Instagram"])
        
        # Calcular métricas proyectadas
        projected_ctr = format_data["ctr"] * platform_data["engagement_boost"]
        projected_engagement = format_data["engagement"] * platform_data["engagement_boost"]
        projected_reach = int(format_data["reach"] * platform_data["reach_multiplier"])
        
        # Calcular comparaciones con otros formatos
        format_comparison = {}
        for fmt, data in post_data.items():
            if fmt != visual_format:
                comparison_engagement = data["engagement"] * platform_data["engagement_boost"]
                improvement = ((projected_engagement - comparison_engagement) / comparison_engagement) * 100
                format_comparison[fmt] = {
                    "engagement_diff": round(improvement, 1),
                    "historical_ctr": data["ctr"]
                }
        
        # Calcular format_boost basado en el formato visual
        format_boost = 1.0
        if visual_format == "Video":
            format_boost = 1.8
        elif visual_format == "Carousel":
            format_boost = 1.4
        
        return {
            "historical_performance": {
                "ctr": format_data["ctr"],
                "engagement": format_data["engagement"],
                "average_reach": format_data["reach"]
            },
            "projected_metrics": {
                "expected_ctr": round(projected_ctr, 3),
                "expected_engagement_rate": round(projected_engagement, 3),
                "estimated_reach": projected_reach
            },
            "format_comparison": format_comparison,
            "platform_insights": {
                "optimal_posting_time": platform_data["peak_hours"],
                "platform_boost": platform_data["engagement_boost"],
                "reach_potential": platform_data["reach_multiplier"]
            },
            "confidence_score": min(0.75 + (platform_data["engagement_boost"] - 1.0) * 0.2, 0.95),
            "conversion_potential": round(projected_engagement * 0.7, 3),
            "format_boost": format_boost
        }
    
    def _create_optimization_recommendations(self, state: Dict[str, Any], insights: Dict[str, Any]) -> list:
        """Crea recomendaciones de optimización"""
        recommendations = []
        
        # Optimización de timing
        platform = getattr(state["prompt_analysis"], 'platform', 'general')
        if platform in self.performance_db["platforms"]:
            peak_hours = self.performance_db["platforms"][platform].get("peak_hours")
            recommendations.append(f"Publicar durante horas pico: {peak_hours}")
        
        # Optimización de formato
        language = state.get("language_config", {}).get("language", "es")
        if insights["format_boost"] < 1.5:
            if language == "en":
                recommendations.append("Consider video format for higher engagement")
            else:
                recommendations.append("Considerar formato de video para mayor engagement")
        
        # Optimización de contenido
        if insights["expected_engagement_rate"] < 0.04:
            if language == "en":
                recommendations.append("Add more interactive or engaging elements")
            else:
                recommendations.append("Agregar elementos más interactivos o controversiales")
        
        # Optimización de CTA
        if insights["conversion_potential"] < 0.03:
            if language == "en":
                recommendations.append("Strengthen call-to-action with urgency or incentives")
            else:
                recommendations.append("Fortalecer call-to-action con urgencia o incentivos")
        
        return recommendations
    
    def _summarize_current_strategy(self, state: Dict[str, Any]) -> str:
        """Resume la estrategia actual"""
        post_type = state["post_type"].value
        platform = getattr(state["prompt_analysis"], 'platform', 'general')
        visual_format = state.get("visual_format_recommendation", {}).get("recommended_format", "Image")
        
        return f"Tipo: {post_type}, Plataforma: {platform}, Formato: {visual_format}"
    
    def _parse_optimizations(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea las optimizaciones del LLM"""
        return {
            "content_optimizations": response.get("content_optimizations", []),
            "timing_recommendations": response.get("timing_recommendations", []),
            "format_adjustments": response.get("format_adjustments", []),
            "engagement_tactics": response.get("engagement_tactics", []),
            "risk_mitigation": response.get("risk_mitigation", [])
        }
    
    def _predict_performance(self, state: Dict[str, Any], optimizations: Dict[str, Any]) -> Dict[str, Any]:
        """Predice performance con optimizaciones aplicadas"""
        base_engagement = 0.04
        
        # Aplicar boosts por optimizaciones
        optimization_boost = len(optimizations.get("content_optimizations", [])) * 0.005
        format_boost = 1.0
        
        visual_format = state.get("visual_format_recommendation", {}).get("recommended_format", "Image")
        if visual_format == "Video":
            format_boost = 1.8
        elif visual_format == "Carousel":
            format_boost = 1.4
        
        predicted_engagement = base_engagement * format_boost + optimization_boost
        
        return {
            "predicted_engagement_rate": min(predicted_engagement, 0.15),  # Cap realista
            "confidence_interval": [predicted_engagement * 0.8, predicted_engagement * 1.2],
            "key_success_factors": optimizations.get("engagement_tactics", [])
        }
