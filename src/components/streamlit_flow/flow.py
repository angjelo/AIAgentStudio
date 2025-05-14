import streamlit as st
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import json
import uuid
from datetime import datetime

from .state import StreamlitFlowState
from .elements import StreamlitFlowNode, StreamlitFlowEdge
from .layouts import Layout, ManualLayout

def streamlit_flow(
    flow_state: StreamlitFlowState,
    key: str,
    height: int = 500,
    show_controls: bool = True,
    show_minimap: bool = False,

    style: Dict[str, Any] = None,
    layout: Layout = None,
    get_node_on_click: bool = False,
    get_edge_on_click: bool = False,

    hide_watermark: bool = False
):
    """
    Render a flow diagram using pure Streamlit HTML/CSS/JS
    
    Parameters:
    -----------
    key : str
        Unique key for this component
    state : StreamlitFlowState
        The state of the flow diagram
    height : int
        Height of the canvas in pixels
    fit_view : bool
        Whether to automatically fit the view to show all nodes
    show_controls : bool
        Whether to show the controls panel
    show_minimap : bool
        Whether to show the minimap
    allow_new_edges : bool
        Whether to allow creating new edges
    animate_new_edges : bool
        Whether to animate newly created edges
    style : Dict[str, Any]
        Custom CSS styles for the canvas
    layout : Layout
        Layout algorithm to use
    get_node_on_click : bool
        Whether to return the node ID when a node is clicked
    get_edge_on_click : bool
        Whether to return the edge ID when an edge is clicked
    pan_on_drag : bool
        Whether to pan the canvas when dragging
    allow_zoom : bool
        Whether to allow zooming
    min_zoom : float
        Minimum zoom level
    enable_pane_menu : bool
        Whether to enable the pane context menu
    enable_node_menu : bool
        Whether to enable the node context menu
    enable_edge_menu : bool
        Whether to enable the edge context menu
    hide_watermark : bool
        Whether to hide the React Flow watermark
    
    Returns:
    --------
    Dict or None
        Returns None if no interaction occurred, or a dictionary with interaction details
    """
    # Initialize state in session state if not already present
    if f"{key}_state" not in st.session_state:
        st.session_state[f"{key}_state"] = flow_state

    # Get the current state
    state = st.session_state[f"{key}_state"]
    
    # Apply layout if provided
    if layout:
        # Convert state nodes to dict format for layout algorithm
        layout_nodes = [node.to_dict() for node in state.nodes]
        layout_edges = [edge.to_dict() for edge in state.edges]
        
        # Apply layout
        updated_nodes = layout.apply(layout_nodes, layout_edges)
        
        # Update node positions in state
        for updated_node in updated_nodes:
            for i, node in enumerate(state.nodes):
                if node.id == updated_node['id']:
                    state.nodes[i].pos = updated_node['pos']
    
    # Default style settings
    default_style = {
        "backgroundColor": "#f8f9fa"
    }
    
    # Merge with custom style
    canvas_style = {**default_style, **(style or {})}
    canvas_style_str = "; ".join([f"{k}: {v}" for k, v in canvas_style.items()])
    
    # Create container for the flow diagram
    flow_container = st.container()
    
    # Create a map of node IDs to nodes for easy lookup
    nodes_map = {node.id: node.to_dict() for node in state.nodes}
    
    # Prepare JavaScript for interaction
    js_code = """
    <script>
    function handleNodeClick(nodeId) {
        // Using Streamlit's setComponentValue to update the selected node
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: {nodeId: nodeId, type: 'node'},
            dataType: 'json'
        }, '*');
    }
    
    function handleEdgeClick(edgeId) {
        // Using Streamlit's setComponentValue for edge clicks
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: {edgeId: edgeId, type: 'edge'},
            dataType: 'json'
        }, '*');
    }
    
    // Animation keyframes
    document.head.insertAdjacentHTML('beforeend', `
        <style>
            @keyframes flowDash {
                to {
                    stroke-dashoffset: -10;
                }
            }
        </style>
    `);
    </script>
    """
    
    # Render nodes
    def render_node(node):
        node_id = node.id
        pos = node.pos
        data = node.data
        node_type = node.node_type
        
        # Determine style based on node type
        if node_type == 'input':
            header_bg = "#4CAF50"
            header_text = "white"
        elif node_type == 'output':
            header_bg = "#2196F3"
            header_text = "white"
        elif node_type == 'llm':
            header_bg = "#9C27B0"
            header_text = "white"
        elif node_type == 'api':
            header_bg = "#FF5722"
            header_text = "white"
        else:
            header_bg = "#6c757d"
            header_text = "white"
        
        # Override with custom style if provided
        if node.style:
            if 'backgroundColor' in node.style:
                header_bg = node.style['backgroundColor']
            if 'color' in node.style:
                header_text = node.style['color']
        
        # Node style
        node_style = f"""
            position: absolute;
            left: {pos[0]}px;
            top: {pos[1]}px;
            width: 180px;
            background-color: white;
            border-radius: 5px;
            border: 1px solid #dee2e6;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            z-index: 1;
            cursor: pointer;
            user-select: none;
        """
        
        # Get label from data
        label = data.get('content', data.get('label', 'Node'))
        details = data.get('details', '')
        
        # Create HTML for node
        html = f"""
        <div class="node" id="node-{node_id}" style="{node_style}" onclick="handleNodeClick('{node_id}')">
            <div style="background-color: {header_bg}; color: {header_text}; 
                        padding: 8px; border-radius: 5px 5px 0 0; font-weight: 500;">
                {label}
            </div>
            <div style="padding: 8px; font-size: 0.85rem;">
                {details}
            </div>
        </div>
        """
        return html
    
    # Render edges
    def render_edge(edge):
        edge_id = edge.id
        source_id = edge.source
        target_id = edge.target
        edge_type = edge.edge_type
        label = edge.label
        animated = edge.animated
        
        # Get source and target positions
        if source_id not in nodes_map or target_id not in nodes_map:
            return ""
        
        source = nodes_map[source_id]
        target = nodes_map[target_id]
        
        # Calculate edge points
        source_pos = source.get('pos', (0, 0))
        target_pos = target.get('pos', (0, 0))
        
        # Adjust connection points based on source/target positions
        source_x = source_pos[0] + 90  # center of source
        source_y = source_pos[1] + 50  # bottom of source
        target_x = target_pos[0] + 90  # center of target
        target_y = target_pos[1]       # top of target
        
        # Adjust for edge type
        if edge_type == 'straight':
            # Straight line with arrow
            path = f"M {source_x} {source_y} L {target_x} {target_y}"
        elif edge_type == 'step':
            # Step line with horizontal then vertical segments
            mid_y = (source_y + target_y) / 2
            path = f"M {source_x} {source_y} L {source_x} {mid_y} L {target_x} {mid_y} L {target_x} {target_y}"
        elif edge_type == 'smoothstep':
            # Smoothed step line
            mid_y = (source_y + target_y) / 2
            path = f"M {source_x} {source_y} C {source_x} {mid_y}, {target_x} {mid_y}, {target_x} {target_y}"
        else:  # default or simplebezier
            # Bezier curve
            control_x1 = source_x
            control_y1 = source_y + 50
            control_x2 = target_x
            control_y2 = target_y - 50
            path = f"M {source_x} {source_y} C {control_x1} {control_y1}, {control_x2} {control_y2}, {target_x} {target_y}"
        
        # Calculate midpoint for label
        mid_x = (source_x + target_x) / 2
        mid_y = (source_y + target_y) / 2
        
        # Edge animation
        animation = "stroke-dasharray: 5; animation: flowDash 0.5s linear infinite;" if animated else ""
        
        # Edge HTML
        edge_html = f"""
        <svg width="100%" height="100%" style="position: absolute; top: 0; left: 0; z-index: 0; pointer-events: none;">
            <path id="edge-{edge_id}" 
                  d="{path}"
                  stroke="#6c757d" stroke-width="2" fill="none" style="{animation}"
                  onclick="handleEdgeClick('{edge_id}')" />
            
            <!-- Arrow marker -->
            <polygon points="{target_x-5},{target_y} {target_x},{target_y-5} {target_x+5},{target_y}"
                     fill="#6c757d" />
        """
        
        # Add label if provided
        if label:
            # Background for label
            if edge.label_show_bg:
                edge_html += f"""
                <rect x="{mid_x-40}" y="{mid_y-10}" width="80" height="20" rx="5" 
                      fill="white" stroke="#dee2e6" />
                """
            
            # Label text
            label_style = ""
            if edge.label_style:
                label_style = "; ".join([f"{k}: {v}" for k, v in edge.label_style.items()])
            
            edge_html += f"""
            <text x="{mid_x}" y="{mid_y+5}" text-anchor="middle" font-size="10" style="{label_style}">
                {label}
            </text>
            """
        
        edge_html += "</svg>"
        return edge_html
    
    # Build HTML content
    nodes_html = "".join([render_node(node) for node in state.nodes])
    edges_html = "".join([render_edge(edge) for edge in state.edges])
    
    # Render the flow diagram
    with flow_container:
        st.markdown(f"""
        <div style="position: relative; height: {height}px; border: 1px solid #dee2e6; 
                    {canvas_style_str}; overflow: hidden; border-radius: 5px;">
            
            <!-- Canvas background with grid -->
            <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
                        background-image: 
                            linear-gradient(#dee2e6 1px, transparent 1px),
                            linear-gradient(90deg, #dee2e6 1px, transparent 1px);
                        background-size: 20px 20px;">
            </div>
            
            <!-- Edge layer -->
            <div id="edges">
                {edges_html}
            </div>
            
            <!-- Nodes layer -->
            <div id="nodes">
                {nodes_html}
            </div>
            
            {js_code}
        """, unsafe_allow_html=True)
        
        # Add minimap if enabled
        if show_minimap:
            # Generate minimap nodes HTML
            minimap_nodes_html = ""
            for node in state.nodes:
                node_dict = node.to_dict()
                pos = node_dict['pos']
                
                # Determine color based on node type
                if node.node_type == 'input':
                    color = "#4CAF50"
                elif node.node_type == 'output':
                    color = "#2196F3"
                elif node.node_type == 'llm':
                    color = "#9C27B0"
                elif node.node_type == 'api':
                    color = "#FF5722"
                else:
                    color = "#6c757d"
                
                # Override with custom style if provided
                if node.style and 'backgroundColor' in node.style:
                    color = node.style['backgroundColor']
                
                # Calculate scaled position for minimap
                left_pos = (pos[0] / 5) + 5
                top_pos = (pos[1] / 5) + 20
                
                minimap_nodes_html += f"""
                <div style="
                    position: absolute;
                    width: 10px;
                    height: 10px;
                    background-color: {color};
                    border-radius: 2px;
                    left: {left_pos}px;
                    top: {top_pos}px;
                "></div>
                """
            
            st.markdown(f"""
            <div style="
                position: absolute;
                bottom: 10px;
                right: 10px;
                width: 150px;
                height: 100px;
                border: 1px solid #dee2e6;
                background-color: rgba(255,255,255,0.8);
                border-radius: 5px;
                padding: 5px;
                z-index: 10;
            ">
                <div style="font-size: 10px; font-weight: bold; margin-bottom: 5px;">Minimap</div>
                {minimap_nodes_html}
            </div>
            """, unsafe_allow_html=True)
        
        # Add controls if enabled
        if show_controls:
            st.markdown("""
            <div style="
                position: absolute;
                top: 10px;
                right: 10px;
                background-color: rgba(255,255,255,0.8);
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 5px;
                z-index: 10;
            ">
                <div style="display: flex; flex-direction: column; gap: 5px;">
                    <button style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 3px; 
                                   padding: 2px 5px; cursor: pointer; font-size: 12px;">+</button>
                    <button style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 3px; 
                                   padding: 2px 5px; cursor: pointer; font-size: 12px;">−</button>
                    <button style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 3px; 
                                   padding: 2px 5px; cursor: pointer; font-size: 12px;">⟲</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if not hide_watermark:
            st.markdown("""
            <div style="position: absolute; bottom: 10px; left: 10px; font-size: 10px; color: #adb5bd;">
                Powered by Streamlit Flow
            </div>
            """, unsafe_allow_html=True)
        
        # Close the main container
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Handle interaction events
    if get_node_on_click or get_edge_on_click:
        # Check for interaction events
        interaction = st.session_state.get(f"{key}")
        
        if interaction:
            # Check node clicks
            if get_node_on_click and 'nodeId' in interaction and interaction.get('type') == 'node':
                state.selected_id = interaction['nodeId']
                return {"node_id": interaction['nodeId']}
            
            # Check edge clicks
            if get_edge_on_click and 'edgeId' in interaction and interaction.get('type') == 'edge':
                return {"edge_id": interaction['edgeId']}
    
    return None