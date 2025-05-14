import os
from typing import Dict, Any
import logging

try:
    import openai
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

logger = logging.getLogger(__name__)

class OpenAIProvider:
    def __init__(self):
        self.client = None
        self.api_key = os.environ.get("OPENAI_API_KEY")
        
        if HAS_OPENAI and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an OpenAI API call"""
        if not HAS_OPENAI:
            return {"error": "OpenAI package not installed. Install with 'pip install openai'"}
        
        if not self.client:
            return {"error": "OpenAI API key not configured"}
        
        try:
            model = config.get("model", "gpt-3.5-turbo")
            temperature = config.get("temperature", 0.7)
            max_tokens = config.get("max_tokens", 1000)
            
            prompt = inputs.get("prompt", "")
            system = inputs.get("system", "You are a helpful assistant.")
            
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "response": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": model
            }
        
        except Exception as e:
            logger.error(f"Error in OpenAI call: {str(e)}")
            return {"error": str(e)}
