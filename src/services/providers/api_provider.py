from typing import Dict, Any
import logging
import json

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

logger = logging.getLogger(__name__)

class APIProvider:
    def __init__(self):
        pass
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an API request"""
        if not HAS_REQUESTS:
            return {"error": "Requests package not installed. Install with 'pip install requests'"}
        
        try:
            url = config.get("url", "")
            method = config.get("method", "GET").upper()
            timeout = config.get("timeout", 30)
            
            if not url:
                return {"error": "URL is required"}
            
            params = inputs.get("params", {})
            headers = inputs.get("headers", {})
            body = inputs.get("body", None)
            
            # Convert body to JSON if it's a dict
            json_data = None
            data = None
            if body is not None:
                if isinstance(body, dict) or isinstance(body, list):
                    json_data = body
                else:
                    data = body
            
            response = requests.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                json=json_data,
                data=data,
                timeout=timeout
            )
            
            # Try to parse response as JSON
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text
            
            return {
                "response": response_data,
                "status": response.status_code,
                "headers": dict(response.headers)
            }
        
        except Exception as e:
            logger.error(f"Error in API call: {str(e)}")
            return {"error": str(e)}
