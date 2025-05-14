import streamlit as st
import uuid
from datetime import datetime

from src.models.node import Agent

def render_sidebar():
    """Render the sidebar for agent management"""
    st.header("Agent Management")
    
    # New agent form
    with st.form("new_agent_form"):
        st.subheader("Create New Agent")
        agent_name = st.text_input("Agent Name", placeholder="My AI Agent")
        agent_description = st.text_area("Description", placeholder="Describe what your agent does")
        
        submit_button = st.form_submit_button("Create Agent")
        
        if submit_button and agent_name:
            # Create a new agent
            new_agent = Agent(
                name=agent_name,
                description=agent_description,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Add to session state
            st.session_state.agent_manager.agents[new_agent.id] = new_agent
            st.session_state.current_agent = new_agent.id
            
            st.success(f"Created agent: {agent_name}")
    
    # Display existing agents
    st.subheader("Your Agents")
    agents = st.session_state.agent_manager.get_all_agents()
    
    if not agents:
        st.info("No agents created yet. Create your first agent above.")
    else:
        for agent in agents:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.button(f"{agent.name}", key=f"select_{agent.id}"):
                    st.session_state.current_agent = agent.id
                    st.session_state.selected_node = None
            
            with col2:
                if st.button("🗑️", key=f"delete_{agent.id}"):
                    st.session_state.agent_manager.delete_agent(agent.id)
                    if st.session_state.current_agent == agent.id:
                        st.session_state.current_agent = None
                        st.session_state.selected_node = None
                    st.rerun()
    
    # Display tools for the current agent
    if st.session_state.current_agent:
        current_agent = st.session_state.agent_manager.get_agent(st.session_state.current_agent)
        if current_agent:
            st.subheader(f"Agent: {current_agent.name}")
            
            # Save button
            if st.button("Save Agent"):
                st.session_state.agent_manager.save_agent(current_agent.id)
                st.success("Agent saved successfully!")
            
            # Test button
            if st.button("Test Agent"):
                st.session_state.show_test_panel = True
            
            # Export button
            if st.button("Export Agent"):
                # TODO: Implement export functionality
                pass