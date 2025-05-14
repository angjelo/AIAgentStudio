import streamlit as st
import json
from typing import Dict, Any

from src.services.engine import AgentEngine

def render_test_panel():
    """Render the test panel for executing the current agent"""
    if not st.session_state.get("show_test_panel", False):
        return
    
    st.header("Test Agent")
    
    if not st.session_state.current_agent:
        st.error("No agent selected")
        return
    
    current_agent = st.session_state.agent_manager.get_agent(st.session_state.current_agent)
    if not current_agent:
        st.error("Selected agent not found")
        return
    
    # Display agent information
    st.subheader(f"Testing: {current_agent.name}")
    if current_agent.description:
        st.markdown(current_agent.description)
    
    # Identify input nodes
    input_nodes = [node for node in current_agent.nodes if node.type == "input"]
    
    if not input_nodes:
        st.warning("This agent has no input nodes. Add input nodes to test the agent.")
        return
    
    # Create input fields for each input node
    st.markdown("### Inputs")
    input_values = {}
    
    for input_node in input_nodes:
        input_type = input_node.config.get("input_type", "text")
        label = input_node.config.get("label", input_node.name)
        placeholder = input_node.config.get("placeholder", "")
        default_value = input_node.config.get("default_value", "")
        
        if input_type == "text":
            input_values[input_node.id] = st.text_area(
                label, 
                value=default_value,
                placeholder=placeholder,
                key=f"input_{input_node.id}"
            )
        elif input_type == "number":
            input_values[input_node.id] = st.number_input(
                label,
                value=float(default_value) if default_value else 0.0,
                key=f"input_{input_node.id}"
            )
        elif input_type == "boolean":
            input_values[input_node.id] = st.checkbox(
                label,
                value=default_value.lower() == "true" if isinstance(default_value, str) else bool(default_value),
                key=f"input_{input_node.id}"
            )
        elif input_type == "select":
            options = input_node.config.get("options", [])
            if options:
                selected_index = 0
                if default_value in options:
                    selected_index = options.index(default_value)
                
                input_values[input_node.id] = st.selectbox(
                    label,
                    options=options,
                    index=selected_index,
                    key=f"input_{input_node.id}"
                )
            else:
                st.warning(f"No options defined for select input: {label}")
                input_values[input_node.id] = ""
        elif input_type == "file":
            uploaded_file = st.file_uploader(
                label,
                key=f"input_{input_node.id}"
            )
            if uploaded_file is not None:
                input_values[input_node.id] = uploaded_file.getvalue()
            else:
                input_values[input_node.id] = None
    
    # Execute button
    if st.button("Execute Agent", key="execute_agent"):
        with st.spinner("Executing agent..."):
            try:
                # Format input data for engine
                engine_inputs = {}
                for node_id, value in input_values.items():
                    engine_inputs[node_id] = value
                
                # Initialize engine
                engine = AgentEngine()
                
                # Execute agent
                results = engine.execute_agent(current_agent, engine_inputs)
                
                # Display results
                st.markdown("### Results")
                
                if not results:
                    st.warning("No results returned")
                else:
                    for output_key, output_value in results.items():
                        st.subheader(output_key)
                        
                        # Handle different output types
                        if isinstance(output_value, dict):
                            if "error" in output_value:
                                st.error(output_value["error"])
                            else:
                                st.json(output_value)
                        elif isinstance(output_value, list):
                            if all(isinstance(item, dict) for item in output_value):
                                st.dataframe(output_value)
                            else:
                                st.json(output_value)
                        elif isinstance(output_value, str):
                            st.markdown(output_value)
                        else:
                            st.write(output_value)
                
                # Also display raw results
                with st.expander("Raw Results"):
                    st.json(results)
                
            except Exception as e:
                st.error(f"Error executing agent: {str(e)}")
                st.exception(e)
    
    # Close button
    if st.button("Close", key="close_test_panel"):
        st.session_state.show_test_panel = False
        st.rerun()