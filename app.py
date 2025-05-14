import streamlit as st
import sys
from src.components.sidebar import render_sidebar
from src.components.custom_canvas import render_canvas
from src.components.node_config import render_node_config
from src.components.test_panel import render_test_panel
from src.services.agent_manager import AgentManager
from src.utils.config import load_config
from src.utils.logger import setup_logger

# Only run setup operations when script is run directly via streamlit
if __name__ == "__main__" or 'streamlit' in sys.modules:
    # Set up logging
    logger = setup_logger()
    
    # Load configuration
    config = load_config()
    
    # Set page config
    st.set_page_config(page_title="AI Agent Studio", layout="wide")
    
    # Initialize session state
    if "agent_manager" not in st.session_state:
        st.session_state.agent_manager = AgentManager(config["app"]["save_dir"])
    
    if "selected_node" not in st.session_state:
        st.session_state.selected_node = None
    
    if "current_agent" not in st.session_state:
        st.session_state.current_agent = None
    
    if "show_test_panel" not in st.session_state:
        st.session_state.show_test_panel = False

# Main application layout
if __name__ == "__main__" or 'streamlit' in sys.modules:
    st.title("AI Agent Studio")
    
    # Check for test panel
    if st.session_state.show_test_panel:
        render_test_panel()
    else:
        # Create a three-column layout
        col1, col2, col3 = st.columns([1, 3, 1])
        
        # Render the sidebar for agent management
        with col1:
            render_sidebar()
        
        # Render the main canvas for node editing
        with col2:
            render_canvas()
        
        # Render the node configuration panel
        with col3:
            render_node_config()