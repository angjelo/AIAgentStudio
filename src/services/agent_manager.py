import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from src.models.node import Agent, Node, Edge, Position, NodeIO
from src.models.node_types import NODE_TYPES, NodeType
from src.services.database_manager import DatabaseManager
from src.utils.config import get_config_value

logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self, save_dir: str = "saved_agents"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        self.agents: Dict[str, Agent] = {}
        self.use_database = get_config_value("database.enable_persistence", True)
        
        # Initialize database if using persistence
        if self.use_database:
            DatabaseManager.initialize_database()
            
        self._load_agents()
    
    def _load_agents(self) -> None:
        """Load all saved agents"""
        if self.use_database:
            try:
                # Load from database
                db_agents = DatabaseManager.get_all_agents()
                for agent in db_agents:
                    loaded_agent = DatabaseManager.load_agent(agent.id)
                    if loaded_agent:
                        self.agents[agent.id] = loaded_agent
                logger.info(f"Loaded {len(self.agents)} agents from database")
            except Exception as e:
                logger.error(f"Error loading agents from database: {e}")
                # Fall back to file-based loading
                self._load_agents_from_files()
        else:
            # Use file-based loading
            self._load_agents_from_files()
    
    def _load_agents_from_files(self) -> None:
        """Load agents from JSON files as fallback"""
        try:
            for filename in os.listdir(self.save_dir):
                if filename.endswith(".json"):
                    try:
                        with open(os.path.join(self.save_dir, filename), "r") as f:
                            agent_data = json.load(f)
                            agent = Agent.from_dict(agent_data)
                            self.agents[agent.id] = agent
                    except Exception as e:
                        logger.error(f"Error loading agent {filename}: {e}")
            logger.info(f"Loaded {len(self.agents)} agents from files")
        except Exception as e:
            logger.error(f"Error loading agents from files: {e}")
    
    def create_agent(self, name: str, description: Optional[str] = None) -> Agent:
        """Create a new agent with the given name and description"""
        now = datetime.now().isoformat()
        agent = Agent(
            name=name,
            description=description,
            created_at=now,
            updated_at=now
        )
        self.agents[agent.id] = agent
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents"""
        return list(self.agents.values())
    
    def update_agent(self, agent: Agent) -> Agent:
        """Update an existing agent"""
        agent.updated_at = datetime.now().isoformat()
        self.agents[agent.id] = agent
        return agent
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent by ID"""
        if agent_id not in self.agents:
            return False
            
        # Remove from memory
        del self.agents[agent_id]
        
        # Delete from database if enabled
        if self.use_database:
            success = DatabaseManager.delete_agent(agent_id)
            if not success:
                logger.warning(f"Failed to delete agent {agent_id} from database")
        
        # Delete file backup
        agent_path = os.path.join(self.save_dir, f"{agent_id}.json")
        if os.path.exists(agent_path):
            try:
                os.remove(agent_path)
            except Exception as e:
                logger.error(f"Error deleting agent file: {e}")
                
        return True
    
    def save_agent(self, agent_id: str) -> bool:
        """Save an agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
            
        success = True
        
        # Save to database if enabled
        if self.use_database:
            success = DatabaseManager.save_agent(agent)
            if not success:
                logger.error(f"Failed to save agent {agent.name} to database, falling back to file")
        
        # Save to file as backup or if database is not used
        if not self.use_database or not success:
            try:
                agent_path = os.path.join(self.save_dir, f"{agent_id}.json")
                with open(agent_path, "w") as f:
                    json.dump(agent.to_dict(), f, indent=2)
                success = True
                logger.info(f"Saved agent {agent.name} to file")
            except Exception as e:
                logger.error(f"Error saving agent to file: {e}")
                success = False
                
        return success
    
    def create_node(self, agent_id: str, node_type: str, name: str, position: Dict[str, float]) -> Optional[Node]:
        """Create a new node in the specified agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return None
        
        # Get node type definition
        node_type_def = NODE_TYPES.get(node_type)
        if not node_type_def:
            return None
        
        # Create inputs and outputs based on node type definition
        inputs = []
        for input_def in node_type_def.default_inputs:
            inputs.append(NodeIO(
                name=input_def["name"],
                data_type=input_def["data_type"],
                description=input_def.get("description")
            ))
        
        outputs = []
        for output_def in node_type_def.default_outputs:
            outputs.append(NodeIO(
                name=output_def["name"],
                data_type=output_def["data_type"],
                description=output_def.get("description")
            ))
        
        # Create the node
        node = Node(
            type=node_type,
            name=name,
            position=Position(**position),
            inputs=inputs,
            outputs=outputs,
            config=node_type_def.default_config.copy(),
            description=node_type_def.description
        )
        
        # Add the node to the agent
        agent.nodes.append(node)
        self.update_agent(agent)
        
        return node
    
    def update_node(self, agent_id: str, node_id: str, updates: Dict[str, Any]) -> Optional[Node]:
        """Update a node in the specified agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return None
        
        for i, node in enumerate(agent.nodes):
            if node.id == node_id:
                for key, value in updates.items():
                    if key == "position":
                        node.position = Position(**value)
                    elif key == "config":
                        node.config.update(value)
                    elif key == "inputs" or key == "outputs":
                        # Handle inputs/outputs updates
                        pass
                    else:
                        setattr(node, key, value)
                
                agent.nodes[i] = node
                self.update_agent(agent)
                return node
        
        return None
    
    def delete_node(self, agent_id: str, node_id: str) -> bool:
        """Delete a node from the specified agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        # Delete the node
        agent.nodes = [node for node in agent.nodes if node.id != node_id]
        
        # Delete any edges connected to this node
        agent.edges = [edge for edge in agent.edges if edge.source_node_id != node_id and edge.target_node_id != node_id]
        
        self.update_agent(agent)
        return True
    
    def create_edge(self, agent_id: str, source_node_id: str, source_output_id: str, 
                   target_node_id: str, target_input_id: str) -> Optional[Edge]:
        """Create a new edge connecting nodes in the specified agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return None
        
        # Find source node and output
        source_node = next((node for node in agent.nodes if node.id == source_node_id), None)
        source_output = next((output for output in source_node.outputs if output.id == source_output_id), None) if source_node else None
        
        # Find target node and input
        target_node = next((node for node in agent.nodes if node.id == target_node_id), None)
        target_input = next((input_item for input_item in target_node.inputs if input_item.id == target_input_id), None) if target_node else None
        
        if not source_node or not source_output or not target_node or not target_input:
            return None
        
        # Create the edge
        edge = Edge(
            source_node_id=source_node_id,
            source_output_id=source_output_id,
            target_node_id=target_node_id,
            target_input_id=target_input_id
        )
        
        # Add the edge to the agent
        agent.edges.append(edge)
        
        # Update the connections
        if target_input.connected_to is None:
            target_input.connected_to = []
        target_input.connected_to.append(source_output_id)
        
        self.update_agent(agent)
        return edge
    
    def delete_edge(self, agent_id: str, edge_id: str) -> bool:
        """Delete an edge from the specified agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        
        edge_to_delete = next((edge for edge in agent.edges if edge.id == edge_id), None)
        if not edge_to_delete:
            return False
        
        # Remove edge
        agent.edges = [edge for edge in agent.edges if edge.id != edge_id]
        
        # Update the target input's connected_to
        for node in agent.nodes:
            if node.id == edge_to_delete.target_node_id:
                for input_item in node.inputs:
                    if input_item.id == edge_to_delete.target_input_id and input_item.connected_to:
                        input_item.connected_to = [id for id in input_item.connected_to if id != edge_to_delete.source_output_id]
                        break
                break
        
        self.update_agent(agent)
        return True