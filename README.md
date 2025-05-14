# AI Agent Studio

A visual platform for creating and managing AI agents using Python and Streamlit.

## Features

- Visual node-based editor for creating AI agents
- Integration with LLM providers like OpenAI (GPT) and Anthropic (Claude)
- Support for custom API connections
- Ability to test and debug agents
- Save and load agent configurations

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
- `src/components/`: UI components
- `src/models/`: Data models
- `src/services/`: Backend services
- `src/utils/`: Utility functions
- `saved_agents/`: Storage for saved agent configurations

## License

MIT
