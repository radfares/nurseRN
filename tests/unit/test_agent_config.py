"""
Unit tests for agent_config.py
Tests configuration functions in isolation
"""

import pytest
import os
from pathlib import Path
from agent_config import (
    get_db_path,
    get_model_id,
    ensure_db_directory,
    DATABASE_PATHS,
    DEFAULT_MODELS,
    DB_DIR,
    PROJECT_ROOT
)


class TestGetDbPath:
    """Test the get_db_path function"""

    def test_valid_agent_names(self):
        """Test that all valid agent names return paths"""
        valid_agents = [
            "nursing_research",
            "medical_research",
            "academic_research",
            "research_writing",
            "project_timeline",
            "data_analysis",
            "citation_validation",
        ]

        for agent in valid_agents:
            path = get_db_path(agent)
            assert path is not None, f"Path for {agent} should not be None"
            assert isinstance(path, str), f"Path for {agent} should be a string"
            assert path.endswith(".db"), f"Path for {agent} should end with .db"

    def test_invalid_agent_raises_error(self):
        """Test that invalid agent name raises ValueError"""
        with pytest.raises(ValueError, match="Unknown agent"):
            get_db_path("invalid_agent")

    def test_returns_absolute_path(self):
        """Test that returned paths are absolute"""
        path = get_db_path("nursing_research")
        assert os.path.isabs(path), "Returned path should be absolute"

    def test_each_agent_has_unique_path(self):
        """Test that each agent has a unique database path"""
        paths = [get_db_path(agent) for agent in DATABASE_PATHS.keys()]
        assert len(paths) == len(set(paths)), "All agent paths should be unique"

    def test_path_includes_tmp_directory(self):
        """Test that database paths are in the tmp directory"""
        path = get_db_path("nursing_research")
        assert "/tmp/" in path or "\\tmp\\" in path, "Path should include tmp directory"


class TestGetModelId:
    """Test the get_model_id function"""

    def test_default_model_for_nursing_research(self):
        """Test default model retrieval for nursing research agent"""
        model = get_model_id("nursing_research")
        assert model == "gpt-4o", "Default model should be gpt-4o"

    def test_default_model_for_project_timeline(self):
        """Test that project_timeline uses gpt-4o-mini"""
        model = get_model_id("project_timeline")
        assert model == "gpt-4o-mini", "Project timeline should use cheaper model"

    def test_env_override(self, monkeypatch):
        """Test environment variable override"""
        monkeypatch.setenv("AGENT_NURSING_RESEARCH_MODEL", "gpt-4o-mini")
        model = get_model_id("nursing_research")
        assert model == "gpt-4o-mini", "Environment variable should override default"

    def test_fallback_for_unknown_agent(self):
        """Test fallback to gpt-4o for unknown agents"""
        model = get_model_id("unknown_agent")
        assert model == "gpt-4o", "Unknown agents should fallback to gpt-4o"

    def test_all_default_models_defined(self):
        """Test that all agents have default models"""
        expected_agents = {
            "nursing_research",
            "medical_research",
            "academic_research",
            "research_writing",
            "project_timeline",
            "data_analysis",
            "citation_validation",
        }
        assert set(DEFAULT_MODELS.keys()) == expected_agents, "All agents should have default models"


class TestEnsureDbDirectory:
    """Test the ensure_db_directory function"""

    def test_creates_directory(self, tmp_path, monkeypatch):
        """Test that directory is created"""
        test_dir = tmp_path / "test_db"
        monkeypatch.setattr("agent_config.DB_DIR", test_dir)

        ensure_db_directory()
        assert test_dir.exists(), "Directory should be created"
        assert test_dir.is_dir(), "Path should be a directory"

    def test_idempotent(self, tmp_path, monkeypatch):
        """Test that running multiple times doesn't error"""
        test_dir = tmp_path / "test_db"
        monkeypatch.setattr("agent_config.DB_DIR", test_dir)

        # Run multiple times
        ensure_db_directory()
        ensure_db_directory()
        ensure_db_directory()

        assert test_dir.exists(), "Directory should still exist after multiple calls"

    def test_handles_existing_directory(self, tmp_path, monkeypatch):
        """Test behavior when directory already exists"""
        test_dir = tmp_path / "test_db"
        test_dir.mkdir(parents=True, exist_ok=True)  # Create it first

        monkeypatch.setattr("agent_config.DB_DIR", test_dir)

        # Should not raise error
        ensure_db_directory()
        assert test_dir.exists(), "Directory should still exist"


