"""
Test script for essential agents (PromptAnalyzer and TextGenerator) with cloud models.
This is a lightweight version that only uses the essential agents.
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('essential_agents_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Add project root to path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Now import from the package
from tools.llm_client import create_llm_client
from agents.prompt_analyzer import PromptAnalyzer
from agents.text_generator import TextGenerator

# Rate limiting configuration
RATE_LIMIT_DELAY = 5  # Increased delay between API calls to avoid rate limits
MAX_RETRIES = 3  # Maximum number of retries for API calls

class WorkflowState:
    """Minimal workflow state for testing"""
    def __init__(self, input_prompt: str):
        self.input_prompt = input_prompt
        self.prompt_analysis = None
        self.core_content = None
        self.language_config = {"language": "es"}  # Default to Spanish
        self.errors = []
        self.warnings = []
        self.agent_timings = {}
        self.completed_steps = []
        self.current_step = ""
        self.is_error = False
        self.post_type = None  # Add post_type field
        self.brand_voice = None  # Add brand_voice field
        self.factual_grounding = None  # Add factual_grounding field

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for compatibility"""
        return {
            "input_prompt": self.input_prompt,
            "prompt_analysis": self.prompt_analysis,
            "core_content": self.core_content,
            "language_config": self.language_config,
            "errors": self.errors,
            "warnings": self.warnings,
            "agent_timings": self.agent_timings,
            "completed_steps": self.completed_steps,
            "current_step": self.current_step,
            "is_error": self.is_error
        }

