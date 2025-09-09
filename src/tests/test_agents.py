"""
Tests para los agentes del sistema de marketing
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

# Importar agentes
from src.agents.prompt_analyzer import PromptAnalyzer
from src.agents.post_classifier import PostClassifier
from src.agents.brand_voice_agent import BrandVoiceAgent
from src.agents.fact_grounding import FactGroundingAgent
from src.agents.text_generator import TextGenerator
from src.agents.caption_creator import CaptionCreator
from src.agents.visual_concept import VisualConceptAgent
from src.agents.reasoning_module import ReasoningModuleAgent

# Importar modelos
from src.models.content_brief import (
    PromptAnalysis, PostType, BrandVoice, FactualGrounding,
    EngagementElements, VisualConcept, ReasoningModule
)

@pytest.fixture
def mock_llm_client():
    """Cliente LLM mock para testing"""
    client = Mock()
    client.generate = AsyncMock()
    client.generate_structured = AsyncMock()
    return client

@pytest.fixture
def sample_prompt():
    """Prompt de ejemplo para testing"""
    return "Crear un post promocional para un nuevo producto de tecnología que se dirige a profesionales jóvenes"

@pytest.fixture
def sample_analysis():
    """Análisis de ejemplo para testing"""
    return PromptAnalysis(
        objective="Ventas",
        audience="Profesionales jóvenes",
        brand_cues=["Innovación", "Tecnología"],
        key_facts=["Nuevo producto", "Tecnología"],
        urgency=None,
        platform=None,
        tone_indicators=["Profesional", "Moderno"],
        content_goals=["Generar leads", "Aumentar awareness"]
    )

class TestPromptAnalyzer:
    """Tests para el Prompt Analyzer"""
    
    def test_initialization(self, mock_llm_client):
        """Test de inicialización del agente"""
        agent = PromptAnalyzer(mock_llm_client)
        assert agent.llm == mock_llm_client
        assert agent.logger is not None
    
    @pytest.mark.asyncio
    async def test_process_success(self, mock_llm_client, sample_prompt):
        """Test de procesamiento exitoso"""
        # Mock de respuesta del LLM
        mock_response = {
            "objective": "Ventas",
            "audience": "Profesionales jóvenes",
            "brand_cues": ["Innovación"],
            "key_facts": ["Nuevo producto"],
            "urgency": None,
            "platform": None,
            "tone_indicators": ["Profesional"],
            "content_goals": ["Generar leads"]
        }
        mock_llm_client.generate_structured.return_value = mock_response
        
        # Crear estado inicial
        state = {
            "input_prompt": sample_prompt,
            "errors": [],
            "warnings": [],
            "agent_timings": {},
            "completed_steps": [],
            "current_step": ""
        }
        
        # Procesar
        agent = PromptAnalyzer(mock_llm_client)
        result = await agent.process(state)
        
        # Verificar resultados
        assert result["prompt_analysis"] is not None
        assert result["current_step"] == "post_classification"
        assert "prompt_analysis" in result["completed_steps"]
        assert result["agent_timings"]["prompt_analyzer"] > 0

class TestPostClassifier:
    """Tests para el Post Classifier"""
    
    def test_initialization(self, mock_llm_client):
        """Test de inicialización del agente"""
        agent = PostClassifier(mock_llm_client)
        assert agent.llm == mock_llm_client
    
    @pytest.mark.asyncio
    async def test_process_success(self, mock_llm_client, sample_analysis):
        """Test de procesamiento exitoso"""
        # Mock de respuesta del LLM
        mock_response = {
            "post_type": "Promotional",
            "justification": "Seleccionado para maximizar conversiones"
        }
        mock_llm_client.generate_structured.return_value = mock_response
        
        # Crear estado con análisis previo
        state = {
            "prompt_analysis": sample_analysis,
            "errors": [],
            "warnings": [],
            "agent_timings": {},
            "completed_steps": [],
            "current_step": ""
        }
        
        # Procesar
        agent = PostClassifier(mock_llm_client)
        result = await agent.process(state)
        
        # Verificar resultados
        assert result["post_type"] == PostType.PROMOTIONAL
        assert result["post_justification"] == "Seleccionado para maximizar conversiones"
        assert result["current_step"] == "brand_voice"
        assert "post_classification" in result["completed_steps"]

class TestBrandVoiceAgent:
    """Tests para el Brand Voice Agent"""
    
    def test_initialization(self, mock_llm_client):
        """Test de inicialización del agente"""
        agent = BrandVoiceAgent(mock_llm_client)
        assert agent.llm == mock_llm_client
    
    @pytest.mark.asyncio
    async def test_process_success(self, mock_llm_client, sample_analysis):
        """Test de procesamiento exitoso"""
        # Mock de respuesta del LLM
        mock_response = {
            "tone": "Profesional",
            "personality": "Innovador",
            "style": "Moderno",
            "values": ["Innovación", "Calidad"],
            "language_level": "Semi-formal"
        }
        mock_llm_client.generate_structured.return_value = mock_response
        
        # Crear estado con análisis previo y tipo de post
        state = {
            "prompt_analysis": sample_analysis,
            "post_type": PostType.PROMOTIONAL,
            "errors": [],
            "warnings": [],
            "agent_timings": {},
            "completed_steps": [],
            "current_step": ""
        }
        
        # Procesar
        agent = BrandVoiceAgent(mock_llm_client)
        result = await agent.process(state)
        
        # Verificar resultados
        assert result["brand_voice"] is not None
        assert result["brand_voice"].tone == "Profesional"
        assert result["current_step"] == "fact_grounding"
        assert "brand_voice" in result["completed_steps"]

class TestTextGenerator:
    """Tests para el Text Generator"""
    
    def test_initialization(self, mock_llm_client):
        """Test de inicialización del agente"""
        agent = TextGenerator(mock_llm_client)
        assert agent.llm == mock_llm_client
    
    def test_clean_and_validate_content(self, mock_llm_client):
        """Test de limpieza y validación de contenido"""
        agent = TextGenerator(mock_llm_client)
        
        # Test con contenido sucio
        dirty_content = "```**Contenido sucio**```\n\n\n\nCon formato extra"
        cleaned = agent._clean_and_validate_content(dirty_content)
        
        assert "```" not in cleaned
        assert "**" not in cleaned
        assert cleaned.count("\n\n") <= 2  # Máximo 2 líneas vacías consecutivas

class TestCaptionCreator:
    """Tests para el Caption Creator"""
    
    def test_initialization(self, mock_llm_client):
        """Test de inicialización del agente"""
        agent = CaptionCreator(mock_llm_client)
        assert agent.llm == mock_llm_client
    
    def test_validate_and_enhance_engagement(self, mock_llm_client):
        """Test de validación y mejora de engagement"""
        agent = CaptionCreator(mock_llm_client)
        
        # Crear engagement incompleto
        engagement = EngagementElements(
            caption="",
            call_to_action="",
            hashtags=[],
            engagement_hooks=[],
            questions=[]
        )
        
        # Validar y mejorar
        enhanced = agent._validate_and_enhance_engagement(engagement)
        
        assert enhanced.caption != ""
        assert enhanced.call_to_action != ""
        assert len(enhanced.hashtags) > 0
        assert len(enhanced.engagement_hooks) > 0
        assert len(enhanced.questions) > 0

class TestVisualConceptAgent:
    """Tests para el Visual Concept Agent"""
    
    def test_initialization(self, mock_llm_client):
        """Test de inicialización del agente"""
        agent = VisualConceptAgent(mock_llm_client)
        assert agent.llm == mock_llm_client
    
    def test_validate_and_enhance_visual_concept(self, mock_llm_client):
        """Test de validación y mejora del concepto visual"""
        agent = VisualConceptAgent(mock_llm_client)
        
        # Crear concepto visual incompleto
        visual = VisualConcept(
            mood="",
            color_palette=[],
            imagery_type="",
            layout_style="",
            visual_elements=[],
            design_notes=""
        )
        
        # Validar y mejorar
        enhanced = agent._validate_and_enhance_visual_concept(visual)
        
        assert enhanced.mood != ""
        assert len(enhanced.color_palette) >= 3
        assert enhanced.imagery_type != ""
        assert enhanced.layout_style != ""
        assert len(enhanced.visual_elements) > 0
        assert enhanced.design_notes != ""

class TestReasoningModuleAgent:
    """Tests para el Reasoning Module Agent"""
    
    def test_initialization(self, mock_llm_client):
        """Test de inicialización del agente"""
        agent = ReasoningModuleAgent(mock_llm_client)
        assert agent.llm == mock_llm_client
    
    def test_create_full_analysis_summary(self, mock_llm_client):
        """Test de creación de resumen de análisis"""
        agent = ReasoningModuleAgent(mock_llm_client)
        
        # Crear estado de ejemplo
        state = {
            "prompt_analysis": sample_analysis(),
            "post_type": PostType.PROMOTIONAL,
            "brand_voice": BrandVoice(
                tone="Profesional",
                personality="Innovador",
                style="Moderno",
                values=["Innovación"],
                language_level="Semi-formal"
            )
        }
        
        # Crear resumen
        summary = agent._create_full_analysis_summary(state)
        
        assert "ANÁLISIS DEL PROMPT:" in summary
        assert "TIPO DE POST: Promotional" in summary
        assert "VOZ DE MARCA:" in summary
        assert "Objetivo: Ventas" in summary

# Tests de integración
class TestAgentIntegration:
    """Tests de integración entre agentes"""
    
    @pytest.mark.asyncio
    async def test_agent_chain(self, mock_llm_client):
        """Test de cadena de agentes"""
        # Crear todos los agentes
        prompt_analyzer = PromptAnalyzer(mock_llm_client)
        post_classifier = PostClassifier(mock_llm_client)
        brand_voice_agent = BrandVoiceAgent(mock_llm_client)
        
        # Estado inicial
        state = {
            "input_prompt": "Crear un post promocional para tecnología",
            "errors": [],
            "warnings": [],
            "agent_timings": {},
            "completed_steps": [],
            "current_step": ""
        }
        
        # Mock de respuestas
        mock_llm_client.generate_structured.side_effect = [
            # Prompt Analyzer
            {
                "objective": "Ventas",
                "audience": "Profesionales",
                "brand_cues": ["Tecnología"],
                "key_facts": ["Nuevo producto"],
                "urgency": None,
                "platform": None,
                "tone_indicators": ["Profesional"],
                "content_goals": ["Generar leads"]
            },
            # Post Classifier
            {
                "post_type": "Promotional",
                "justification": "Para maximizar conversiones"
            },
            # Brand Voice Agent
            {
                "tone": "Profesional",
                "personality": "Innovador",
                "style": "Moderno",
                "values": ["Innovación"],
                "language_level": "Semi-formal"
            }
        ]
        
        # Ejecutar cadena
        state = await prompt_analyzer.process(state)
        state = await post_classifier.process(state)
        state = await brand_voice_agent.process(state)
        
        # Verificar estado final
        assert state["prompt_analysis"] is not None
        assert state["post_type"] == PostType.PROMOTIONAL
        assert state["brand_voice"] is not None
        assert len(state["completed_steps"]) == 3

