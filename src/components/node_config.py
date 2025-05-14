import streamlit as st
import json
from typing import Dict, Any, List, Optional

from src.models.node import Node
from src.models.node_types import NODE_TYPES, NodeType

def render_node_config():
    """Render the configuration panel for the selected node"""
    st.header("Node Configuration")
    
    if not st.session_state.current_agent or not st.session_state.selected_node:
        st.info("Select a node to configure")
        return
    
    # Get the current agent and selected node
    current_agent = st.session_state.agent_manager.get_agent(st.session_state.current_agent)
    if not current_agent:
        st.error("Selected agent not found")
        return
    
    selected_node = next((node for node in current_agent.nodes if node.id == st.session_state.selected_node), None)
    if not selected_node:
        st.session_state.selected_node = None
        st.info("Select a node to configure")
        return
    
    # Get node type definition
    node_type_def = NODE_TYPES.get(selected_node.type)
    if not node_type_def:
        st.error(f"Unknown node type: {selected_node.type}")
        return
    
    st.subheader(f"{selected_node.name} ({node_type_def.name})")
    
    # Basic node configuration
    with st.form("node_config_form"):
        node_name = st.text_input("Node Name", value=selected_node.name)
        node_description = st.text_area("Description", value=selected_node.description or "")
        
        # Node type specific configuration
        st.markdown("#### Configuration")
        
        updated_config = {}
        
        if selected_node.type == NodeType.INPUT:
            input_type = st.selectbox(
                "Input Type",
                options=["text", "number", "boolean", "select", "file"],
                index=["text", "number", "boolean", "select", "file"].index(selected_node.config.get("input_type", "text"))
            )
            updated_config["input_type"] = input_type
            
            updated_config["label"] = st.text_input("Label", value=selected_node.config.get("label", "Input"))
            updated_config["placeholder"] = st.text_input("Placeholder", value=selected_node.config.get("placeholder", ""))
            updated_config["default_value"] = st.text_input("Default Value", value=selected_node.config.get("default_value", ""))
            
            if input_type == "select":
                options_str = st.text_area(
                    "Options (one per line)", 
                    value="\n".join(selected_node.config.get("options", []))
                )
                updated_config["options"] = [opt.strip() for opt in options_str.split("\n") if opt.strip()]
        
        elif selected_node.type == NodeType.OUTPUT:
            output_type = st.selectbox(
                "Output Type",
                options=["text", "json", "table", "chart"],
                index=["text", "json", "table", "chart"].index(selected_node.config.get("output_type", "text"))
            )
            updated_config["output_type"] = output_type
            
            updated_config["label"] = st.text_input("Label", value=selected_node.config.get("label", "Output"))
        
        elif selected_node.type == NodeType.LLM:
            provider = st.selectbox(
                "Provider",
                options=["openai", "anthropic"],
                index=["openai", "anthropic"].index(selected_node.config.get("provider", "openai"))
            )
            updated_config["provider"] = provider
            
            if provider == "openai":
                model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
            else:  # anthropic
                model_options = ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
            
            current_model = selected_node.config.get("model")
            model_index = 0
            if current_model in model_options:
                model_index = model_options.index(current_model)
            
            updated_config["model"] = st.selectbox("Model", options=model_options, index=model_index)
            updated_config["temperature"] = st.slider("Temperature", min_value=0.0, max_value=1.0, value=float(selected_node.config.get("temperature", 0.7)), step=0.1)
            updated_config["max_tokens"] = st.number_input("Max Tokens", min_value=1, max_value=10000, value=int(selected_node.config.get("max_tokens", 1000)))
        
        elif selected_node.type == NodeType.API:
            updated_config["url"] = st.text_input("URL", value=selected_node.config.get("url", ""))
            
            method = st.selectbox(
                "Method",
                options=["GET", "POST", "PUT", "DELETE", "PATCH"],
                index=["GET", "POST", "PUT", "DELETE", "PATCH"].index(selected_node.config.get("method", "GET"))
            )
            updated_config["method"] = method
            
            updated_config["timeout"] = st.number_input("Timeout (seconds)", min_value=1, max_value=300, value=int(selected_node.config.get("timeout", 30)))
            
            headers_str = st.text_area(
                "Default Headers (JSON)", 
                value=json.dumps(selected_node.config.get("default_headers", {}), indent=2)
            )
            try:
                updated_config["default_headers"] = json.loads(headers_str)
            except json.JSONDecodeError:
                st.error("Invalid JSON for headers")
        
        elif selected_node.type == NodeType.TRANSFORM:
            transform_type = st.selectbox(
                "Transform Type",
                options=["jq", "regex", "template"],
                index=["jq", "regex", "template"].index(selected_node.config.get("transform_type", "jq"))
            )
            updated_config["transform_type"] = transform_type
            
            if transform_type == "jq":
                updated_config["expression"] = st.text_input("JQ Expression", value=selected_node.config.get("expression", "."))
            elif transform_type == "regex":
                updated_config["expression"] = st.text_input("Regex Pattern", value=selected_node.config.get("expression", ""))
            elif transform_type == "template":
                updated_config["expression"] = st.text_area("Template", value=selected_node.config.get("expression", ""))
        
        elif selected_node.type == NodeType.CONDITION:
            condition_type = st.selectbox(
                "Condition Type",
                options=["expression", "comparison"],
                index=["expression", "comparison"].index(selected_node.config.get("condition_type", "expression"))
            )
            updated_config["condition_type"] = condition_type
            
            if condition_type == "expression":
                updated_config["expression"] = st.text_input("Expression", value=selected_node.config.get("expression", "data != null"))
            elif condition_type == "comparison":
                updated_config["left"] = st.text_input("Left Value", value=selected_node.config.get("left", ""))
                updated_config["operator"] = st.selectbox(
                    "Operator",
                    options=["==", "!=", ">", "<", ">=", "<=", "contains", "starts_with", "ends_with"],
                    index=["==", "!=", ">", "<", ">=", "<=", "contains", "starts_with", "ends_with"].index(selected_node.config.get("operator", "=="))
                )
                updated_config["right"] = st.text_input("Right Value", value=selected_node.config.get("right", ""))
        
        elif selected_node.type == NodeType.LOOP:
            loop_type = st.selectbox(
                "Loop Type",
                options=["for_each", "while"],
                index=["for_each", "while"].index(selected_node.config.get("loop_type", "for_each"))
            )
            updated_config["loop_type"] = loop_type
            
            if loop_type == "while":
                updated_config["condition"] = st.text_input("Condition", value=selected_node.config.get("condition", ""))
            
            updated_config["collect_results"] = st.checkbox("Collect Results", value=selected_node.config.get("collect_results", True))
        
        # Submit button
        if st.form_submit_button("Update Node"):
            # Update node with new configuration
            updates = {
                "name": node_name,
                "description": node_description,
                "config": updated_config
            }
            
            updated_node = st.session_state.agent_manager.update_node(
                st.session_state.current_agent,
                st.session_state.selected_node,
                updates
            )
            
            if updated_node:
                st.success("Node updated successfully!")
            else:
                st.error("Failed to update node")
    
    # Display node details
    with st.expander("Node Details"):
        st.json(selected_node.to_dict())
    
    # Action to deselect the node
    if st.button("Done"):
        st.session_state.selected_node = None
        st.rerun()