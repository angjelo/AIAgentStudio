import os
from typing import Dict, Any
import logging

try:
    import anthropic
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

logger = logging.getLogger(__name__)

class AnthropicProvider:
    def __init__(self):
        self.client = None
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if HAS_ANTHROPIC and self.api_key:
            self.client = Anthropic(api_key=self.api_key)
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an Anthropic API call"""
        if not HAS_ANTHROPIC:
            return {"error": "Anthropic package not installed. Install with 'pip install anthropic'"}
        
        if not self.client:
            return {"error": "Anthropic API key not configured"}
        
        try:
            model = config.get("model", "claude-3-opus-20240229")
            temperature = config.get("temperature", 0.7)
            max_tokens = config.get("max_tokens", 1000)
            
            prompt = inputs.get("prompt", "")
            system = inputs.get("system", "You are a helpful AI assistant.")
            
            response = self.client.messages.create(
                model=model,
                system=system,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "response": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                "model": model
            }
        
        except Exception as e:
            logger.error(f"Error in Anthropic call: {str(e)}")
            return {"error": str(e)}
