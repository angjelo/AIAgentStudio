from typing import Dict, List, Any, Optional, Tuple, Literal
import math

class Layout:
    def __init__(self):
        pass

    def apply(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Apply layout to nodes. Base implementation returns nodes unchanged."""
        return nodes

class ManualLayout(Layout):
    def __init__(self):
        super().__init__()

class TreeLayout(Layout):
    def __init__(self, 
                 direction: Literal['up', 'down', 'left', 'right'] = 'down', 
                 node_node_spacing: float = 75):
        super().__init__()
        self.direction = direction
        self.node_node_spacing = node_node_spacing
    
    def apply(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Apply tree layout to nodes"""
        if not nodes:
            return nodes
            
        # Create a node mapping and find root nodes
        node_map = {node['id']: node for node in nodes}
        
        # Build adjacency list
        children = {node['id']: [] for node in nodes}
        has_parent = {node['id']: False for node in nodes}
        
        for edge in edges:
            source = edge['source']
            target = edge['target']
            
            if source in children and target in has_parent:
                children[source].append(target)
                has_parent[target] = True
        
        # Find root nodes (nodes without parents)
        roots = [node['id'] for node in nodes if not has_parent[node['id']]]
        
        # Use first node as root if no root was found
        if not roots and nodes:
            roots = [nodes[0]['id']]
            
        # Execute layout for each tree
        for root_id in roots:
            self._layout_tree(root_id, node_map, children)
            
        return list(node_map.values())
    
    def _layout_tree(self, root_id: str, node_map: Dict[str, Dict], children: Dict[str, List[str]], 
                   x: float = 100, y: float = 100, level: int = 0) -> Tuple[float, float]:
        """Recursively layout a tree starting from root_id"""
        node = node_map[root_id]
        
        # Position current node
        if self.direction == 'down':
            node['pos'] = (x, y + level * self.node_node_spacing)
        elif self.direction == 'up':
            node['pos'] = (x, y - level * self.node_node_spacing)
        elif self.direction == 'right':
            node['pos'] = (x + level * self.node_node_spacing, y)
        elif self.direction == 'left':
            node['pos'] = (x - level * self.node_node_spacing, y)
            
        # Position children
        child_count = len(children[root_id])
        if child_count == 0:
            return (node['pos'][0], node['pos'][1])
            
        # Calculate width needed for children
        total_width = (child_count - 1) * self.node_node_spacing
        start_pos = -total_width / 2
        
        for i, child_id in enumerate(children[root_id]):
            child_x_offset = start_pos + i * self.node_node_spacing
            
            # Determine child position based on direction
            if self.direction == 'down' or self.direction == 'up':
                child_x = x + child_x_offset
                self._layout_tree(child_id, node_map, children, child_x, y, level + 1)
            else:  # left or right
                child_y = y + child_x_offset
                self._layout_tree(child_id, node_map, children, x, child_y, level + 1)
                
        return (node['pos'][0], node['pos'][1])

class LayeredLayout(Layout):
    def __init__(self, 
                 direction: Literal['up', 'down', 'left', 'right'] = 'down', 
                 node_node_spacing: float = 75, 
                 node_layer_spacing: float = 75):
        super().__init__()
        self.direction = direction
        self.node_node_spacing = node_node_spacing
        self.node_layer_spacing = node_layer_spacing
    
    def apply(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Apply layered layout to nodes"""
        # Assign layers
        layers = self._assign_layers(nodes, edges)
        
        # Position nodes in each layer
        for layer_idx, layer_nodes in enumerate(layers):
            for node_idx, node_id in enumerate(layer_nodes):
                for node in nodes:
                    if node['id'] == node_id:
                        # Calculate position based on direction
                        if self.direction == 'down':
                            x = 100 + node_idx * self.node_node_spacing
                            y = 100 + layer_idx * self.node_layer_spacing
                        elif self.direction == 'up':
                            x = 100 + node_idx * self.node_node_spacing
                            y = 100 + (len(layers) - layer_idx - 1) * self.node_layer_spacing
                        elif self.direction == 'right':
                            x = 100 + layer_idx * self.node_layer_spacing
                            y = 100 + node_idx * self.node_node_spacing
                        elif self.direction == 'left':
                            x = 100 + (len(layers) - layer_idx - 1) * self.node_layer_spacing
                            y = 100 + node_idx * self.node_node_spacing
                            
                        node['pos'] = (x, y)
                        break
        
        return nodes
    
    def _assign_layers(self, nodes: List[Dict], edges: List[Dict]) -> List[List[str]]:
        """Assign nodes to layers based on dependencies"""
        # Map of node_id to incoming edge count
        node_ids = [node['id'] for node in nodes]
        incoming_edges = {node_id: 0 for node_id in node_ids}
        
        # Count incoming edges for each node
        for edge in edges:
            if edge['target'] in incoming_edges:
                incoming_edges[edge['target']] += 1
        
        # Start with nodes that have no incoming edges
        roots = [node_id for node_id in node_ids if incoming_edges[node_id] == 0]
        
        # If no roots are found, use the first node
        if not roots and node_ids:
            roots = [node_ids[0]]
            
        # Build layers using a topological sort approach
        visited = set()
        layers = []
        current_layer = roots
        
        while current_layer:
            layers.append(current_layer)
            next_layer = []
            
            for node_id in current_layer:
                visited.add(node_id)
                
                # Find outgoing edges
                outgoing = [edge['target'] for edge in edges if edge['source'] == node_id]
                
                # Add target nodes to next layer if all their dependencies are visited
                for target_id in outgoing:
                    if target_id not in visited and target_id not in next_layer:
                        # Check if all dependencies are visited
                        dependencies = [edge['source'] for edge in edges if edge['target'] == target_id]
                        if all(dep in visited for dep in dependencies):
                            next_layer.append(target_id)
            
            current_layer = next_layer
        
        # Add any unvisited nodes to a final layer
        remaining = [node_id for node_id in node_ids if node_id not in visited]
        if remaining:
            layers.append(remaining)
            
        return layers