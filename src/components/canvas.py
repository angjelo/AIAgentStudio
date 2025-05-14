import streamlit as st
import uuid
import json
from typing import Dict, Any, List, Optional
from streamlit_elements import elements, dashboard, mui, html

from src.models.node import Node, Edge, Position
from src.models.node_types import NODE_TYPES, NodeType

# Style constants
NODE_WIDTH = 250
NODE_HEIGHT = 150
NODE_STYLE = {
    "padding": "10px",
    "borderRadius": "8px",
    "background": "#f5f5f5",
    "boxShadow": "0px 2px 10px rgba(0,0,0,0.1)"
}

def render_canvas():
    """Render the main canvas for node editing"""
    st.header("Agent Canvas")
    
    if not st.session_state.current_agent:
        st.info("Select or create an agent to start building")
        return
    
    current_agent = st.session_state.agent_manager.get_agent(st.session_state.current_agent)
    if not current_agent:
        st.error("Selected agent not found")
        return
    
    # Add new node section
    st.subheader("Add Node")
    node_cols = st.columns(4)
    
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
    
    # Render canvas with nodes using streamlit-elements
    with elements("canvas"):
        # Create a dashboard layout
        with dashboard.Grid(draggableHandle=".draggable"):
            # Render each node
            for i, node in enumerate(current_agent.nodes):
                node_key = f"node_{node.id}"
                node_type_def = NODE_TYPES.get(node.type)
                
                # Node position and size
                layout = {
                    "i": node_key,
                    "x": int(node.position.x / 50),  # Scale to grid
                    "y": int(node.position.y / 50),  # Scale to grid
                    "w": 5,  # Width in grid units
                    "h": 3,  # Height in grid units
                }
                
                with dashboard.Item(key=node_key, **layout):
                    # Node card
                    with mui.Card(sx={"height": "100%"}):
                        # Node header
                        with mui.CardHeader(
                            title=node.name,
                            className="draggable",
                            sx={"cursor": "move", "backgroundColor": node_type_def.color if node_type_def else "#ccc", "color": "white"}
                        ):
                            pass
                        
                        # Node content
                        with mui.CardContent():
                            # Display node inputs
                            if node.inputs:
                                mui.Typography("Inputs:", variant="subtitle2")
                                for input_item in node.inputs:
                                    mui.Chip(label=input_item.name, size="small", sx={"margin": "2px"})
                            
                            # Display node outputs
                            if node.outputs:
                                mui.Typography("Outputs:", variant="subtitle2", sx={"marginTop": "8px"})
                                for output_item in node.outputs:
                                    mui.Chip(label=output_item.name, size="small", sx={"margin": "2px"})
                        
                        # Node actions
                        with mui.CardActions():
                            # Configure button
                            with mui.Button("Configure", size="small", onClick=on_click_configure_node(node.id)):
                                pass
                            
                            # Delete button
                            with mui.Button("Delete", size="small", color="error", onClick=on_click_delete_node(node.id)):
                                pass
    
    # Node connections section - simplified version
    if current_agent.nodes:
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

# Event handlers for node interactions
def on_click_configure_node(node_id):
    """Handler for configure node button"""
    def handle_click(event):
        # Update selected node in session state
        st.session_state.selected_node = node_id
        # Force a rerun to update the UI
        st.rerun()
    return handle_click

def on_click_delete_node(node_id):
    """Handler for delete node button"""
    def handle_click(event):
        # Delete the node
        current_agent_id = st.session_state.current_agent
        if current_agent_id:
            st.session_state.agent_manager.delete_node(current_agent_id, node_id)
            if st.session_state.selected_node == node_id:
                st.session_state.selected_node = None
            # Force a rerun to update the UI
            st.rerun()
    return handle_click