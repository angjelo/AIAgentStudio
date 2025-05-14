import streamlit as st
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from src.models.node import Node, Edge, Position
from src.models.node_types import NODE_TYPES, NodeType
from src.components.streamlit_flow import streamlit_flow, StreamlitFlowState, StreamlitFlowNode, StreamlitFlowEdge, LayeredLayout

# Define node styles based on node type
NODE_STYLES = {
    NodeType.INPUT: {
        "backgroundColor": "#4CAF50",
        "color": "white",
        "border": "1px solid #2E7D32",
        "borderRadius": "5px"
    },
    NodeType.OUTPUT: {
        "backgroundColor": "#2196F3",
        "color": "white",
        "border": "1px solid #1565C0",
        "borderRadius": "5px"
    },
    NodeType.LLM: {
        "backgroundColor": "#9C27B0",
        "color": "white",
        "border": "1px solid #6A1B9A",
        "borderRadius": "5px"
    },
    NodeType.API: {
        "backgroundColor": "#FF5722",
        "color": "white",
        "border": "1px solid #D84315",
        "borderRadius": "5px"
    },
    NodeType.TRANSFORM: {
        "backgroundColor": "#FFC107",
        "color": "black",
        "border": "1px solid #FFA000",
        "borderRadius": "5px"
    },
    NodeType.CONDITION: {
        "backgroundColor": "#607D8B",
        "color": "white",
        "border": "1px solid #455A64",
        "borderRadius": "5px"
    },
    NodeType.LOOP: {
        "backgroundColor": "#795548",
        "color": "white",
        "border": "1px solid #5D4037",
        "borderRadius": "5px"
    },
}

def render_canvas():
    """Render the custom canvas for node editing using our streamlit_flow implementation"""
    st.header("Agent Canvas")
    
    if not hasattr(st.session_state, "current_agent") or not st.session_state.current_agent:
        st.info("Select or create an agent to start building")
        return
    
    current_agent = st.session_state.agent_manager.get_agent(st.session_state.current_agent)
    if not current_agent:
        st.error("Selected agent not found")
        return
    
    # Canvas container with debug info
    with st.container():
        st.subheader("Add Node")
        create_node_selector(current_agent)
        
        # Canvas background with grid and nodes
        st.markdown("##### Flow Diagram")
        
        # Convert agent model to flow state
        flow_state = get_flow_state(current_agent)
        
        # Use our custom streamlit_flow implementation
        result = streamlit_flow(
            flow_state=flow_state,
            key=f"flow_{current_agent.id}",
            height=600,
            layout=LayeredLayout(direction='down', node_node_spacing=150, node_layer_spacing=150),
            get_node_on_click=True,
            show_minimap=True,
            show_controls=True,
            allow_new_edges=True,
            animate_new_edges=True,
            style={"backgroundColor": "#f8f9fa", "border": "1px solid #dee2e6"}
        )
        
        # Handle node selection
        if result and "node_id" in result:
            st.session_state.selected_node = result["node_id"]
            st.rerun()
        
    # Show connection manager below canvas
    render_node_connections(current_agent)
    
    # Display node information if selected
    if hasattr(st.session_state, "selected_node") and st.session_state.selected_node:
        display_selected_node_info(current_agent)
    
    # Add a button to save the agent
    if st.button("Save Agent", key=f"save_agent_{current_agent.id}"):
        if st.session_state.agent_manager.save_agent(current_agent.id):
            st.success("Agent saved successfully!")
        else:
            st.error("Failed to save agent!")

def create_node_selector(current_agent):
    """Create a UI for adding new nodes to the agent"""
    # Group node types by category
    node_categories = {}
    for node_type, node_def in NODE_TYPES.items():
        category = node_def.category
        if category not in node_categories:
            node_categories[category] = []
        node_categories[category].append((node_type, node_def))
    
    # Create tabs for each category
    tabs = st.tabs(list(node_categories.keys()))
    
    for i, (category, node_types) in enumerate(node_categories.items()):
        with tabs[i]:
            cols = st.columns(len(node_types))
            for j, (node_type, node_def) in enumerate(node_types):
                with cols[j]:
                    if st.button(f"{node_def.name}", key=f"add_{node_type}"):
                        # Create a new node at a default position
                        node = st.session_state.agent_manager.create_node(
                            current_agent.id,
                            node_type,
                            node_def.name,
                            {"x": 100 + (len(current_agent.nodes) * 50), "y": 100 + (len(current_agent.nodes) * 50)}
                        )
                        st.rerun()

