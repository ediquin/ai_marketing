"""
Detector de idioma y configuración de respuestas multiidioma
"""
import re
from typing import Dict, Optional
from enum import Enum

class Language(Enum):
    """Idiomas soportados"""
    SPANISH = "es"
    ENGLISH = "en"
    AUTO = "auto"

class LanguageDetector:
    """Detector de idioma basado en patrones y palabras clave"""
    
    def __init__(self):
        # Palabras clave comunes en español
        self.spanish_keywords = {
            'crear', 'generar', 'hacer', 'necesito', 'quiero', 'campaña', 
            'marketing', 'producto', 'empresa', 'cliente', 'venta', 'promoción',
            'lanzamiento', 'estrategia', 'contenido', 'publicidad', 'marca',
            'audiencia', 'mercado', 'negocio', 'servicio', 'oferta'
        }
        
        # Palabras clave comunes en inglés
        self.english_keywords = {
            'create', 'generate', 'make', 'need', 'want', 'campaign',
            'marketing', 'product', 'company', 'client', 'sale', 'promotion',
            'launch', 'strategy', 'content', 'advertising', 'brand',
            'audience', 'market', 'business', 'service', 'offer'
        }
        
        # Patrones de idioma
        self.spanish_patterns = [
            r'\b(el|la|los|las|un|una|de|del|en|con|por|para|que|es|son)\b',
            r'\b(ción|sión|dad|tad|mente)\b',
            r'[ñáéíóúü]'
        ]
        
        self.english_patterns = [
            r'\b(the|a|an|of|in|on|at|to|for|with|by|from|that|is|are)\b',
            r'\b(ing|tion|sion|ness|ment|able|ible)\b'
        ]
    
    def detect_language(self, text: str) -> Language:
        """
        Detecta el idioma del texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            Language detectado
        """
        if not text or len(text.strip()) < 10:
            return Language.SPANISH  # Default a español
        
        text_lower = text.lower()
        
        # Contar palabras clave
        spanish_score = sum(1 for word in self.spanish_keywords if word in text_lower)
        english_score = sum(1 for word in self.english_keywords if word in text_lower)
        
        # Contar patrones
        for pattern in self.spanish_patterns:
            spanish_score += len(re.findall(pattern, text_lower, re.IGNORECASE))
        
        for pattern in self.english_patterns:
            english_score += len(re.findall(pattern, text_lower, re.IGNORECASE))
        
        # Decidir idioma
        if english_score > spanish_score:
            return Language.ENGLISH
        else:
            return Language.SPANISH
    
    def get_language_config(self, detected_language: Language, user_override: Optional[Language] = None) -> Dict[str, str]:
        """
        Obtiene la configuración de idioma para los prompts
        
        Args:
            detected_language: Idioma detectado automáticamente
            user_override: Override manual del usuario
            
        Returns:
            Configuración de idioma para los prompts
        """
        # Usar override si está disponible, sino usar detección automática
        final_language = user_override if user_override and user_override != Language.AUTO else detected_language
        
        if final_language == Language.ENGLISH:
            return {
                "language": "en",
                "instruction": "Respond in English. Use professional English terminology for marketing and business concepts.",
                "format_instruction": "Format your response in English with clear, professional language.",
                "system_prompt_suffix": "\n\nIMPORTANT: Respond entirely in English."
            }
        else:  # Spanish
            return {
                "language": "es", 
                "instruction": "Responde en español. Usa terminología profesional en español para conceptos de marketing y negocios.",
                "format_instruction": "Formatea tu respuesta en español con lenguaje claro y profesional.",
                "system_prompt_suffix": "\n\nIMPORTANTE: Responde completamente en español."
            }

# Instancia global
language_detector = LanguageDetector()
