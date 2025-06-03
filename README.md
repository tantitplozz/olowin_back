# OmniCard-AI: Multi-Agent Financial Transaction Analysis System

OmniCard-AI is a sophisticated multi-agent system designed for real-time financial transaction analysis, risk assessment, and intelligent decision-making.

## Features

- **Multi-Agent Workflow**: Specialized agents for various tasks working together
- **Dynamic LLM Routing**: Intelligent routing of prompts to appropriate LLMs
- **Vectorized Memory**: Persistent memory using ChromaDB
- **Real-time Monitoring**: Logging and monitoring via FastAPI and WebSocket
- **Containerized Services**: Easy deployment with Docker
- **Interactive Interface**: CLI and API endpoints for interaction
- **AutoBuyer Agent**: MetaGPT-powered agent for simulating human browsing behavior

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js & npm (if using the frontend part)
- API Keys (e.g., Google Gemini, OpenAI, GoLogin as per `.env.example`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/omnicard-ai.git # Replace with your actual repo URL
    cd omnicard-ai
    ```

2.  **Set up environment variables:**
    Create a `.env` file from the example and populate it with your actual API keys and configurations.
    ```bash
    cp .env.example .env
    # Edit .env with your API keys and configuration
    ```

3.  **Create necessary data directories (if not handled by Docker volumes initially):**
    ```bash
    mkdir -p data/chromadb
    ```

4.  **Install Python dependencies (preferably in a virtual environment):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

5.  **Build and start Docker services (for containerized deployment):**
    ```bash
    docker-compose up --build -d
    ```
    This will build the images and start the `api`, `mongodb`, and `frontend` (if configured) services.

6.  **Set up the frontend (if applicable and not fully handled by Docker):**
    If you have a separate frontend setup (e.g., in the `frontend/` directory):
    ```bash
    cd frontend
    npm install
    npm run dev # Or your frontend start command
    ```

### Usage

The application can be run in different modes using `main.py`:

*   **API Mode (Default with Docker):**
    The FastAPI server will be accessible (default: `http://localhost:8000`).
    If running locally without Docker:
    ```bash
    python main.py --mode api
    ```

*   **CLI Mode:**
    Execute tasks directly via the command line.
    ```bash
    python main.py --mode cli --task "Your task description here"
    ```

*   **MetaGPT Mode (for specific scripts like `run_metagpt_with_promptilus.py`):**
    ```bash
    python main.py --mode metagpt --task "Your task for MetaGPT script"
    ```

#### Web Interface

If the frontend service is running (default: `http://localhost:5173`), you can access the web UI there.

#### API Endpoints

(Assuming standard FastAPI setup from `api/server.py`)
-   `GET /`: Main HTML page (if `index.html` is served)
-   `POST /submit_task`: Submit a task to the system. Body: `{"task": "your task description"}`
-   Other endpoints as defined in `api/server.py`.

## AutoBuyer Agent

The AutoBuyer Agent, likely located in `autobuyer_project/`, uses the MetaGPT framework to simulate human browsing behavior for tasks like cookie collection and e-commerce interactions.

### Setup (AutoBuyer)

1.  Navigate to the autobuyer directory:
    ```bash
    cd autobuyer_project
    ```

2.  Install its specific dependencies (if any beyond the main `requirements.txt`):
    ```bash
    # pip install -r requirements.txt # if it has its own
    playwright install --with-deps chromium # Example if Playwright is used
    ```

3.  Configure the agent (check for a `config.yaml` or similar in its directory):
    ```bash
    # cp config.example.yaml config.yaml # If applicable
    # Edit its configuration file with necessary API keys and settings
    ```

4.  Run the AutoBuyer agent (this might be integrated into the main system or run standalone):
    ```bash
    # python autobuyer_main.py # Or however it's invoked
    ```

## Project Structure Overview

```
omnicard-ai/ (or MEEMEE/)
├── .git/                    # Git repository data
├── .github/                 # GitHub specific files (e.g., workflows)
├── .vscode/                 # VS Code settings
├── api/                     # FastAPI server code (e.g., server.py)
├── agents/                  # Core agent implementations
├── agent_prompts/           # Prompts for agents
├── autobuyer_project/       # AutoBuyer agent module
├── clients/                 # Clients for external services (e.g., LLM APIs)
├── config/                  # Application configuration files
├── data/                    # Persistent data (e.g., ChromaDB, logs if not in root `logs`)
│   └── chromadb/
├── frontend/                # Frontend application (e.g., React, Vue)
├── knowledge_bases/         # Knowledge base files for agents
├── loggers/                 # Logging utilities
├── memory/                  # Memory management components
├── metagpt/                 # MetaGPT framework related code (if customized or vendored)
├── metagpt_integration/     # Integration code with MetaGPT
├── scripts/                 # Utility and standalone scripts
├── static/                  # Static assets for the web server (CSS, JS, images)
├── templates/               # HTML templates for FastAPI
├── tests/                   # Test suite
├── utils/                   # Utility functions and classes
├── workflow/                # Workflow definitions and management
├── .env                     # Local environment variables (GITIGNORED)
├── .env.example             # Example environment variables
├── .gitignore               # Specifies intentionally untracked files that Git should ignore
├── .pylintrc                # Pylint configuration
├── CODE_OF_CONDUCT.md       # Code of Conduct for contributors
├── CONTRIBUTING.md          # Guidelines for contributing
├── Dockerfile               # Docker build instructions for the main application
├── LICENSE                  # Project license (e.g., MIT)
├── main.py                  # Main entry point for the application
├── pyproject.toml           # Python project configuration (packaging, tools)
├── README.md                # This file: Project overview and instructions
└── requirements.txt         # Python dependencies
```

This structure is a general guideline and might vary based on the actual project layout.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing to the project. 