def display_selected_node_info(current_agent):
    """Display information about the currently selected node"""
    if not st.session_state.selected_node:
        st.info("Select a node to see its details")
        return
    
    selected_node = next((node for node in current_agent.nodes if node.id == st.session_state.selected_node), None)
    if not selected_node:
        st.session_state.selected_node = None
        st.info("Select a node to see its details")
        return
    
    # Display node information
    st.subheader(f"{selected_node.name}")
    st.caption(f"Type: {selected_node.type}")
    
    with st.expander("Node Details", expanded=True):
        if selected_node.inputs:
            st.markdown("**Inputs:**")
            for input_item in selected_node.inputs:
                st.markdown(f"- {input_item.name} ({input_item.data_type})")
        
        if selected_node.outputs:
            st.markdown("**Outputs:**")
            for output_item in selected_node.outputs:
                st.markdown(f"- {output_item.name} ({output_item.data_type})")
        
        # Display configuration
        st.markdown("**Configuration:**")
        st.json(selected_node.config)
    
    # Configuration button
    if st.button("Configure Node", key=f"configure_{selected_node.id}"):
        st.session_state.selected_node_for_config = selected_node.id
        
    # Delete button
    if st.button("Delete Node", key=f"delete_{selected_node.id}"):
        if st.session_state.agent_manager.delete_node(current_agent.id, selected_node.id):
            st.session_state.selected_node = None
            st.success(f"Node '{selected_node.name}' deleted")
            st.rerun()
        else:
            st.error("Failed to delete node!")

def get_flow_state(agent):
    """Convert agent model to flow state"""
    # Create StreamlitFlowNode instances for each node
    flow_nodes = []
    for node in agent.nodes:
        # Get style for this node type
        style = NODE_STYLES.get(node.type, {})
        
        # Create a readable label for the node data
        details = ""
        if node.type == NodeType.LLM:
            provider = node.config.get('provider', 'unknown')
            model = node.config.get('model', 'unknown')
            details += f"Provider: {provider}\n"
            details += f"Model: {model}"
            
            # Add provider-specific styling for LLM nodes
            if provider == "openai":
                style["borderTop"] = "4px solid #10a37f"  # OpenAI green
            elif provider == "anthropic":
                style["borderTop"] = "4px solid #b83280"  # Anthropic purple
                
        elif node.type == NodeType.API:
            url = node.config.get('url', '')
            method = node.config.get('method', 'GET')
            details += f"URL: {url}\n"
            details += f"Method: {method}"
            
            # Add method-specific styling for API nodes
            if method == "GET":
                style["borderTop"] = "4px solid #3182ce"  # Blue for GET
            elif method == "POST":
                style["borderTop"] = "4px solid #38a169"  # Green for POST
            elif method == "PUT":
                style["borderTop"] = "4px solid #d69e2e"  # Yellow for PUT
            elif method == "DELETE":
                style["borderTop"] = "4px solid #e53e3e"  # Red for DELETE
        
        # Create StreamlitFlowNode instance
        flow_node = StreamlitFlowNode(
            id=node.id,
            pos=(node.position.x, node.position.y),
            data={
                'label': node.name,
                'details': details
            },
            node_type=node.type,
            style=style,
            # Set source/target positions based on node type
            source_position='bottom' if node.type != NodeType.OUTPUT else 'right',
            target_position='top' if node.type != NodeType.INPUT else 'left'
        )
        flow_nodes.append(flow_node)
    
    # Create StreamlitFlowEdge instances for each edge
    flow_edges = []
    for edge in agent.edges:
        # Find nodes to get proper display info
        source_node = next((node for node in agent.nodes if node.id == edge.source_node_id), None)
        target_node = next((node for node in agent.nodes if node.id == edge.target_node_id), None)
        
        if source_node and target_node:
            # Find connection details
            source_output = next((output for output in source_node.outputs if output.id == edge.source_output_id), None)
            target_input = next((input_item for input_item in target_node.inputs if input_item.id == edge.target_input_id), None)
            
            if source_output and target_input:
                label = f"{source_output.name} → {target_input.name}"
                
                # Determine edge type and style based on source/target node types
                edge_type = 'default'
                edge_style = {}
                if source_node.type == NodeType.LLM or target_node.type == NodeType.LLM:
                    edge_style = {"stroke": "#9C27B0", "strokeWidth": 2}
                elif source_node.type == NodeType.API or target_node.type == NodeType.API:
                    edge_style = {"stroke": "#FF5722", "strokeWidth": 2}
                
                # Create StreamlitFlowEdge instance
                flow_edge = StreamlitFlowEdge(
                    id=edge.id,
                    source=edge.source_node_id,
                    target=edge.target_node_id,
                    edge_type=edge_type,
                    label=label,
                    animated=True,
                    style=edge_style,
                    label_style={"fontSize": "10px", "fill": "#6c757d"},
                    label_show_bg=True
                )
                flow_edges.append(flow_edge)
    
    # Create a StreamlitFlowState instance
    flow_state = StreamlitFlowState(
        nodes=flow_nodes,
        edges=flow_edges
    )
    
    return flow_state

