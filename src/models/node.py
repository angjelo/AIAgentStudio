from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
import uuid

class NodeIO(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    data_type: str
    description: Optional[str] = None
    connected_to: Optional[List[str]] = None

class Position(BaseModel):
    x: float
    y: float

class Node(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    name: str
    position: Position
    inputs: List[NodeIO] = []
    outputs: List[NodeIO] = []
    config: Dict[str, Any] = {}
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Node':
        return Node(**data)


class Edge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_node_id: str
    source_output_id: str
    target_node_id: str
    target_input_id: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Edge':
        return Edge(**data)


class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    nodes: List[Node] = []
    edges: List[Edge] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Agent':
        return Agent(**data)