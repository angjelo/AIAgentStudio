import json
import logging
from typing import Dict, Any, List, Optional
import traceback

from src.models.node import Agent, Node, Edge
from src.models.node_types import NodeType
from src.services.providers.openai_provider import OpenAIProvider
from src.services.providers.anthropic_provider import AnthropicProvider
from src.services.providers.api_provider import APIProvider
from src.services.providers.transform_provider import TransformProvider

logger = logging.getLogger(__name__)

class AgentEngine:
    def __init__(self):
        self.providers = {
            NodeType.LLM: {
                "openai": OpenAIProvider(),
                "anthropic": AnthropicProvider(),
            },
            NodeType.API: APIProvider(),
            NodeType.TRANSFORM: TransformProvider(),
        }
        self.execution_cache = {}
    
    def execute_agent(self, agent: Agent, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent with the given input data"""
        logger.info(f"Executing agent: {agent.name}")
        
        # Reset execution cache
        self.execution_cache = {}
        
        # Find input nodes and set their values
        input_nodes = [node for node in agent.nodes if node.type == NodeType.INPUT]
        for input_node in input_nodes:
            input_key = input_node.config.get("input_name", "input")
            if input_key in input_data:
                self.execution_cache[f"{input_node.id}:output"] = input_data[input_key]
        
        # Find output nodes
        output_nodes = [node for node in agent.nodes if node.type == NodeType.OUTPUT]
        
        # Execute the graph until all output nodes have values
        output_results = {}
        for output_node in output_nodes:
            result = self._execute_node(agent, output_node.id)
            output_key = output_node.config.get("output_name", "output")
            output_results[output_key] = result
        
        return output_results
    
    def _execute_node(self, agent: Agent, node_id: str) -> Any:
        """Execute a single node and its dependencies"""
        # Check if we already computed this node
        if node_id in self.execution_cache:
            return self.execution_cache[node_id]
        
        # Find the node
        node = next((n for n in agent.nodes if n.id == node_id), None)
        if not node:
            raise ValueError(f"Node not found: {node_id}")
        
        logger.debug(f"Executing node: {node.name} ({node.type})")
        
        try:
            # If it's an input node, we should already have the value
            if node.type == NodeType.INPUT:
                output_value = self.execution_cache.get(f"{node.id}:output")
                if output_value is None:
                    output_value = node.config.get("default_value", "")
                return output_value
            
            # If it's an output node, we need to get the input value
            if node.type == NodeType.OUTPUT:
                # Find edges connecting to this node's inputs
                input_edges = [e for e in agent.edges if e.target_node_id == node.id]
                
                if input_edges:
                    # Use the first connected input
                    edge = input_edges[0]
                    source_node_id = edge.source_node_id
                    
                    # Recursively execute the source node
                    input_value = self._execute_node(agent, source_node_id)
                    
                    # Store the output in cache
                    self.execution_cache[node.id] = input_value
                    return input_value
                else:
                    # No input connected
                    return None
            
            # For other node types, gather inputs and execute
            inputs = {}
            for input_item in node.inputs:
                # Find edges connecting to this input
                input_edges = [e for e in agent.edges if e.target_node_id == node.id and e.target_input_id == input_item.id]
                
                if input_edges:
                    # Get the source node and output
                    edge = input_edges[0]
                    source_node_id = edge.source_node_id
                    source_output_id = edge.source_output_id
                    
                    # Recursively execute the source node
                    source_value = self._execute_node(agent, source_node_id)
                    
                    # Add to inputs
                    inputs[input_item.name] = source_value
                else:
                    # No input connected, use default value if available
                    default_key = f"default_{input_item.name}"
                    if default_key in node.config:
                        inputs[input_item.name] = node.config[default_key]
            
            # Execute the node based on its type
            result = self._execute_node_by_type(node, inputs)
            
            # Store the result in cache
            self.execution_cache[node.id] = result
            return result
        
        except Exception as e:
            logger.error(f"Error executing node {node.name}: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def _execute_node_by_type(self, node: Node, inputs: Dict[str, Any]) -> Any:
        """Execute a node based on its type"""
        if node.type == NodeType.LLM:
            provider_name = node.config.get("provider", "openai")
            provider = self.providers[NodeType.LLM].get(provider_name)
            if not provider:
                raise ValueError(f"LLM provider not found: {provider_name}")
            return provider.execute(node.config, inputs)
        
        elif node.type == NodeType.API:
            return self.providers[NodeType.API].execute(node.config, inputs)
        
        elif node.type == NodeType.TRANSFORM:
            return self.providers[NodeType.TRANSFORM].execute(node.config, inputs)
        
        elif node.type == NodeType.CONDITION:
            condition_result = self._evaluate_condition(node.config, inputs)
            if condition_result:
                return inputs.get("data")
            else:
                return None
        
        elif node.type == NodeType.LOOP:
            items = inputs.get("items", [])
            results = []
            
            for i, item in enumerate(items):
                result = {
                    "item": item,
                    "index": i,
                }
                if node.config.get("collect_results", True):
                    results.append(result)
            
            return {"results": results}
        
        else:
            raise ValueError(f"Unsupported node type: {node.type}")
    
    def _evaluate_condition(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> bool:
        """Evaluate a condition node"""
        condition_type = config.get("condition_type", "expression")
        
        if condition_type == "expression":
            # Very basic expression evaluation - this would be expanded in a real implementation
            expression = config.get("expression", "").strip()
            if expression == "true":
                return True
            elif expression == "false":
                return False
            elif expression == "data != null":
                return inputs.get("data") is not None
            else:
                # Default to True if we can't evaluate
                return True
        else:
            return True