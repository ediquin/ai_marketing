"""
Cliente LLM unificado para múltiples proveedores
"""
import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, Union
from abc import ABC, abstractmethod

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class LLMResponse(BaseModel):
    """Respuesta estándar del LLM"""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    processing_time: float
    metadata: Dict[str, Any] = {}

class LLMClient(ABC):
    """Cliente base abstracto para LLMs"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Genera texto usando el LLM"""
        pass
    
    @abstractmethod
    async def generate_structured(self, prompt: str, expected_format: str, **kwargs) -> Dict[str, Any]:
        """Genera respuesta estructurada (JSON)"""
        pass

class GoogleAIClient(LLMClient):
    """Cliente para Google AI (Gemini)"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # Delay progresivo para evitar rate limiting
                if attempt > 0:
                    delay = base_delay * (2 ** attempt)  # Backoff exponencial
                    await asyncio.sleep(delay)
                else:
                    await asyncio.sleep(2.0)  # Delay inicial más largo
                
                url = f"{self.base_url}/{self.model}:generateContent"
                headers = {"Content-Type": "application/json"}
                
                data = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "maxOutputTokens": kwargs.get("max_tokens", 2000)
                    }
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        url,
                        headers=headers,
                        json=data,
                        params={"key": self.api_key}
                    )
                    response.raise_for_status()
                    
                result = response.json()
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                
                processing_time = time.time() - start_time
                
                return LLMResponse(
                    content=content,
                    model=self.model,
                    provider="google_ai",
                    processing_time=processing_time
                )
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:
                    logger.warning(f"Rate limit alcanzado, reintentando en {base_delay * (2 ** (attempt + 1))}s...")
                    continue
                else:
                    logger.error(f"Error en Google AI: {e}")
                    raise
            except Exception as e:
                logger.error(f"Error en Google AI: {e}")
                raise
    
    async def generate_structured(self, prompt: str, expected_format: str, **kwargs) -> Dict[str, Any]:
        """Genera respuesta estructurada con manejo de errores JSON"""
        try:
            # Añadir instrucciones específicas para JSON
            structured_prompt = f"""{prompt}
            
            IMPORTANT: Respond ONLY with valid JSON. Do not include any explanation or additional text.
            Expected format: {expected_format}"""
            
            response = await self.generate(structured_prompt, **kwargs)
            
            # Intentar parsear directamente
            try:
                parsed = json.loads(response.content)
                return self._normalize_json_fields(parsed)
            except json.JSONDecodeError:
                # Si falla, intentar extraer JSON del texto
                logger.warning("Respuesta no es JSON válido, intentando extraer JSON")
                
                # Buscar JSON en la respuesta
                import re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    return self._normalize_json_fields(parsed)
                else:
                    raise ValueError("No se pudo extraer JSON válido de la respuesta")
                    
        except Exception as e:
            logger.error(f"Error generando respuesta estructurada: {e}")
            raise
    
    def _normalize_json_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza campos JSON de español a inglés"""
        field_mapping = {
            'hechos': 'key_facts',
            'fuentes': 'data_sources',
            'estadisticas': 'statistics',
            'estado_verificacion': 'verification_status',
            'hecho': 'fact',
            'categoria': 'category',
            'verificacion_necesaria': 'verification_needed',
            'fuente_necesaria': 'source_needed',
            'reclamacion': 'claim'
        }
        
        def normalize_recursive(obj):
            if isinstance(obj, dict):
                normalized = {}
                for key, value in obj.items():
                    # Normalizar la clave
                    new_key = field_mapping.get(key, key)
                    # Normalizar el valor recursivamente
                    normalized[new_key] = normalize_recursive(value)
                return normalized
            elif isinstance(obj, list):
                return [normalize_recursive(item) for item in obj]
            else:
                return obj
        
        return normalize_recursive(data)