async def test_essential_agents():
    """Test the essential agents with cloud models"""
    try:
        logger.info("=== Starting Essential Agents Test ===")
        
        # Initialize LLM client with cloud providers
        llm_client = create_llm_client()
        
        # Initialize agents
        prompt_analyzer = PromptAnalyzer(llm_client=llm_client)
        text_generator = TextGenerator(llm_client=llm_client)
        
        # Test prompt
        prompt = """
        Crea un post de LinkedIn anunciando el lanzamiento de 'Nexus Taskboard', 
        una nueva herramienta SaaS para gestores de equipos técnicos. 
        El tono debe ser profesional y entusiasta, destacando cómo mejora la productividad.
        """
        
        logger.info("Initializing workflow state...")
        state = WorkflowState(input_prompt=prompt)
        
        # Set required fields for the text generator
        from models.content_brief import PostType, BrandVoice, FactualGrounding
        
        # Set post_type
        state.post_type = PostType.LAUNCH
        
        # Set brand_voice
        state.brand_voice = BrandVoice(
            tone="profesional y entusiasta",
            personality="innovadora y confiable",
            style="directo y claro",
            values=["innovación", "eficiencia", "simplicidad"],
            language_level="profesional"
        )
        
        # Set factual_grounding
        state.factual_grounding = FactualGrounding(
            key_facts=[
                "Nexus Taskboard es una herramienta SaaS",
                "Diseñada para gestores de equipos técnicos",
                "Mejora la productividad del equipo"
            ],
            data_sources=["documentación del producto"],
            verification_status="verificado"
        )
        
        # Add required fields for the text generator
        from models.content_brief import PostType
        state.post_type = PostType.LAUNCH
        state.brand_voice = {
            "tone": "profesional y entusiasta",
            "personality": "innovadora y confiable",
            "style": "directo y claro",
            "values": ["innovación", "eficiencia", "simplicidad"],
            "language_level": "profesional"
        }
        state.factual_grounding = {
            "key_facts": [
                "Nexus Taskboard es una herramienta SaaS",
                "Diseñada para gestores de equipos técnicos",
                "Mejora la productividad del equipo"
            ],
            "data_sources": ["documentación del producto"],
            "verification_status": "verificado"
        }
        
        # Step 1: Analyze prompt with retry logic
        retry_count = 0
        result = None
        
        while retry_count < MAX_RETRIES:
            try:
                logger.info(f"Running Prompt Analyzer (Attempt {retry_count + 1}/{MAX_RETRIES})...")
                await asyncio.sleep(RATE_LIMIT_DELAY)  # Rate limiting
                
                # Convert state to dict for the prompt analyzer
                state_dict = state.to_dict()
                
                # Call the prompt analyzer
                result = await prompt_analyzer.process(state_dict)
                break  # If successful, exit the retry loop
                
            except Exception as e:
                retry_count += 1
                wait_time = RATE_LIMIT_DELAY * (2 ** retry_count)  # Exponential backoff
                logger.warning(f"Attempt {retry_count} failed: {str(e)}. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                
        if result is None:
            error_msg = f"Prompt Analyzer failed after {MAX_RETRIES} attempts"
            logger.error(error_msg)
            state.errors.append(error_msg)
            state.is_error = True
            return False
        
        # Update the state with the result
        if isinstance(result, dict):
            if "prompt_analysis" in result:
                state.prompt_analysis = result["prompt_analysis"]
            if "is_error" in result and result["is_error"]:
                logger.error(f"Prompt Analyzer failed: {result.get('errors', ['Unknown error'])}")
                return False
        
        logger.info("Prompt analysis completed successfully")
        
        # Step 2: Generate content with retry logic
        retry_count = 0
        result = None
        
        while retry_count < MAX_RETRIES:
            try:
                logger.info(f"Running Text Generator (Attempt {retry_count + 1}/{MAX_RETRIES})...")
                await asyncio.sleep(RATE_LIMIT_DELAY)  # Rate limiting
                
                # Prepare the state for the text generator
                state_dict = state.to_dict()
                
                # Ensure required fields are present with fallbacks
                if "post_type" not in state_dict or state_dict["post_type"] is None:
                    from models.content_brief import PostType
                    state_dict["post_type"] = PostType.LAUNCH  # Pass the enum, not the string value
                if "brand_voice" not in state_dict or state_dict["brand_voice"] is None:
                    state_dict["brand_voice"] = {
                        "tone": "profesional y entusiasta",
                        "personality": "innovadora y confiable",
                        "style": "directo y claro"
                    }
                if "factual_grounding" not in state_dict or state_dict["factual_grounding"] is None:
                    state_dict["factual_grounding"] = {
                        "key_facts": ["Nexus Taskboard es una herramienta SaaS"],
                        "verification_status": "verificado"
                    }
                
                # Call the text generator
                result = await text_generator.process(state_dict)
                break  # If successful, exit the retry loop
                
            except Exception as e:
                retry_count += 1
                wait_time = RATE_LIMIT_DELAY * (2 ** retry_count)  # Exponential backoff
                logger.warning(f"Attempt {retry_count} failed: {str(e)}. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                
        if result is None:
            error_msg = f"Text Generator failed after {MAX_RETRIES} attempts"
            logger.error(error_msg)
            state.errors.append(error_msg)
            state.is_error = True
            return False
        
        # Update the state with the result
        if isinstance(result, dict):
            if "core_content" in result:
                state.core_content = result["core_content"]
            if "is_error" in result and result["is_error"]:
                error_msg = f"Text Generator failed: {result.get('errors', ['Unknown error'])}"
                logger.error(error_msg)
                state.errors.append(error_msg)
                state.is_error = True
                return False
        
        # Check for errors in the state object
        if hasattr(state, 'is_error') and state.is_error:
            error_msg = f"Text Generator failed: {getattr(state, 'errors', ['Unknown error'])}"
            logger.error(error_msg)
            return False
            
        # Display results
        print("\n=== GENERATED CONTENT ===")
        print(getattr(state, 'core_content', 'No content generated'))
        
        # Save results
        with open("essential_agents_output.txt", "w", encoding="utf-8") as f:
            f.write("=== PROMPT ===\n")
            f.write(prompt)
            f.write("\n\n=== GENERATED CONTENT ===\n")
            f.write(getattr(state, 'core_content', 'No content generated'))
        
        logger.info("Test completed successfully. Output saved to 'essential_agents_output.txt'")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    asyncio.run(test_essential_agents())
