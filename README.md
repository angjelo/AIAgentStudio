# AI Agent Studio

A visual platform for creating and managing AI agents using Python and Streamlit, with a canvas-based node editor.

## Features

- Visual node-based editor for creating AI agents with drag-and-drop functionality
- Interactive flow diagram with minimap and controls
- Integration with LLM providers like OpenAI (GPT) and Anthropic (Claude)
- Support for custom API connections and data transformations
- Node types for input, output, LLM, API, transform, condition, and loop
- Ability to test and debug agents
- Save and load agent configurations
- PostgreSQL database integration with Docker

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Usage

Run the application with:

```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Main Streamlit application
- `docker-compose.yml`: Docker configuration for PostgreSQL
- `src/components/`: UI components
  - `sidebar.py`: Agent management sidebar
  - `custom_canvas.py`: Node-based flow editor
  - `node_config.py`: Node configuration panel
  - `streamlit_flow/`: Custom flow diagram implementation
    - `elements.py`: Flow node and edge definitions
    - `flow.py`: Flow diagram renderer
    - `layouts.py`: Layout algorithms (Tree, Layered)
    - `state.py`: Flow state management
- `src/models/`: Data models
  - `database.py`: SQLAlchemy database models
  - `node.py`: Node, Edge, and Agent models
  - `node_types.py`: Node type definitions
- `src/services/`: Backend services
  - `agent_manager.py`: Agent CRUD operations
  - `database_manager.py`: Database interactions
  - `engine.py`: Agent execution engine
  - `providers/`: API integration providers
    - `anthropic_provider.py`: Claude integration
    - `api_provider.py`: External API integration
    - `openai_provider.py`: GPT integration
    - `transform_provider.py`: Data transformation
- `src/utils/`: Utility functions
- `saved_agents/`: Storage for saved agent configurations

## License

MIT