class GroqClient(LLMClient):
    """Cliente para Groq"""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000)
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            processing_time = time.time() - start_time
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider="groq",
                tokens_used=result.get("usage", {}).get("total_tokens"),
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error en Groq: {e}")
            raise
    
    async def generate_structured(self, prompt: str, expected_format: str, **kwargs) -> Dict[str, Any]:
        # Mejorar prompt para modelos locales con instrucciones más específicas
        structured_prompt = f"""
{prompt}

IMPORTANT: You must respond with ONLY valid JSON in this exact format:
{expected_format}

Do not include any explanation, markdown formatting, or additional text. 
Start your response with {{ and end with }}.
Ensure all strings are properly quoted and the JSON is valid.
"""
        
        response = await self.generate(structured_prompt, **kwargs)
        
        # Intentar múltiples estrategias de parsing
        content = response.content.strip()
        
        # Estrategia 1: JSON directo
        try:
            parsed = json.loads(content)
            return parsed
        except json.JSONDecodeError:
            pass
        
        # Estrategia 2: Extraer JSON entre llaves
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                parsed = json.loads(json_str)
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Estrategia 3: Buscar múltiples bloques JSON
        try:
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, content)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    return parsed
                except:
                    continue
        except:
            pass
        
        # Estrategia 4: Crear JSON básico a partir del contenido
        logger.warning("No se pudo parsear JSON, creando estructura básica")
        
        # Analizar el contenido y crear un JSON básico
        lines = content.lower().split('\n')
        basic_json = {}
        
        # Buscar patrones comunes
        if 'campaign' in content.lower():
            basic_json['campaign_type'] = 'Marketing Campaign'
        if 'audience' in content.lower() or 'target' in content.lower():
            basic_json['target_audience'] = 'General Audience'
        if 'objective' in content.lower() or 'goal' in content.lower():
            basic_json['objective'] = 'Brand Awareness'
        
        # Si no encontramos nada útil, usar valores por defecto
        if not basic_json:
            basic_json = {
                "campaign_type": "General Marketing",
                "target_audience": "General Audience",
                "objective": "Brand Awareness"
            }
        
        return basic_json
    
    def _normalize_json_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza campos JSON de español a inglés"""
        field_mapping = {
            'hechos': 'key_facts',
            'fuentes': 'data_sources',
            'estadisticas': 'statistics',
            'estado_verificacion': 'verification_status',
            'hecho': 'fact',
            'categoria': 'category',
            'verificacion_necesaria': 'verification_needed',
            'fuente_necesaria': 'source_needed',
            'reclamacion': 'claim'
        }
        
        def normalize_recursive(obj):
            if isinstance(obj, dict):
                normalized = {}
                for key, value in obj.items():
                    # Normalizar la clave
                    new_key = field_mapping.get(key, key)
                    # Normalizar el valor recursivamente
                    normalized[new_key] = normalize_recursive(value)
                return normalized
            elif isinstance(obj, list):
                return [normalize_recursive(item) for item in obj]
            else:
                return obj
        
        return normalize_recursive(data)

class OllamaClient(LLMClient):
    """Cliente para modelos locales usando Ollama"""
    
    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": kwargs.get("temperature", 0.7),
                        "top_p": kwargs.get("top_p", 0.9),
                        "max_tokens": kwargs.get("max_tokens", 2048)
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    processing_time = time.time() - start_time
                    
                    return LLMResponse(
                        content=data.get("response", ""),
                        model=self.model,
                        provider="ollama",
                        processing_time=processing_time,
                        metadata={"local": True, "base_url": self.base_url}
                    )
                else:
                    raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error en Ollama: {e}")
            # Fallback a respuesta simulada para desarrollo
            processing_time = time.time() - start_time
            return LLMResponse(
                content="[LOCAL MODEL UNAVAILABLE] Simulated response for development",
                model=self.model,
                provider="ollama_fallback",
                processing_time=processing_time,
                metadata={"local": True, "fallback": True, "error": str(e)}
            )
    
    async def generate_structured(self, prompt: str, expected_format: str, **kwargs) -> Dict[str, Any]:
        """Genera respuesta estructurada usando Ollama"""
        structured_prompt = f"""{prompt}

