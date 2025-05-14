from typing import Dict, List, Optional, Any
import logging
from datetime import datetime


from src.models.database import db, AgentModel, NodeModel, NodeIOModel, EdgeModel
from src.models.node import Agent, Node, Edge, Position, NodeIO

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles database operations for agents, nodes, and edges"""
    
    @staticmethod
    def initialize_database():
        """Initialize database and create tables"""
        try:
            db.create_tables()
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return False
    
    @staticmethod
    def save_agent(agent: Agent) -> bool:
        """Save agent to database"""
        session = db.get_session()
        try:
            # Check if agent already exists
            db_agent = session.query(AgentModel).filter(AgentModel.id == agent.id).first()
            
            if db_agent:
                # Update existing agent
                db_agent.name = agent.name
                db_agent.description = agent.description
                db_agent.updated_at = datetime.now()
                
                # Delete existing nodes and edges
                session.query(NodeIOModel).filter(
                    NodeIOModel.node_id.in_([node.id for node in db_agent.nodes])
                ).delete(synchronize_session=False)
                
                session.query(NodeModel).filter(
                    NodeModel.agent_id == agent.id
                ).delete(synchronize_session=False)
                
                session.query(EdgeModel).filter(
                    EdgeModel.agent_id == agent.id
                ).delete(synchronize_session=False)
            else:
                # Create new agent
                db_agent = AgentModel(
                    id=agent.id,
                    name=agent.name,
                    description=agent.description,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(db_agent)
            
            # Add nodes
            for node in agent.nodes:
                db_node = NodeModel(
                    id=node.id,
                    agent_id=agent.id,
                    type=node.type,
                    name=node.name,
                    description=node.description,
                    position_x=node.position.x,
                    position_y=node.position.y,
                    config=node.config
                )
                session.add(db_node)
                
                # Add inputs
                for input_io in node.inputs:
                    db_input = NodeIOModel(
                        id=input_io.id,
                        node_id=node.id,
                        name=input_io.name,
                        description=input_io.description,
                        data_type=input_io.data_type,
                        io_type="input",
                        connected_to=input_io.connected_to if input_io.connected_to else []
                    )
                    session.add(db_input)
                
                # Add outputs
                for output_io in node.outputs:
                    db_output = NodeIOModel(
                        id=output_io.id,
                        node_id=node.id,
                        name=output_io.name,
                        description=output_io.description,
                        data_type=output_io.data_type,
                        io_type="output",
                        connected_to=[]
                    )
                    session.add(db_output)
            
            # Add edges
            for edge in agent.edges:
                db_edge = EdgeModel(
                    id=edge.id,
                    agent_id=agent.id,
                    source_node_id=edge.source_node_id,
                    source_output_id=edge.source_output_id,
                    target_node_id=edge.target_node_id,
                    target_input_id=edge.target_input_id
                )
                session.add(db_edge)
            
            session.commit()
            return True
        
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving agent to database: {e}")
            return False
        
        finally:
            session.close()
    
    @staticmethod
    def load_agent(agent_id: str) -> Optional[Agent]:
        """Load agent from database"""
        session = db.get_session()
        try:
            db_agent = session.query(AgentModel).filter(AgentModel.id == agent_id).first()
            
            if not db_agent:
                return None
                
            # Create nodes
            nodes = []
            for db_node in db_agent.nodes:
                # Create inputs
                inputs = []
                for db_input in db_node.inputs:
                    inputs.append(NodeIO(
                        id=db_input.id,
                        name=db_input.name,
                        description=db_input.description,
                        data_type=db_input.data_type,
                        connected_to=db_input.connected_to
                    ))
                
                # Create outputs
                outputs = []
                for db_output in db_node.outputs:
                    outputs.append(NodeIO(
                        id=db_output.id,
                        name=db_output.name,
                        description=db_output.description,
                        data_type=db_output.data_type
                    ))
                
                # Create node
                node = Node(
                    id=db_node.id,
                    type=db_node.type,
                    name=db_node.name,
                    position=Position(x=db_node.position_x, y=db_node.position_y),
                    description=db_node.description,
                    config=db_node.config,
                    inputs=inputs,
                    outputs=outputs
                )
                nodes.append(node)
            
            # Create edges
            edges = []
            for db_edge in db_agent.edges:
                edge = Edge(
                    id=db_edge.id,
                    source_node_id=db_edge.source_node_id,
                    source_output_id=db_edge.source_output_id,
                    target_node_id=db_edge.target_node_id,
                    target_input_id=db_edge.target_input_id
                )
                edges.append(edge)
            
            # Create agent
            agent = Agent(
                id=db_agent.id,
                name=db_agent.name,
                description=db_agent.description,
                nodes=nodes,
                edges=edges,
                created_at=db_agent.created_at.isoformat() if db_agent.created_at else None,
                updated_at=db_agent.updated_at.isoformat() if db_agent.updated_at else None
            )
            
            return agent
        
        except Exception as e:
            logger.error(f"Error loading agent from database: {e}")
            return None
        
        finally:
            session.close()
    
    @staticmethod
    def get_all_agents() -> List[Agent]:
        """Get all agents from database"""
        session = db.get_session()
        try:
            db_agents = session.query(AgentModel).all()
            
            agents = []
            for db_agent in db_agents:
                agent = Agent(
                    id=db_agent.id,
                    name=db_agent.name,
                    description=db_agent.description,
                    created_at=db_agent.created_at.isoformat() if db_agent.created_at else None,
                    updated_at=db_agent.updated_at.isoformat() if db_agent.updated_at else None
                )
                agents.append(agent)
            
            return agents
        
        except Exception as e:
            logger.error(f"Error getting agents from database: {e}")
            return []
        
        finally:
            session.close()
    
    @staticmethod
    def delete_agent(agent_id: str) -> bool:
        """Delete agent from database"""
        session = db.get_session()
        try:
            # Query the agent
            db_agent = session.query(AgentModel).filter(AgentModel.id == agent_id).first()
            
            if not db_agent:
                return False
            
            # Delete the agent (cascade will delete nodes and edges)
            session.delete(db_agent)
            session.commit()
            
            return True
        
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting agent from database: {e}")
            return False
        
        finally:
            session.close()