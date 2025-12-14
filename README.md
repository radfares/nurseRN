# Nursing Research Project Assistant

> [!IMPORTANT]
> ## 🎯 USE BRANCH: `main`
> **All feature branches have been merged into `main`. This is the only branch you should use.**
> 
> Last updated: **December 6, 2025** | Grade: **95/100** (Production Ready)
> ```bash
> git checkout main && git pull origin main
> ```

A comprehensive multi-agent AI system designed to support nursing residents through their healthcare improvement projects (November 2025 - June 2026). Built with the Agno framework, this system provides specialized AI agents for research, writing, planning, and statistical analysis.

<div align="center">

![Status](https://img.shields.io/badge/status-production--ready-success)
![Branch](https://img.shields.io/badge/branch-main-brightgreen)
![Agents](https://img.shields.io/badge/agents-6%2B2_modes-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Updated](https://img.shields.io/badge/updated-Dec_6_2025-orange)

</div>

---


## 🎯 Overview

The Nursing Research Project Assistant is a project-centric multi-agent system that helps nursing residents:

- **Develop PICOT questions** for quality improvement projects
- **Search literature** across PubMed, ClinicalTrials.gov, medRxiv, Semantic Scholar, CORE, DOAJ, and web sources
- **Write and organize** research content
- **Track project milestones** and deadlines
- **Plan statistical analysis** and data collection
- **Manage multiple projects** with dedicated databases

---

## ✨ Features

### 🤖 Six Specialized AI Agents

1. **Nursing Research Agent** - PICOT development, healthcare standards, evidence-based practice
2. **Medical Research Agent** - PubMed searches for peer-reviewed clinical studies
3. **Academic Research Agent** - ArXiv searches for theoretical and methodological research
4. **Research Writing Agent** - Academic writing, literature synthesis, poster content
5. **Project Timeline Agent** - Milestone tracking and deadline management
6. **Data Analysis Planner** - Statistical test selection, sample size calculations, data templates
   - All agents use a standardized reasoning framework—see the "Reasoning Approach" section in each agent’s instructions.

### 📁 Project Management

- **Create Projects**: Initialize new projects with default milestones
- **Switch Projects**: Seamlessly switch between multiple projects
- **Archive Projects**: Archive completed projects
- **Project Databases**: Each project has its own SQLite database with 7 core tables:
  - PICOT versions
  - Literature findings
  - Analysis plans
  - Milestones
  - Writing drafts
  - Conversations
  - Documents

### 🛡️ Resilience & Reliability

- **Circuit Breakers**: Protect against API failures
- **Retry Logic**: Exponential backoff for transient failures
- **API Caching**: 24-hour TTL for API responses
- **Safe Tool Creation**: Graceful fallback when API keys are missing
- **Error Handling**: Comprehensive logging and error recovery

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (tested with Python 3.14.0)
- **OpenAI API Key** (required for all agents)
- **Optional API Keys**:
  - Exa API Key (for Nursing Research Agent)
  - SerpAPI Key (for Nursing Research Agent)
  - PubMed Email (for Medical Research Agent)
  - Feature flag: set `REASONING_BLOCK=off` to disable the standardized reasoning blocks (defaults to on)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nurseRN
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Verify setup**
   ```bash
   python3 verify_setup.py
   ```

### Running the System

**Option 1: Use the start script (recommended)**
```bash
./start_nursing_project.sh
```

**Option 2: Manual start**
```bash
source .venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno"
python3 run_nursing_project.py
```

---

## 📖 Usage Guide

### Project Management

When you start the system, you'll see the project management menu:

```
PROJECT MANAGEMENT
================================================================================

★ ACTIVE PROJECT: my_project

Project Commands:
  new <project_name>     - Create new project
  list                   - List all projects
  switch <project_name>  - Switch to project
  archive <project_name> - Archive project
  agents                 - Launch agents (requires active project)
  exit                   - Exit program
```

### Using Agents

1. **Create or switch to a project**: `new my_project` or `switch my_project`
2. **Launch agents**: `agents`
3. **Select an agent**: Choose 1-6 from the menu
4. **Chat with agent**: Ask questions naturally
5. **Switch agents**: Type `switch` to return to agent menu
6. **Return to projects**: Type `back` to return to project menu

### Example Queries

**Nursing Research Agent:**
```
Help me develop a PICOT question for reducing patient falls in a medical-surgical unit
```

**Medical Research Agent:**
```
Find 3 recent peer-reviewed articles about catheter-associated urinary tract infection prevention
```

**Research Writing Agent:**
```
Help me write a PICOT question about reducing CAUTI in ICU patients
```

**Data Analysis Planner:**
```
Catheter infection rate: baseline 15%, target 8%. Need sample size calculation.
```

---

## 🏗️ Architecture

### Project Structure

```
nurseRN/
├── agents/                            # All AI agents (organized)
│   ├── base_agent.py                  # Base class for all agents
│   ├── nursing_research_agent.py      # Agent 1: Nursing Research
│   ├── medical_research_agent.py      # Agent 2: Medical Research (PubMed)
│   ├── academic_research_agent.py     # Agent 3: Academic Research (ArXiv)
│   ├── research_writing_agent.py      # Agent 4: Research Writing
│   ├── nursing_project_timeline_agent.py  # Agent 5: Project Timeline
│   └── data_analysis_agent.py         # Agent 6: Data Analysis
├── run_nursing_project.py             # Main entry point
├── start_nursing_project.sh           # Quick start script
├── project_manager.py                 # Project management system
├── agent_config.py                    # Centralized configuration
├── src/services/
│   ├── api_tools.py                   # Safe API tool creation
│   └── circuit_breaker.py             # Circuit breaker protection
├── data/
│   ├── projects/                      # Project databases
│   └── archives/                      # Archived projects
├── tmp/                               # Agent session databases
├── libs/agno/                         # Vendored Agno framework
└── requirements.txt                   # Python dependencies
```

### Key Components

**BaseAgent Class** (`agents/base_agent.py`)
- Abstract base class for all agents
- Provides logging, error handling, and agent creation
- Ensures consistent architecture across agents

**Agent Configuration** (`agent_config.py`)
- Centralized database paths
- Model configuration
- Logging settings
- Helper functions

**Project Manager** (`project_manager.py`)
- Project creation and management
- Database initialization with schema
- Default milestones (Nov 2025 - June 2026)
- Project switching and archival

**API Tools** (`src/services/api_tools.py`)
- Safe tool creation with fallback
- Circuit breaker protection
- API status reporting
- HTTP response caching

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional (for enhanced functionality)
EXA_API_KEY=your-exa-api-key-here
SERP_API_KEY=your-serpapi-key-here
PUBMED_EMAIL=your-email@example.com

# Optional configuration
AGENT_LOG_LEVEL=INFO
```

### Model Configuration

Default models can be overridden via environment variables:

```bash
AGENT_NURSING_RESEARCH_MODEL=gpt-4o
AGENT_MEDICAL_RESEARCH_MODEL=gpt-4o
AGENT_ACADEMIC_RESEARCH_MODEL=gpt-4o
AGENT_RESEARCH_WRITING_MODEL=gpt-4o
AGENT_PROJECT_TIMELINE_MODEL=gpt-4o-mini
AGENT_DATA_ANALYSIS_MODEL=gpt-4o
```

---

## 📚 Documentation

- **[AGENT_STATUS.md](AGENT_STATUS.md)** - Detailed agent status and capabilities
- **[NURSING_PROJECT_GUIDE.md](NURSING_PROJECT_GUIDE.md)** - Comprehensive usage guide
- **[NEW_AGENTS_GUIDE.md](NEW_AGENTS_GUIDE.md)** - PubMed/ArXiv agent guide
- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[GITHUB_SETUP_GUIDE.md](GITHUB_SETUP_GUIDE.md)** - GitHub repository setup

---

## 🧪 Testing

### Verify Setup

```bash
python3 verify_setup.py
```

This checks:
- Python version
- Project structure
- Core dependencies
- Agno library import
- Environment file and API keys

### Run Individual Agents

Each agent can be run standalone for testing:

```bash
python3 -m agents.nursing_research_agent
python3 -m agents.medical_research_agent
python3 -m agents.academic_research_agent
python3 -m agents.research_writing_agent
python3 -m agents.nursing_project_timeline_agent
python3 -m agents.data_analysis_agent
```

---

## 💰 Cost Estimates

| Agent | Model | Cost per Query | Typical Session |
|-------|-------|----------------|-----------------|
| Nursing Research | GPT-4o | ~$0.03 | $0.30-0.60 |
| Medical Research | GPT-4o | ~$0.02 | $0.20-0.40 |
| Academic Research | GPT-4o | ~$0.02 | $0.20-0.40 |
| Research Writing | GPT-4o | ~$0.04 | $0.40-0.80 |
| Timeline Agent | GPT-4o-mini | ~$0.001 | $0.01-0.05 |
| Data Analysis | GPT-4o | ~$0.02 | $0.20-0.40 |

**Total monthly budget (moderate use)**: $10-20

---

## 🔐 Security

- ✅ API keys stored in `.env` file (not committed to git)
- ✅ `.env` file is in `.gitignore`
- ✅ No hardcoded credentials
- ✅ Safe tool creation with fallback patterns
- ✅ Circuit breakers prevent API abuse

---

## 🛠️ Development

### Adding a New Agent

1. Create a new file: `my_new_agent.py`
2. Inherit from `BaseAgent`:
   ```python
   from base_agent import BaseAgent
   
   class MyNewAgent(BaseAgent):
       def __init__(self):
           super().__init__(
               agent_name="My New Agent",
               agent_key="my_new_agent",
               tools=[]  # Add tools if needed
           )
       
       def _create_agent(self):
           # Create and return Agent instance
           pass
       
       def show_usage_examples(self):
           # Display usage examples
           pass
   ```
3. Add database path to `agent_config.py`
4. Add to `run_nursing_project.py` agent menu

### Project Structure Guidelines

- **Agents**: One file per agent in project root
- **Services**: Shared utilities in `src/services/`
- **Configuration**: Centralized in `agent_config.py`
- **Databases**: Agent sessions in `tmp/`, projects in `data/projects/`

---

## 📝 License

This project uses the Agno framework (vendored in `libs/agno/`). See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📞 Support

For issues, questions, or contributions:
- Check existing documentation files
- Review `AGENT_STATUS.md` for agent capabilities
- Run `verify_setup.py` to diagnose setup issues

---

## 🎉 Acknowledgments

Built with:
- **[Agno Framework](https://agno.com)** - Multi-agent framework and runtime
- **OpenAI GPT-4o** - Primary language model
- **PubMed API** - Biomedical literature database
- **ArXiv API** - Academic paper repository

---

**Status**: Production-ready ✅  
**Branch**: `main` ← **USE THIS ONE**  
**Last Updated**: December 6, 2025  
**Version**: 2.0.0 (Orchestration + System Hardening)
