"""
Minimal content_brief module for the lightweight agents.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class PostType(str, Enum):
    """Types of social media posts"""
    LAUNCH = "Launch"
    EDUCATIONAL = "Educational"
    PROMOTIONAL = "Promotional"
    STORYTELLING = "Storytelling"
    ENGAGEMENT = "Engagement"

class PromptAnalysis(BaseModel):
    """Analysis of the user's prompt"""
    objective: str = Field(description="The main objective of the content")
    audience: str = Field(description="Target audience for the content")
    brand_cues: List[str] = Field(description="Brand elements to include")
    key_facts: List[str] = Field(description="Key facts or points to cover")
    urgency: Optional[str] = Field(description="Level of urgency")
    platform: Optional[str] = Field(description="Target platform")
    tone_indicators: List[str] = Field(description="Tone indicators")
    content_goals: List[str] = Field(description="Goals for the content")

class BrandVoice(BaseModel):
    """Brand voice and style guidelines"""
    tone: str = Field(description="General tone of voice")
    personality: str = Field(description="Brand personality traits")
    style: str = Field(description="Writing style")
    values: List[str] = Field(description="Core brand values")
    language_level: str = Field(description="Language formality level")

class FactualGrounding(BaseModel):
    """Factual information and sources"""
    key_facts: List[str] = Field(description="Key facts to include")
    data_sources: List[str] = Field(description="Sources of information")
    verification_status: str = Field(description="Status of fact verification")

class EngagementElements(BaseModel):
    """Elements to increase engagement"""
    caption: str = Field(description="Main caption text")
    call_to_action: str = Field(description="Call to action text")
    hashtags: List[str] = Field(description="Relevant hashtags")
    engagement_hooks: List[str] = Field(description="Hooks to capture attention", default_factory=list)
    questions: List[str] = Field(description="Questions to engage audience")

class VisualConcept(BaseModel):
    """Visual style guidelines"""
    mood: str = Field(description="Visual mood or theme")
    color_palette: List[str] = Field(description="Color scheme")
    imagery_type: str = Field(description="Type of imagery to use")
    layout_style: str = Field(description="Layout and composition style", default="modern")
    visual_elements: List[str] = Field(description="Key visual elements", default_factory=list)
    design_notes: str = Field(description="Additional design guidance", default="")

class ReasoningModule(BaseModel):
    """Reasoning behind content decisions"""
    strategic_decisions: List[str] = Field(description="Key strategic decisions")
    audience_considerations: str = Field(description="Audience considerations")
    platform_optimization: str = Field(description="Platform-specific optimizations")
    competitive_analysis: str = Field(description="Competitive analysis and positioning", default="")
    risk_assessment: str = Field(description="Risk assessment and mitigation strategies", default="")

class ProcessingMetadata(BaseModel):
    """Metadata about content processing"""
    processing_time: float = Field(description="Time taken to process")
    model_used: str = Field(description="AI model used")
    timestamp: str = Field(description="When processing occurred")

class ContentBrief(BaseModel):
    """Complete content brief combining all components"""
    post_type: PostType = Field(description="Type of social media post")
    core_content: str = Field(description="Main content/message")
    prompt_analysis: PromptAnalysis = Field(description="Analysis of the user's prompt")
    brand_voice: BrandVoice = Field(description="Brand voice and tone guidelines")
    engagement_elements: EngagementElements = Field(description="Elements to increase engagement")
    visual_concept: VisualConcept = Field(description="Visual style guidelines")
    factual_grounding: FactualGrounding = Field(description="Factual information and sources")
    reasoning: ReasoningModule = Field(description="Strategic reasoning behind content decisions")
    metadata: ProcessingMetadata = Field(description="Processing metadata")
    
    class Config:
        json_encoders = {
            'enum.Enum': lambda v: v.value
        }