def render_node_connections(current_agent):
    """Render the UI for managing node connections"""
    st.subheader("Node Connections")
    
    with st.form("create_connection"):
        st.markdown("Connect node outputs to inputs")
        
        # Source node/output selection
        st.markdown("**Source**")
        source_cols = st.columns(2)
        with source_cols[0]:
            source_node_options = [(node.id, node.name) for node in current_agent.nodes if node.outputs]
            source_node = st.selectbox(
                "Source Node", 
                options=[id for id, _ in source_node_options],
                format_func=lambda x: next((name for id, name in source_node_options if id == x), x),
                key="source_node"
            )
        
        with source_cols[1]:
            source_node_obj = next((node for node in current_agent.nodes if node.id == source_node), None)
            source_output_options = [(output.id, output.name) for output in source_node_obj.outputs] if source_node_obj else []
            source_output = st.selectbox(
                "Source Output", 
                options=[id for id, _ in source_output_options],
                format_func=lambda x: next((name for id, name in source_output_options if id == x), x),
                key="source_output"
            )
        
        # Target node/input selection
        st.markdown("**Target**")
        target_cols = st.columns(2)
        with target_cols[0]:
            target_node_options = [(node.id, node.name) for node in current_agent.nodes if node.inputs]
            target_node = st.selectbox(
                "Target Node", 
                options=[id for id, _ in target_node_options],
                format_func=lambda x: next((name for id, name in target_node_options if id == x), x),
                key="target_node"
            )
        
        with target_cols[1]:
            target_node_obj = next((node for node in current_agent.nodes if node.id == target_node), None)
            target_input_options = [(input_item.id, input_item.name) for input_item in target_node_obj.inputs] if target_node_obj else []
            target_input = st.selectbox(
                "Target Input", 
                options=[id for id, _ in target_input_options],
                format_func=lambda x: next((name for id, name in target_input_options if id == x), x),
                key="target_input"
            )
        
        # Create connection button
        if st.form_submit_button("Create Connection"):
            if source_node and source_output and target_node and target_input:
                edge = st.session_state.agent_manager.create_edge(
                    current_agent.id,
                    source_node,
                    source_output,
                    target_node,
                    target_input
                )
                if edge:
                    st.success("Connection created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create connection. Check your selections.")
    
    # Display existing connections
    if current_agent.edges:
        st.subheader("Existing Connections")
        for edge in current_agent.edges:
            # Find source and target node names
            source_node = next((node for node in current_agent.nodes if node.id == edge.source_node_id), None)
            target_node = next((node for node in current_agent.nodes if node.id == edge.target_node_id), None)
            
            if source_node and target_node:
                # Find source output and target input names
                source_output = next((output for output in source_node.outputs if output.id == edge.source_output_id), None)
                target_input = next((input_item for input_item in target_node.inputs if input_item.id == edge.target_input_id), None)
                
                if source_output and target_input:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"{source_node.name}.{source_output.name} → {target_node.name}.{target_input.name}")
                    with col3:
                        if st.button("🗑️", key=f"delete_edge_{edge.id}"):
                            if st.session_state.agent_manager.delete_edge(current_agent.id, edge.id):
                                st.rerun()