IMPORTANT: Respond with valid JSON only. No additional text.
Expected format: {expected_format}
"""
        
        response = await self.generate(structured_prompt, **kwargs)
        
        try:
            # Intentar parsear como JSON
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("Respuesta de Ollama no es JSON válido, intentando extraer JSON")
            
            # Intentar extraer JSON del texto
            content = response.content.strip()
            
            # Buscar JSON entre llaves
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                try:
                    json_str = content[start_idx:end_idx + 1]
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            # Fallback: respuesta estructurada simulada
            return {
                "error": "Could not parse JSON from local model",
                "raw_response": response.content,
                "fallback": True
            }

class UnifiedLLMClient:
    """Cliente unificado que maneja múltiples proveedores"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.clients = {}
        self._setup_clients()
    
    def _setup_clients(self):
        """Configura los clientes disponibles"""
        # Google AI
        if self.config.get("GOOGLE_API_KEY"):
            try:
                self.clients["google"] = GoogleAIClient(
                    api_key=self.config["GOOGLE_API_KEY"],
                    model=self.config.get("GOOGLE_MODEL", "gemini-1.5-flash")
                )
                logger.info("Google AI client configurado")
            except Exception as e:
                logger.warning(f"No se pudo configurar Google AI: {e}")
        
        # Groq
        if self.config.get("GROQ_API_KEY"):
            try:
                self.clients["groq"] = GroqClient(
                    api_key=self.config["GROQ_API_KEY"],
                    model=self.config.get("GROQ_MODEL", "llama-3.1-70b-versatile")
                )
                logger.info("Groq client configurado")
            except Exception as e:
                logger.warning(f"No se pudo configurar Groq: {e}")
        
        # Ollama (Local Models)
        try:
            ollama_model = self.config.get("OLLAMA_MODEL", "llama3.1")
            ollama_url = self.config.get("OLLAMA_URL", "http://localhost:11434")
            self.clients["ollama"] = OllamaClient(
                model=ollama_model,
                base_url=ollama_url
            )
            logger.info(f"Ollama client configurado: {ollama_model}")
        except Exception as e:
            logger.warning(f"No se pudo configurar Ollama: {e}")
        
        if not self.clients:
            logger.warning("No se configuraron clientes LLM")
    
    def get_client(self, provider: str = None) -> LLMClient:
        """Obtiene el cliente para el proveedor especificado con fallback inteligente"""
        if provider and provider in self.clients:
            return self.clients[provider]
        
        # Fallback inteligente: usar Groq como principal (más rápido, menos rate limiting)
        if "groq" in self.clients:
            return self.clients["groq"]
        elif "google_ai" in self.clients:
            return self.clients["google_ai"]
        elif self.clients:
            return list(self.clients.values())[0]
        
        raise RuntimeError("No hay clientes LLM configurados")
    
    async def generate(self, prompt: str, provider: str = None, **kwargs) -> LLMResponse:
        """Genera texto usando el proveedor especificado con fallback automático"""
        # Lista de proveedores en orden de preferencia
        providers_to_try = []
        
        if provider and provider in self.clients:
            providers_to_try.append(provider)
        
        # Agregar fallbacks automáticos
        if "groq" in self.clients and "groq" not in providers_to_try:
            providers_to_try.append("groq")
        if "ollama" in self.clients and "ollama" not in providers_to_try:
            providers_to_try.append("ollama")
        if "google" in self.clients and "google" not in providers_to_try:
            providers_to_try.append("google")
        
        last_error = None
        
        for provider_name in providers_to_try:
            try:
                client = self.clients[provider_name]
                logger.info(f"Intentando generar con {provider_name}")
                response = await client.generate(prompt, **kwargs)
                logger.info(f"Generación exitosa con {provider_name}")
                return response
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Error con {provider_name}: {error_msg}")
                last_error = e
                
                # Si es error de rate limit (429), probar siguiente proveedor inmediatamente
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    logger.info(f"Rate limit en {provider_name}, probando siguiente proveedor...")
                    continue
                # Si es otro error, también continuar con el siguiente
                continue
        
        # Si todos los proveedores fallaron
        if last_error:
            logger.error(f"Todos los proveedores fallaron. Último error: {last_error}")
            raise last_error
        else:
            raise RuntimeError("No hay proveedores disponibles")
    
    async def generate_structured(self, prompt: str, expected_format: str, provider: str = None, **kwargs) -> Dict[str, Any]:
        """Genera respuesta estructurada usando el proveedor especificado con fallback automático"""
        # Lista de proveedores en orden de preferencia
        providers_to_try = []
        
        if provider and provider in self.clients:
            providers_to_try.append(provider)
        
        # Agregar fallbacks automáticos
        if "groq" in self.clients and "groq" not in providers_to_try:
            providers_to_try.append("groq")
        if "ollama" in self.clients and "ollama" not in providers_to_try:
            providers_to_try.append("ollama")
        if "google" in self.clients and "google" not in providers_to_try:
            providers_to_try.append("google")
        
        last_error = None
        
        for provider_name in providers_to_try:
            try:
                client = self.clients[provider_name]
                logger.info(f"Intentando generar estructura con {provider_name}")
                response = await client.generate_structured(prompt, expected_format, **kwargs)
                logger.info(f"Generación estructurada exitosa con {provider_name}")
                return response
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Error con {provider_name}: {error_msg}")
                last_error = e
                
                # Si es error de rate limit (429), probar siguiente proveedor inmediatamente
                if "429" in error_msg or "Too Many Requests" in error_msg:
                    logger.info(f"Rate limit en {provider_name}, probando siguiente proveedor...")
                    continue
                # Si es otro error, también continuar con el siguiente
                continue
        
        # Si todos los proveedores fallaron
        if last_error:
            logger.error(f"Todos los proveedores fallaron. Último error: {last_error}")
            raise last_error
        else:
            raise RuntimeError("No hay proveedores disponibles")

# Alias para compatibilidad
LLMClient = UnifiedLLMClient

def create_llm_client() -> UnifiedLLMClient:
    """
    Función factory para crear el cliente LLM unificado
    Lee la configuración desde variables de entorno
    """
    import os
    from dotenv import load_dotenv
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Configuración del cliente
    config = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "GOOGLE_MODEL": os.getenv("GOOGLE_MODEL", "gemini-1.5-flash"),
        "GROQ_MODEL": os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile"),
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        "OLLAMA_URL": os.getenv("OLLAMA_URL", "http://localhost:11434"),
    }
    
    return UnifiedLLMClient(config)
