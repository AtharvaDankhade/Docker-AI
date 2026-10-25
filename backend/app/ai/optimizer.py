"""AI optimization module (Ollama integration)"""
import asyncio
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import httpx

from ..core.config import get_settings
from ..models.schemas import ProjectInfo


@dataclass
class OllamaResponse:
    """Response from Ollama API"""
    success: bool
    content: str = ""
    error: str = ""


class OllamaClient:
    """Client for Ollama API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.ollama_host.rstrip("/")
        self.model = self.settings.ollama_model
        self.timeout = self.settings.ollama_timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def check_health(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    async def generate(self, prompt: str, system_prompt: str = "") -> OllamaResponse:
        """Generate completion from Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 1024,
                }
            }
            if system_prompt:
                payload["system"] = system_prompt
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            
            if response.status_code == 200:
                data = response.json()
                return OllamaResponse(success=True, content=data.get("response", ""))
            else:
                return OllamaResponse(success=False, error=f"HTTP {response.status_code}: {response.text}")
        
        except httpx.TimeoutException:
            return OllamaResponse(success=False, error="Request timeout")
        except Exception as e:
            return OllamaResponse(success=False, error=str(e))
    
    async def pull_model(self) -> bool:
        """Pull model if not available"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model},
                timeout=300,
            )
            return response.status_code == 200
        except Exception:
            return False


class AIOptimizer:
    """AI-powered Dockerfile optimizer using Ollama"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = OllamaClient() if self.settings.ollama_enabled else None
        self._available: Optional[bool] = None
    
    def is_available(self) -> bool:
        """Check if AI optimizer is available"""
        if not self.settings.ollama_enabled or not self.client:
            return False
        if self._available is None:
            # Async check would be better but keeping sync for simplicity
            self._available = False
        return self._available
    
    async def check_availability(self) -> bool:
        """Async check for Ollama availability"""
        if not self.settings.ollama_enabled or not self.client:
            self._available = False
            return False
        
        self._available = await self.client.check_health()
        return self._available
    
    def get_suggestions(self, project_info: ProjectInfo, dockerfile: str) -> Optional[List[str]]:
        """Get AI optimization suggestions (sync wrapper)"""
        if not self.is_available():
            return None
        
        # This would ideally be async, but for sync compatibility we return None
        # The async version should be used in async contexts
        return None
    
    async def get_suggestions_async(self, project_info: ProjectInfo, dockerfile: str) -> List[str]:
        """Get AI optimization suggestions asynchronously"""
        if not await self.check_availability():
            return []
        
        prompt = self._build_prompt(project_info, dockerfile)
        system_prompt = self._get_system_prompt()
        
        response = await self.client.generate(prompt, system_prompt)
        
        if not response.success:
            return [f"AI optimization unavailable: {response.error}"]
        
        return self._parse_suggestions(response.content)
    
    def _get_system_prompt(self) -> str:
        return """You are a Dockerfile optimization expert. Analyze the provided Dockerfile and project information, then provide specific, actionable optimization suggestions. Focus on:
1. Security improvements
2. Build performance (layer caching, build time)
3. Runtime performance (image size, startup time)
4. Best practices compliance
5. Production readiness

Format your response as a JSON array of strings, each being a specific suggestion."""
    
    def _build_prompt(self, project_info: ProjectInfo, dockerfile: str) -> str:
        return f"""Project Information:
- Language: {project_info.language.value}
- Framework: {project_info.framework.value}
- Package Manager: {project_info.package_manager}
- Entry Point: {project_info.entry_point}
- Port: {project_info.port}
- Dependencies: {len(project_info.dependencies)} packages

Current Dockerfile:
```dockerfile
{dockerfile}
```

Provide 3-5 specific optimization suggestions as a JSON array of strings. Each suggestion should be actionable and specific to this project type."""
    
    def _parse_suggestions(self, content: str) -> List[str]:
        """Parse suggestions from AI response"""
        try:
            # Try to extract JSON array
            start = content.find('[')
            end = content.rfind(']') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                suggestions = json.loads(json_str)
                if isinstance(suggestions, list):
                    return [str(s) for s in suggestions if s]
        except Exception:
            pass
        
        # Fallback: split by lines
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        # Filter out non-suggestions
        suggestions = []
        for line in lines:
            # Remove common prefixes
            line = line.lstrip('- *•1234567890. ')
            if len(line) > 20 and not line.lower().startswith(('here', 'the following', 'suggestions:')):
                suggestions.append(line)
        
        return suggestions[:5]  # Limit to 5


# Global instance
_ai_optimizer: Optional[AIOptimizer] = None


def get_ai_optimizer() -> Optional[AIOptimizer]:
    """Get global AI optimizer instance"""
    global _ai_optimizer
    if _ai_optimizer is None:
        _ai_optimizer = AIOptimizer()
    return _ai_optimizer


async def get_ai_suggestions(project_info: ProjectInfo, dockerfile: str) -> List[str]:
    """Get AI suggestions asynchronously"""
    optimizer = get_ai_optimizer()
    if optimizer:
        return await optimizer.get_suggestions_async(project_info, dockerfile)
    return []