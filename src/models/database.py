from sqlalchemy import Column, String, Text, JSON, ForeignKey, DateTime, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import json
from typing import Dict, Any, List, Optional
import uuid

from src.utils.config import get_config_value

# Create SQLAlchemy base class
Base = declarative_base()

class AgentModel(Base):
    """Database model for Agent"""
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    nodes = relationship("NodeModel", back_populates="agent", cascade="all, delete-orphan")
    edges = relationship("EdgeModel", back_populates="agent", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges]
        }

class NodeModel(Base):
    """Database model for Node"""
    __tablename__ = "nodes"
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    config = Column(JSON, default=dict)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="nodes")
    inputs = relationship("NodeIOModel", 
                         primaryjoin="and_(NodeModel.id==NodeIOModel.node_id, NodeIOModel.io_type=='input')",
                         cascade="all, delete-orphan")
    outputs = relationship("NodeIOModel", 
                          primaryjoin="and_(NodeModel.id==NodeIOModel.node_id, NodeIOModel.io_type=='output')",
                          cascade="all, delete-orphan",
                          overlaps="inputs")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "position": {
                "x": self.position_x,
                "y": self.position_y
            },
            "config": self.config,
            "inputs": [input_io.to_dict() for input_io in self.inputs],
            "outputs": [output_io.to_dict() for output_io in self.outputs]
        }

class NodeIOModel(Base):
    """Database model for Node inputs and outputs"""
    __tablename__ = "node_ios"
    
    id = Column(String, primary_key=True)
    node_id = Column(String, ForeignKey("nodes.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    data_type = Column(String, nullable=False)
    io_type = Column(String, nullable=False)  # 'input' or 'output'
    connected_to = Column(JSON, default=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "data_type": self.data_type,
            "connected_to": self.connected_to
        }

class EdgeModel(Base):
    """Database model for Edge (connections between nodes)"""
    __tablename__ = "edges"
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    source_node_id = Column(String, nullable=False)
    source_output_id = Column(String, nullable=False)
    target_node_id = Column(String, nullable=False)
    target_input_id = Column(String, nullable=False)
    
    # Relationships
    agent = relationship("AgentModel", back_populates="edges")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "source_node_id": self.source_node_id,
            "source_output_id": self.source_output_id,
            "target_node_id": self.target_node_id,
            "target_input_id": self.target_input_id
        }

# Database connection management
class Database:
    def __init__(self):
        """Initialize database connection"""
        self.db_url = get_config_value("database.url")
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all defined tables"""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
        
    def close(self):
        """Close database connection"""
        self.engine.dispose()

# Create global database instance
db = Database()