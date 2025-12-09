# Nursing Research Agents - Setup Guide

This guide will help you set up and run the 6 nursing research agents for your healthcare quality improvement project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Running the Agents](#running-the-agents)
- [Agent Overview](#agent-overview)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **pip** (Python package installer)
- **API Keys** for:
  - OpenAI (Required for all agents)
  - Exa (Required for Agent 1 only)
  - SerpAPI (Required for Agent 1 only)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/radfares/nursing-research-agents.git
cd nursing-research-agents
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If `requirements.txt` doesn't exist, install Agno:

```bash
pip install agno
```

---

## Environment Configuration

### 1. Copy the Environment Template

```bash
cp .env.example .env
```

### 2. Edit `.env` and Add Your API Keys

```bash
nano .env  # or use your preferred text editor
```

**Required for ALL agents:**
```bash
OPENAI_API_KEY=sk-...your-key-here...
```

**Required for Agent 1 (Nursing Research) only:**
```bash
EXA_API_KEY=your-exa-key-here
SERP_API_KEY=your-serp-api-key-here
```

### 3. Get Your API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **Exa**: https://exa.ai (for recent healthcare articles)
- **SerpAPI**: https://serpapi.com (for healthcare standards/guidelines)

### 4. Verify Setup

```bash
python3 -c "import os; print('OpenAI:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

---

## Running the Agents

### 1. Start the Project Assistant

The main entry point for the system is `run_nursing_project.py`. This handles project management, agent selection, and database initialization.

```bash
./start_nursing_project.sh
```

Or manually:

```bash
python3 run_nursing_project.py
```

### 2. Project Management

The system is **project-centric**. You will be prompted to:
1.  **Create a new project** (e.g., "fall_prevention_2025")
2.  **Switch to an existing project**
3.  **Launch agents** for the active project

### 3. Agent Selection

Once a project is active, you can select from the 6 specialized agents:
1.  **Nursing Research Agent**: Standards & Guidelines
2.  **Medical Research Agent**: PubMed Clinical Studies
3.  **Academic Research Agent**: ArXiv & Methodology
4.  **Research Writing Agent**: Writing & Synthesis
5.  **Project Timeline Agent**: Deadlines & Milestones
6.  **Data Analysis Planner**: Statistics & Sample Size

---

## Agent Overview

### Agent 1: Nursing Research Agent
- **Tools**: Exa, SerpAPI
- **Purpose**: PICOT development, literature searches, healthcare standards
- **API Keys**: OpenAI, Exa, SerpAPI

### Agent 2: Medical Research Agent (PubMed)
- **Tools**: PubMed
- **Purpose**: Biomedical and nursing literature from PubMed database
- **API Keys**: OpenAI only

### Agent 3: Academic Research Agent (ArXiv)
- **Tools**: ArXiv
- **Purpose**: Academic papers, statistical methods, theoretical research
- **API Keys**: OpenAI only

### Agent 4: Research Writing Agent
- **Tools**: None (pure writing assistant)
- **Purpose**: Academic writing, literature reviews, poster sections
- **API Keys**: OpenAI only

### Agent 5: Project Timeline Agent
- **Tools**: None (knowledge-based)
- **Purpose**: Track progress through nursing residency project (Nov 2025 - June 2026)
- **API Keys**: OpenAI only

### Agent 6: Data Analysis Planning Agent
- **Tools**: None (statistical expert)
- **Purpose**: Statistical test selection, sample size, data templates
- **API Keys**: OpenAI only

---

## Using Streaming Responses

All agents support streaming for real-time response generation:

```python
# Example: Streaming with Agent 2
from medical_research_agent import medical_research_agent

medical_research_agent.print_response(
    "Find 3 recent studies on fall prevention",
    stream=True
)
```

Streaming provides a better user experience for longer responses.

---

## Project Structure

```
nursing-research-agents/
├── agents/                      # All AI agents (organized)
│   ├── base_agent.py            # Shared utilities (logging, error handling)
│   ├── nursing_research_agent.py    # Agent 1
│   ├── medical_research_agent.py    # Agent 2
│   ├── academic_research_agent.py   # Agent 3
│   ├── research_writing_agent.py    # Agent 4
│   ├── nursing_project_timeline_agent.py  # Agent 5
│   └── data_analysis_agent.py   # Agent 6
├── agent_config.py              # Centralized configuration
├── main_menu.py                 # Interactive menu
├── .env.example                 # Environment template
├── .env                         # Your API keys (not in git)
├── .gitignore                   # Excludes .env, tmp/, etc.
└── docs/                        # Documentation
    └── phase_planning/          # Development phases
```

---

## Database Files

Agents use SQLite databases to maintain conversation history:

```
/tmp/nursing_research_agents_db/
├── nursing_research.db
├── medical_research.db
├── academic_research.db
├── research_writing.db
├── project_timeline.db
└── data_analysis.db
```

**Note**: These are in `/tmp` and may be cleared on system restart. This is intentional for privacy.

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'agno'"

**Solution**: Install Agno framework
```bash
pip install agno
```

### Issue: "API key not configured" warning

**Solution**:
1. Check `.env` file exists
2. Verify API keys are set correctly
3. For Agent 1, ensure both `EXA_API_KEY` and `SERP_API_KEY` are set

### Issue: Agent crashes on startup

**Solution**: Check logs for error details
```bash
# Logs are printed to console
# Look for ERROR level messages
```

### Issue: Database errors

**Solution**: Ensure `/tmp` directory is writable
```bash
ls -ld /tmp
# Should show: drwxrwxrwt
```

---

## Security Best Practices

1. **NEVER** commit `.env` to version control
2. **NEVER** share API keys publicly
3. **Rotate** API keys if they are ever exposed
4. **Monitor** API usage and costs regularly
5. Use **separate** API keys for development and production

---

## Cost Monitoring

### OpenAI Costs (All Agents)
- Model: GPT-4o
- Pricing: https://openai.com/pricing
- Typical cost: $0.01 - $0.05 per query

### Exa Costs (Agent 1 Only)
- Pricing: https://exa.ai/pricing
- Free tier available

### SerpAPI Costs (Agent 1 Only)
- Pricing: https://serpapi.com/pricing
- Free tier: 100 searches/month

**Tip**: Start with free tiers, monitor usage, upgrade as needed.

---

## Getting Help

- **Documentation**: `/docs/phase_planning/` folder
- **Issues**: Create an issue on GitHub
- **Agent Status**: Check `docs/phase_planning/` for detailed status

---

## Version Information

- **Phase 1**: Core Safety, Security & Stability ✅
- **Phase 2**: Architecture, Reuse & Streaming ✅
- **Phase 3**: Testing, Monitoring & Production (Planned)

---

## License

[Add your license information here]

---

## Acknowledgments

Built using the [Agno](https://agno.com) multi-agent framework.

---

**Last Updated**: 2025-11-16
**Version**: Beta 1 (Phase 2 Complete)
