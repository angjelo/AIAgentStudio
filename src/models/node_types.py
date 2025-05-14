from typing import Dict, List, Any
from pydantic import BaseModel, Field
from enum import Enum

class NodeType(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    LLM = "llm"
    API = "api"
    TRANSFORM = "transform"
    CONDITION = "condition"
    LOOP = "loop"

class DataType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    ANY = "any"

class NodeTypeDefinition(BaseModel):
    type: NodeType
    name: str
    description: str
    icon: str
    color: str
    category: str
    default_inputs: List[Dict[str, Any]] = []
    default_outputs: List[Dict[str, Any]] = []
    default_config: Dict[str, Any] = {}

# Define node types available in the application
NODE_TYPES: Dict[NodeType, NodeTypeDefinition] = {
    NodeType.INPUT: NodeTypeDefinition(
        type=NodeType.INPUT,
        name="Input",
        description="Provides input data to the agent",
        icon="input",
        color="#4CAF50",
        category="Basic",
        default_outputs=[
            {"name": "output", "data_type": DataType.ANY, "description": "Output data"}
        ],
        default_config={
            "input_type": "text",
            "label": "Input",
            "placeholder": "Enter input here",
            "default_value": ""
        }
    ),
    
    NodeType.OUTPUT: NodeTypeDefinition(
        type=NodeType.OUTPUT,
        name="Output",
        description="Displays output data from the agent",
        icon="output",
        color="#2196F3",
        category="Basic",
        default_inputs=[
            {"name": "input", "data_type": DataType.ANY, "description": "Input data"}
        ],
        default_config={
            "output_type": "text",
            "label": "Output"
        }
    ),
    
    NodeType.LLM: NodeTypeDefinition(
        type=NodeType.LLM,
        name="LLM",
        description="Makes calls to language models like GPT or Claude",
        icon="chat",
        color="#9C27B0",
        category="AI",
        default_inputs=[
            {"name": "prompt", "data_type": DataType.STRING, "description": "Prompt text"},
            {"name": "system", "data_type": DataType.STRING, "description": "System message"},
        ],
        default_outputs=[
            {"name": "response", "data_type": DataType.STRING, "description": "LLM response"},
        ],
        default_config={
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000,
        }
    ),
    
    NodeType.API: NodeTypeDefinition(
        type=NodeType.API,
        name="API",
        description="Makes HTTP requests to external APIs",
        icon="api",
        color="#FF5722",
        category="Integration",
        default_inputs=[
            {"name": "params", "data_type": DataType.OBJECT, "description": "Request parameters"},
            {"name": "headers", "data_type": DataType.OBJECT, "description": "HTTP headers"},
            {"name": "body", "data_type": DataType.ANY, "description": "Request body"},
        ],
        default_outputs=[
            {"name": "response", "data_type": DataType.ANY, "description": "API response"},
            {"name": "status", "data_type": DataType.NUMBER, "description": "HTTP status code"},
        ],
        default_config={
            "url": "",
            "method": "GET",
            "timeout": 30,
        }
    ),
    
    NodeType.TRANSFORM: NodeTypeDefinition(
        type=NodeType.TRANSFORM,
        name="Transform",
        description="Transforms data from one format to another",
        icon="transform",
        color="#FFC107",
        category="Data",
        default_inputs=[
            {"name": "input", "data_type": DataType.ANY, "description": "Input data"},
        ],
        default_outputs=[
            {"name": "output", "data_type": DataType.ANY, "description": "Transformed data"},
        ],
        default_config={
            "transform_type": "jq",
            "expression": ".",
        }
    ),
    
    NodeType.CONDITION: NodeTypeDefinition(
        type=NodeType.CONDITION,
        name="Condition",
        description="Evaluates a condition and routes data accordingly",
        icon="branch",
        color="#607D8B",
        category="Flow Control",
        default_inputs=[
            {"name": "condition", "data_type": DataType.BOOLEAN, "description": "Condition to evaluate"},
            {"name": "data", "data_type": DataType.ANY, "description": "Data to route"},
        ],
        default_outputs=[
            {"name": "true", "data_type": DataType.ANY, "description": "Output if condition is true"},
            {"name": "false", "data_type": DataType.ANY, "description": "Output if condition is false"},
        ],
        default_config={
            "condition_type": "expression",
            "expression": "data != null",
        }
    ),
    
    NodeType.LOOP: NodeTypeDefinition(
        type=NodeType.LOOP,
        name="Loop",
        description="Iterates over an array or performs a loop",
        icon="loop",
        color="#795548",
        category="Flow Control",
        default_inputs=[
            {"name": "items", "data_type": DataType.ARRAY, "description": "Items to iterate over"},
        ],
        default_outputs=[
            {"name": "item", "data_type": DataType.ANY, "description": "Current item"},
            {"name": "index", "data_type": DataType.NUMBER, "description": "Current index"},
            {"name": "results", "data_type": DataType.ARRAY, "description": "Collected results"},
        ],
        default_config={
            "loop_type": "for_each",
            "collect_results": True,
        }
    ),
}