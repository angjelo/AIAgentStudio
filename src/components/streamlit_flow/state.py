from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .elements import StreamlitFlowNode, StreamlitFlowEdge

class StreamlitFlowState:
    def __init__(
        self,
        nodes: List[StreamlitFlowNode] = None,
        edges: List[StreamlitFlowEdge] = None,
        selected_id: str = None
    ):
        self.nodes = nodes or []
        self.edges = edges or []
        self.selected_id = selected_id
        self.timestamp = int(datetime.now().timestamp() * 1000)
    
    def add_node(self, node: StreamlitFlowNode) -> None:
        """Add a node to the state"""
        self.nodes.append(node)
        self.timestamp = int(datetime.now().timestamp() * 1000)
    
    def add_edge(self, edge: StreamlitFlowEdge) -> None:
        """Add an edge to the state"""
        self.edges.append(edge)
        self.timestamp = int(datetime.now().timestamp() * 1000)
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node and its connected edges"""
        self.nodes = [node for node in self.nodes if node.id != node_id]
        self.edges = [edge for edge in self.edges 
                     if edge.source != node_id and edge.target != node_id]
        self.timestamp = int(datetime.now().timestamp() * 1000)
    
    def remove_edge(self, edge_id: str) -> None:
        """Remove an edge"""
        self.edges = [edge for edge in self.edges if edge.id != edge_id]
        self.timestamp = int(datetime.now().timestamp() * 1000)
    
    def get_node(self, node_id: str) -> Optional[StreamlitFlowNode]:
        """Get a node by ID"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def update_node(self, node_id: str, updates: Dict[str, Any]) -> bool:
        """Update a node with new attributes"""
        for i, node in enumerate(self.nodes):
            if node.id == node_id:
                for key, value in updates.items():
                    if hasattr(node, key):
                        setattr(node, key, value)
                self.timestamp = int(datetime.now().timestamp() * 1000)
                return True
        return False
    
    def update(self) -> None:
        """Update the timestamp to trigger a re-render"""
        self.timestamp = int(datetime.now().timestamp() * 1000)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            'nodes': [node.to_dict() for node in self.nodes],
            'edges': [edge.to_dict() for edge in self.edges],
            'selected_id': self.selected_id,
            'timestamp': self.timestamp
        }
    
    def serialize(self) -> str:
        """Serialize state to JSON string"""
        return json.dumps(self.to_dict())