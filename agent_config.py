"""
Centralized Configuration for Nursing Research Agents
Handles paths, directories, and common settings across all 6 agents.

Created: 2025-11-16 (Phase 1 - Core Safety, Security & Stability)
"""

import os
from pathlib import Path

# ============================================================================
# PROJECT ROOT & DIRECTORIES
# ============================================================================

# Get project root (directory containing this config file)
PROJECT_ROOT = Path(__file__).parent.resolve()

# Database directory (create if doesn't exist)
DB_DIR = PROJECT_ROOT / "tmp"
DB_DIR.mkdir(exist_ok=True)

# ============================================================================
# DATABASE PATHS (Absolute paths for all agents)
# ============================================================================

DATABASE_PATHS = {
    "nursing_research": str(DB_DIR / "nursing_research_agent.db"),
    "medical_research": str(DB_DIR / "medical_research_agent.db"),
    "academic_research": str(DB_DIR / "academic_research_agent.db"),
    "research_writing": str(DB_DIR / "research_writing_agent.db"),
    "project_timeline": str(DB_DIR / "project_timeline_agent.db"),
    "data_analysis": str(DB_DIR / "data_analysis_agent.db"),
}

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Default models for each agent (can be overridden via environment variables)
DEFAULT_MODELS = {
    "nursing_research": "gpt-4o",
    "medical_research": "gpt-4o",
    "academic_research": "gpt-4o",
    "research_writing": "gpt-4o",
    "project_timeline": "gpt-4o-mini",  # Cheaper for timeline queries
    "data_analysis": "gpt-4o",
}

# Model-specific parameters
DATA_ANALYSIS_TEMPERATURE = 0.2  # Low for statistical reliability
DATA_ANALYSIS_MAX_TOKENS = 1600  # JSON + short prose

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv("AGENT_LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_db_path(agent_name: str) -> str:
    """
    Get the absolute database path for a given agent.

    Args:
        agent_name: One of: nursing_research, medical_research, academic_research,
                    research_writing, project_timeline, data_analysis

    Returns:
        Absolute path to the agent's database file

    Raises:
        ValueError: If agent_name is not recognized
    """
    if agent_name not in DATABASE_PATHS:
        raise ValueError(
            f"Unknown agent: {agent_name}. "
            f"Valid agents: {', '.join(DATABASE_PATHS.keys())}"
        )
    return DATABASE_PATHS[agent_name]


def get_model_id(agent_name: str) -> str:
    """
    Get the default model ID for a given agent.

    Can be overridden via environment variable: AGENT_{NAME}_MODEL

    Args:
        agent_name: Agent identifier

    Returns:
        Model ID (e.g., "gpt-4o", "gpt-4o-mini")
    """
    env_var = f"AGENT_{agent_name.upper()}_MODEL"
    return os.getenv(env_var, DEFAULT_MODELS.get(agent_name, "gpt-4o"))


def ensure_db_directory():
    """Ensure the database directory exists. Called on module import."""
    DB_DIR.mkdir(parents=True, exist_ok=True)


# Auto-create DB directory when module is imported
ensure_db_directory()
