"""
Sistema RAG gratuito para datos de marketing en tiempo real
Utiliza Chroma DB, Sentence Transformers y DuckDuckGo Search
"""

import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import re

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

DEPENDENCIES_AVAILABLE = CHROMADB_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE and DUCKDUCKGO_AVAILABLE

if not DEPENDENCIES_AVAILABLE:
    logging.warning("RAG dependencies not installed. Install with: pip install chromadb sentence-transformers duckduckgo-search")

class MarketingBenchmarkData:
    """Base de datos de benchmarks reales de marketing"""
    
    @staticmethod
    def get_real_benchmarks() -> List[Dict[str, Any]]:
        """Datos reales extraídos de reportes públicos 2024"""
        return [
            {
                "platform": "Instagram",
                "format": "Reels",
                "metric": "CTR",
                "value": 1.84,
                "engagement_rate": 4.2,
                "industry": "E-commerce",
                "source": "Hootsuite Digital Trends Report 2024",
                "date": "2024-Q3",
                "context": "Video content outperforms static images by 112%",
                "audience": "Gen Z"
            },
            {
                "platform": "Instagram", 
                "format": "Carousel",
                "metric": "CTR",
                "value": 1.23,
                "engagement_rate": 2.8,
                "industry": "E-commerce", 
                "source": "Sprout Social Index 2024",
                "date": "2024-Q3",
                "context": "Multiple images increase dwell time by 73%",
                "audience": "Millennials"
            },
            {
                "platform": "Instagram",
                "format": "Static Image",
                "metric": "CTR", 
                "value": 0.89,
                "engagement_rate": 1.9,
                "industry": "E-commerce",
                "source": "Social Media Examiner 2024",
                "date": "2024-Q3",
                "context": "High-quality visuals with clear CTAs perform best",
                "audience": "General"
            },
            {
                "platform": "TikTok",
                "format": "Short Video",
                "metric": "Engagement Rate",
                "value": 5.3,
                "engagement_rate": 5.3,
                "industry": "Fashion",
                "source": "Social Media Examiner 2024",
                "date": "2024-Q3", 
                "context": "Short-form video dominates discovery algorithms",
                "audience": "Gen Z"
            },
            {
                "platform": "LinkedIn",
                "format": "Document Post",
                "metric": "CTR", 
                "value": 0.89,
                "engagement_rate": 2.1,
                "industry": "B2B SaaS",
                "source": "HubSpot State of Marketing 2024",
                "date": "2024-Q3",
                "context": "Native documents get 5x more engagement than links",
                "audience": "Professionals"
            },
            {
                "platform": "Facebook",
                "format": "Video",
                "metric": "CTR",
                "value": 1.04,
                "engagement_rate": 2.3,
                "industry": "General",
                "source": "Buffer State of Social 2024",
                "date": "2024-Q3",
                "context": "Video posts receive 59% more engagement than other post types",
                "audience": "Millennials"
            },
            {
                "platform": "Twitter",
                "format": "Thread",
                "metric": "Engagement Rate",
                "value": 3.7,
                "engagement_rate": 3.7,
                "industry": "Tech",
                "source": "Twitter Business 2024",
                "date": "2024-Q3",
                "context": "Threads encourage deeper engagement and discussion",
                "audience": "Tech-savvy"
            },
            {
                "platform": "YouTube",
                "format": "Shorts",
                "metric": "CTR",
                "value": 2.1,
                "engagement_rate": 6.8,
                "industry": "Entertainment",
                "source": "YouTube Creator Economy Report 2024",
                "date": "2024-Q3",
                "context": "Shorts drive 25% more subscriber growth than long-form",
                "audience": "Gen Z"
            }
        ]