class TestDatabasePaths:
    """Test DATABASE_PATHS configuration"""

    def test_all_paths_unique(self):
        """Ensure all database paths are unique"""
        paths = list(DATABASE_PATHS.values())
        assert len(paths) == len(set(paths)), "All database paths should be unique"

    def test_all_agents_have_paths(self):
        """Ensure all agents have database paths"""
        expected_agents = {
            "nursing_research",
            "medical_research",
            "academic_research",
            "research_writing",
            "project_timeline",
            "data_analysis",
            "citation_validation",
        }
        assert set(DATABASE_PATHS.keys()) == expected_agents, "All agents should have paths"

    def test_all_paths_are_strings(self):
        """Ensure all paths are strings"""
        for agent, path in DATABASE_PATHS.items():
            assert isinstance(path, str), f"Path for {agent} should be a string"

    def test_all_paths_end_with_db(self):
        """Ensure all paths have .db extension"""
        for agent, path in DATABASE_PATHS.items():
            assert path.endswith(".db"), f"Path for {agent} should end with .db"

    def test_paths_contain_agent_names(self):
        """Test that database paths contain agent names for clarity"""
        for agent, path in DATABASE_PATHS.items():
            # Convert underscores to match filename convention
            agent_name_part = agent.replace("_", "_")
            assert agent_name_part in path, f"Path should contain agent name: {agent}"


class TestProjectConfiguration:
    """Test project-level configuration"""

    def test_project_root_exists(self):
        """Test that PROJECT_ROOT points to an existing directory"""
        assert PROJECT_ROOT.exists(), "PROJECT_ROOT should exist"
        assert PROJECT_ROOT.is_dir(), "PROJECT_ROOT should be a directory"

    def test_project_root_is_absolute(self):
        """Test that PROJECT_ROOT is an absolute path"""
        assert PROJECT_ROOT.is_absolute(), "PROJECT_ROOT should be absolute path"

    def test_db_dir_is_within_project(self):
        """Test that DB_DIR is within PROJECT_ROOT"""
        assert PROJECT_ROOT in DB_DIR.parents or DB_DIR == PROJECT_ROOT / "tmp", \
            "DB_DIR should be within PROJECT_ROOT"

    def test_db_dir_name_is_tmp(self):
        """Test that database directory is named 'tmp'"""
        assert DB_DIR.name == "tmp", "Database directory should be named 'tmp'"


class TestDefaultModels:
    """Test DEFAULT_MODELS configuration"""

    def test_all_models_are_strings(self):
        """Test that all model IDs are strings"""
        for agent, model in DEFAULT_MODELS.items():
            assert isinstance(model, str), f"Model for {agent} should be a string"

    def test_all_models_start_with_gpt(self):
        """Test that all models are GPT models"""
        for agent, model in DEFAULT_MODELS.items():
            assert model.startswith("gpt-"), f"Model for {agent} should start with 'gpt-'"

    def test_project_timeline_uses_cheaper_model(self):
        """Test that project timeline uses the cheaper model"""
        assert DEFAULT_MODELS["project_timeline"] == "gpt-4o-mini", \
            "Project timeline should use cheaper model for cost efficiency"

    def test_research_agents_use_premium_model(self):
        """Test that research agents use premium models"""
        research_agents = [
            "nursing_research",
            "medical_research",
            "academic_research",
            "research_writing",
            "data_analysis"
        ]
        for agent in research_agents:
            assert DEFAULT_MODELS[agent] == "gpt-4o", \
                f"{agent} should use premium gpt-4o model"
