## Project Overview

This is a Python-based, multi-agent AI system designed to assist nursing residents with healthcare improvement projects. The system is built using the `agno` framework (vendored in the `libs/` directory) and features a suite of specialized agents for tasks like research, writing, and project management.

The architecture is project-centric, meaning users can create and switch between multiple research projects. Each project gets its own dedicated SQLite database to store all related artifacts, including PICOT questions, literature findings, data analysis plans, and conversation history.

The core of the system resides in the `agents/` directory, where each agent is defined. These agents inherit from a common `BaseAgent` and use a centralized configuration (`agent_config.py`). The main entry point is `run_nursing_project.py`, which provides a command-line interface for managing projects and interacting with the agents.

**Key Technologies:**
- Python 3.8+
- Agno Framework (for agent creation and management)
- OpenAI (for language models like GPT-4o)
- SQLite (for project-specific databases)
- Tools: `biopython` (PubMed), `google-search-results` (SerpAPI)

## Building and Running

### 1. Setup

The project uses a virtual environment and `requirements.txt` for dependency management.

**Setup command (Unix/macOS):**
```bash
# First time setup
./scripts/dev_setup.sh
```

**Activate environment:**
```bash
source .venv/bin/activate
```

### 2. Running the Application

The main application is launched via a shell script that handles environment setup and execution.

**Start command:**
```bash
./start_nursing_project.sh
```
This script will launch an interactive CLI where you can manage projects and select an agent to chat with.

### 3. Running Tests

The project uses `pytest` for testing. A convenience script is provided to run the full test suite.

**Test command:**
```bash
./scripts/test.sh
```

## Development Conventions

- **Project Structure:** The system is organized into distinct modules:
    - `agents/`: Contains the definitions for each specialized AI agent.
    - `src/services/`: Shared utilities like circuit breakers and API tool creators.
    - `data/projects/`: Stores the SQLite databases for each project.
    - `scripts/`: Houses shell scripts for setup, testing, and formatting.
- **Agent Design:** Agents inherit from the `BaseAgent` class (`agents/base_agent.py`) to ensure a consistent structure, including logging and error handling.
- **Configuration:** All configuration (database paths, model IDs, logging levels) is centralized in `agent_config.py`. API keys are managed via a `.env` file.
- **Code Style:** Code formatting is enforced using `ruff`. The `format.sh` script should be run before committing changes.
- **Type Checking:** Static type analysis is performed with `mypy`. The `validate.sh` script runs this check.
- **Contribution:** The `CONTRIBUTING.md` file outlines the fork-and-pull-request workflow and PR naming conventions.