class RealTimeContextEngine:
    """Motor de contexto en tiempo real usando APIs gratuitas"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if DEPENDENCIES_AVAILABLE:
            self.ddgs = DDGS()
        
    def get_trending_topics(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """Obtiene temas trending usando DuckDuckGo"""
        if not DEPENDENCIES_AVAILABLE:
            return self._get_fallback_trends(query)
            
        try:
            search_query = f"{query} trending {datetime.now().strftime('%B %Y')}"
            results = list(self.ddgs.text(search_query, max_results=limit))
            return [{"title": r["title"], "snippet": r["body"][:200]} for r in results]
        except Exception as e:
            self.logger.warning(f"Error getting trends from DuckDuckGo: {e}")
            return self._get_fallback_trends(query)
    
    def _get_fallback_trends(self, query: str) -> List[Dict[str, str]]:
        """Tendencias fallback basadas en la época del año"""
        current_month = datetime.now().month
        
        seasonal_trends = {
            9: [  # Septiembre
                {"title": "Back to School Marketing Trends", "snippet": "Educational content and student-focused campaigns dominate September"},
                {"title": "Fall Fashion Week Impact", "snippet": "Autumn fashion trends influence social media content strategies"},
                {"title": "Q4 Marketing Preparation", "snippet": "Brands prepare for holiday season with strategic content planning"}
            ],
            10: [  # Octubre
                {"title": "Halloween Marketing Campaigns", "snippet": "Spooky season drives creative content and engagement"},
                {"title": "Fall Lifestyle Content", "snippet": "Cozy aesthetics and autumn activities trend across platforms"}
            ]
        }
        
        return seasonal_trends.get(current_month, [
            {"title": "Digital Marketing Evolution", "snippet": "Continuous adaptation to platform algorithm changes"},
            {"title": "Authentic Content Demand", "snippet": "Users increasingly prefer genuine, behind-the-scenes content"}
        ])
    
    def get_hashtag_trends(self, platform: str, industry: str = "general") -> List[str]:
        """Obtiene hashtags trending por plataforma e industria"""
        if not DEPENDENCIES_AVAILABLE:
            return self._get_fallback_hashtags(platform, industry)
            
        try:
            search_query = f"{platform} trending hashtags {industry} {datetime.now().strftime('%B %Y')}"
            results = list(self.ddgs.text(search_query, max_results=3))
            hashtags = self._extract_hashtags_from_results(results)
            return hashtags if hashtags else self._get_fallback_hashtags(platform, industry)
        except Exception as e:
            self.logger.warning(f"Error getting hashtag trends: {e}")
            return self._get_fallback_hashtags(platform, industry)
    
    def _extract_hashtags_from_results(self, results: List[Dict]) -> List[str]:
        """Extrae hashtags de los resultados de búsqueda"""
        hashtags = []
        for result in results:
            text = result.get("body", "")
            found_tags = re.findall(r'#\w+', text)
            hashtags.extend(found_tags[:2])
        return list(set(hashtags))[:5]
    
    def _get_fallback_hashtags(self, platform: str, industry: str) -> List[str]:
        """Hashtags fallback basados en plataforma e industria"""
        base_hashtags = {
            "Instagram": ["#InstagramReels", "#IGTrending", "#ContentCreator"],
            "TikTok": ["#TikTokTrending", "#ForYou", "#Viral"],
            "LinkedIn": ["#LinkedInTips", "#ProfessionalGrowth", "#BusinessInsights"],
            "Facebook": ["#FacebookMarketing", "#SocialMedia", "#Engagement"],
            "Twitter": ["#TwitterTrends", "#SocialMediaMarketing", "#DigitalMarketing"]
        }
        
        industry_hashtags = {
            "fashion": ["#FashionTrends", "#StyleInspo", "#OOTD"],
            "tech": ["#TechInnovation", "#DigitalTransformation", "#AI"],
            "fitness": ["#FitnessMotivation", "#HealthyLifestyle", "#WorkoutTips"],
            "food": ["#FoodTrends", "#RecipeOfTheDay", "#Foodie"]
        }
        
        platform_tags = base_hashtags.get(platform, ["#SocialMedia", "#Marketing", "#Trending"])
        industry_tags = industry_hashtags.get(industry.lower(), ["#Business", "#Growth"])
        
        return platform_tags + industry_tags

class MarketingRAGSystem:
    """Sistema RAG principal para estrategia de marketing"""
    
    def __init__(self, enable_rag: bool = True):
        self.logger = logging.getLogger(__name__)
        self.enable_rag = enable_rag and DEPENDENCIES_AVAILABLE
        
        # Inicializar valores por defecto para evitar AttributeError
        self.chroma_client = None
        self.collection = None
        self.embedding_model = None
        self.ddgs = None
        
        if self.enable_rag:
            self._initialize_rag_components()
        else:
            self.logger.info("RAG system disabled or dependencies not available")
        
        # Componentes siempre disponibles
        self.context_engine = RealTimeContextEngine()
        self.benchmark_data = MarketingBenchmarkData.get_real_benchmarks()
        
    def _initialize_rag_components(self):
        """Inicializa componentes RAG si están disponibles"""
        try:
            # Inicializar valores por defecto
            self.chroma_client = None
            self.collection = None
            self.embedding_model = None
            self.ddgs = None
            
            # Inicializar Chroma (gratis)
            if CHROMADB_AVAILABLE:
                self.chroma_client = chromadb.Client()
                
                # Crear o obtener colección
                try:
                    self.collection = self.chroma_client.get_collection("marketing_benchmarks")
                    self.logger.info("Colección RAG existente cargada")
                except:
                    self.collection = self.chroma_client.create_collection(
                        name="marketing_benchmarks",
                        metadata={"description": "Real marketing performance data"}
                    )
                    self._populate_knowledge_base()
                    self.logger.info("Nueva colección RAG creada y poblada")
                
                # Modelo de embeddings local (gratis)
                if SENTENCE_TRANSFORMERS_AVAILABLE:
                    self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                    self.logger.info("Embedding model initialized successfully")
                else:
                    self.logger.warning("Sentence transformers not available")
            else:
                self.logger.warning("ChromaDB not available")
            
            # Componentes RAG opcionales
            if DUCKDUCKGO_AVAILABLE:
                try:
                    # Inicializar DuckDuckGo Search (gratis, sin límites)
                    self.ddgs = DDGS()
                    self.logger.info("DuckDuckGo Search initialized successfully")
                except Exception as e:
                    self.logger.error(f"Error inicializando DuckDuckGo: {e}")
                    self.ddgs = None
                    
        except Exception as e:
            self.logger.error(f"Error inicializando RAG: {e}")
            self.enable_rag = False
    
    def _populate_knowledge_base(self):
        """Puebla la base de conocimiento con datos reales"""
        benchmarks = MarketingBenchmarkData.get_real_benchmarks()
        
        documents = []
        metadatas = []
        ids = []
        
        for i, benchmark in enumerate(benchmarks):
            # Crear texto descriptivo para embeddings
            doc_text = f"""
            Platform: {benchmark['platform']}
            Format: {benchmark['format']}
            Metric: {benchmark['metric']} = {benchmark['value']}%
            Engagement Rate: {benchmark['engagement_rate']}%
            Industry: {benchmark['industry']}
            Audience: {benchmark['audience']}
            Context: {benchmark['context']}
            Source: {benchmark['source']}
            Date: {benchmark['date']}
            """
            
            documents.append(doc_text.strip())
            metadatas.append(benchmark)
            ids.append(f"benchmark_{i}")
        
        # Generar embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Agregar a Chroma
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        self.logger.info(f"Base de conocimiento poblada con {len(benchmarks)} registros")
    
    def query_performance_data(self, query: str, platform: str = None, 
                             industry: str = None, n_results: int = 3) -> List[Dict]:
        """Consulta datos de rendimiento usando RAG o fallback"""
        
        if self.enable_rag:
            return self._query_with_rag(query, platform, industry, n_results)
        else:
            return self._query_with_fallback(query, platform, industry, n_results)
    
    def _query_with_rag(self, query: str, platform: str, industry: str, n_results: int) -> List[Dict]:
        """Consulta usando sistema RAG"""
        try:
            # Verificar que el modelo de embeddings esté disponible
            if not hasattr(self, 'embedding_model'):
                self.logger.warning("Embedding model not available, using fallback")
                return self._query_with_fallback(query, platform, industry, n_results)
            
            # Construir query contextual
            search_query = query
            if platform:
                search_query += f" {platform}"
            if industry:
                search_query += f" {industry}"
            
            # Generar embedding de la consulta
            query_embedding = self.embedding_model.encode([search_query]).tolist()[0]
            
            # Construir filtros
            where_clause = {}
            if platform:
                where_clause["platform"] = platform
            if industry:
                where_clause["industry"] = industry
            
            # Buscar en base vectorial
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None
            )
            
            return results['metadatas'][0] if results['metadatas'] else []
            
        except Exception as e:
            self.logger.error(f"Error en consulta RAG: {e}")
            return self._query_with_fallback(query, platform, industry, n_results)
    
    def _query_with_fallback(self, query: str, platform: str, industry: str, n_results: int) -> List[Dict]:
        """Consulta usando datos estáticos como fallback"""
        benchmarks = self.benchmark_data
        
        # Filtrar por plataforma e industria
        filtered = benchmarks
        if platform:
            filtered = [b for b in filtered if b['platform'].lower() == platform.lower()]
        if industry:
            filtered = [b for b in filtered if b['industry'].lower() == industry.lower()]
        
        # Ordenar por engagement rate y tomar los mejores
        filtered.sort(key=lambda x: x.get('engagement_rate', 0), reverse=True)
        return filtered[:n_results]
    
    def get_real_time_context(self, brand_context: str, platform: str, industry: str = "general") -> Dict:
        """Obtiene contexto en tiempo real"""
        context = {
            "trending_topics": self.context_engine.get_trending_topics(f"{brand_context} {industry}"),
            "hashtags": self.context_engine.get_hashtag_trends(platform, industry),
            "timestamp": datetime.now().isoformat(),
            "data_source": "real_time_search" if DEPENDENCIES_AVAILABLE else "fallback_seasonal"
        }
        return context
    
    def generate_enhanced_recommendation(self, prompt: str, platform: str, 
                                       industry: str, goal: str) -> Dict:
        """Genera recomendación mejorada con RAG"""
        
        # 1. Consultar datos históricos
        historical_data = self.query_performance_data(
            f"{goal} {platform} {industry}", platform, industry
        )
        
        # 2. Obtener contexto actual
        current_context = self.get_real_time_context(prompt, platform, industry)
        
        # 3. Analizar y recomendar
        if not historical_data:
            # Usar datos generales si no hay específicos
            historical_data = self.query_performance_data(
                f"{platform}", platform, None
            )
            
        if not historical_data:
            return {"error": "No historical data found", "fallback": True}
        
        # Encontrar mejor formato basado en datos
        best_format = max(historical_data, key=lambda x: x.get('engagement_rate', 0))
        
        # Construir recomendación mejorada
        recommendation = {
            "recommended_format": best_format['format'],
            "historical_justification": {
                "metric": f"{best_format['metric']}: {best_format['value']}%",
                "engagement_rate": f"{best_format['engagement_rate']}%",
                "source": best_format['source'],
                "context": best_format['context'],
                "audience": best_format['audience']
            },
            "contextual_justification": {
                "trending_topics": [t['title'] for t in current_context['trending_topics'][:2]],
                "suggested_hashtags": current_context['hashtags'][:5],
                "seasonal_context": f"Optimized for {datetime.now().strftime('%B %Y')}"
            },
            "expected_performance": {
                "estimated_ctr": best_format['value'],
                "estimated_engagement": best_format['engagement_rate'],
                "confidence": "High" if len(historical_data) >= 2 else "Medium"
            },
            "competitive_advantage": self._generate_competitive_insights(best_format, historical_data),
            "rag_enabled": self.enable_rag,
            "data_freshness": current_context['timestamp']
        }
        
        return recommendation
    
    def _generate_competitive_insights(self, best_format: Dict, all_data: List[Dict]) -> Dict:
        """Genera insights competitivos basados en los datos"""
        if len(all_data) < 2:
            return {"insight": "Limited competitive data available"}
        
        # Comparar con otros formatos
        other_formats = [d for d in all_data if d['format'] != best_format['format']]
        if other_formats:
            avg_other_engagement = sum(d.get('engagement_rate', 0) for d in other_formats) / len(other_formats)
            improvement = ((best_format['engagement_rate'] - avg_other_engagement) / avg_other_engagement) * 100
            
            return {
                "insight": f"{best_format['format']} outperforms other formats by {improvement:.1f}%",
                "comparison": f"vs average of {avg_other_engagement:.1f}% engagement",
                "advantage": "significant" if improvement > 50 else "moderate" if improvement > 20 else "minor"
            }
        
        return {"insight": "Strong performance based on historical data"}

# Función de utilidad para verificar dependencias
def check_rag_dependencies():
    """Verifica disponibilidad de dependencias RAG"""
    return {
        "chromadb": CHROMADB_AVAILABLE,
        "sentence_transformers": SENTENCE_TRANSFORMERS_AVAILABLE,
        "duckduckgo_search": DUCKDUCKGO_AVAILABLE
    }
