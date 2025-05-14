from typing import Dict, Any
import logging
import json
import re

logger = logging.getLogger(__name__)

class TransformProvider:
    def __init__(self):
        pass
    
    def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data transformation"""
        try:
            transform_type = config.get("transform_type", "jq")
            expression = config.get("expression", ".")
            input_data = inputs.get("input", {})
            
            if transform_type == "jq":
                return self._transform_jq(expression, input_data)
            elif transform_type == "regex":
                return self._transform_regex(expression, input_data)
            elif transform_type == "template":
                return self._transform_template(expression, input_data)
            else:
                return {"error": f"Unsupported transform type: {transform_type}"}
        
        except Exception as e:
            logger.error(f"Error in transform: {str(e)}")
            return {"error": str(e)}
    
    def _transform_jq(self, expression: str, data: Any) -> Dict[str, Any]:
        """Simple implementation of jq-like functionality
        Note: This is a very simple implementation and doesn't support full jq syntax
        """
        try:
            # Basic identity operation
            if expression == ".":
                return {"output": data}
            
            # Property access (e.g., ".property")
            property_match = re.match(r'^\.(\w+)$', expression)
            if property_match and isinstance(data, dict):
                prop = property_match.group(1)
                if prop in data:
                    return {"output": data[prop]}
                else:
                    return {"output": None}
            
            # Array index access (e.g., ".[0]")
            index_match = re.match(r'^\.(\[\d+\])$', expression)
            if index_match and isinstance(data, list):
                index_str = index_match.group(1)
                index = int(index_str[1:-1])  # Remove [ and ]
                if 0 <= index < len(data):
                    return {"output": data[index]}
                else:
                    return {"output": None}
            
            return {"output": data, "warning": "Unsupported jq expression"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def _transform_regex(self, expression: str, data: Any) -> Dict[str, Any]:
        """Apply regex transformation"""
        try:
            if not isinstance(data, str):
                data = json.dumps(data)
            
            matches = re.findall(expression, data)
            return {"output": matches}
        
        except Exception as e:
            return {"error": str(e)}
    
    def _transform_template(self, template: str, data: Any) -> Dict[str, Any]:
        """Apply simple template transformation
        Replaces {{variable}} with values from the data
        """
        try:
            if not isinstance(data, dict):
                return {"output": template, "warning": "Template requires dictionary input"}
            
            result = template
            for key, value in data.items():
                placeholder = "{{" + key + "}}"
                # Convert value to string if it's not already
                if not isinstance(value, str):
                    value = json.dumps(value)
                result = result.replace(placeholder, value)
            
            return {"output": result}
        
        except Exception as e:
            return {"error": str(e)}
