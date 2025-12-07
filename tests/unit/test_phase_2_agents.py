import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import json
import shutil
from pathlib import Path

# Skip entire module if agno is mocked/polluted by other tests
pytest.importorskip("agno.models.response", reason="agno module polluted by other tests")

from agents.medical_research_agent import MedicalResearchAgent
from agents.nursing_research_agent import NursingResearchAgent
from agents.academic_research_agent import AcademicResearchAgent
from agents.research_writing_agent import ResearchWritingAgent
from agents.nursing_project_timeline_agent import ProjectTimelineAgent
from agents.data_analysis_agent import DataAnalysisAgent
from src.services.agent_audit_logger import AuditLogger

# Fixture to clean up audit logs after tests
@pytest.fixture
def clean_audit_logs():
    log_dir = Path(".claude/agent_audit_logs")
    if log_dir.exists():
        shutil.rmtree(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    yield
    # Cleanup after test
    if log_dir.exists():
        shutil.rmtree(log_dir)

class TestPhase2AgentTemperature:
    """Verify all agents have temperature=0 (factual mode)."""
    
    def test_medical_research_agent_temperature_zero(self):
        agent = MedicalResearchAgent()
        assert agent.agent.model.temperature == 0

    def test_nursing_research_agent_temperature_zero(self):
        agent = NursingResearchAgent()
        # This might fail initially until fixed
        assert agent.agent.model.temperature == 0

    def test_academic_research_agent_temperature_zero(self):
        agent = AcademicResearchAgent()
        assert agent.agent.model.temperature == 0

    def test_research_writing_agent_temperature_zero(self):
        agent = ResearchWritingAgent()
        assert agent.agent.model.temperature == 0

    def test_project_timeline_agent_temperature_zero(self):
        agent = ProjectTimelineAgent()
        assert agent.agent.model.temperature == 0

    def test_data_analysis_agent_temperature_zero(self):
        agent = DataAnalysisAgent()
        assert agent.agent.model.temperature == 0

class TestPhase2AuditLogging:
    """Verify all agents have audit logging enabled."""

    def test_medical_research_agent_has_audit_logger(self):
        agent = MedicalResearchAgent()
        assert hasattr(agent, "audit_logger")
        assert isinstance(agent.audit_logger, AuditLogger)

    def test_nursing_research_agent_has_audit_logger(self):
        agent = NursingResearchAgent()
        assert hasattr(agent, "audit_logger")
        assert isinstance(agent.audit_logger, AuditLogger)

    def test_academic_research_agent_has_audit_logger(self):
        agent = AcademicResearchAgent()
        assert hasattr(agent, "audit_logger")
        assert isinstance(agent.audit_logger, AuditLogger)

    def test_research_writing_agent_has_audit_logger(self):
        agent = ResearchWritingAgent()
        assert hasattr(agent, "audit_logger")
        assert isinstance(agent.audit_logger, AuditLogger)

    def test_project_timeline_agent_has_audit_logger(self):
        agent = ProjectTimelineAgent()
        assert hasattr(agent, "audit_logger")
        assert isinstance(agent.audit_logger, AuditLogger)

    def test_data_analysis_agent_has_audit_logger(self):
        agent = DataAnalysisAgent()
        assert hasattr(agent, "audit_logger")
        assert isinstance(agent.audit_logger, AuditLogger)

class TestPhase2ValidationSystems:
    """Verify validation systems are in place."""

    def test_medical_research_validation(self):
        agent = MedicalResearchAgent()
        assert hasattr(agent, "run_with_grounding_check")
        assert hasattr(agent, "_extract_verified_pmids_from_output")

    def test_nursing_research_validation(self):
        agent = NursingResearchAgent()
        # Should have validation methods
        assert hasattr(agent, "_validate_run_output") or hasattr(agent, "run_with_grounding_check")

    def test_academic_research_validation(self):
        agent = AcademicResearchAgent()
        # Should have validation methods (to be implemented)
        assert hasattr(agent, "run_with_grounding_check") or hasattr(agent, "_validate_run_output")

    def test_research_writing_validation(self):
        agent = ResearchWritingAgent()
        # Should have validation methods (to be implemented)
        assert hasattr(agent, "run_with_grounding_check") or hasattr(agent, "_validate_run_output")

    def test_project_timeline_validation(self):
        agent = ProjectTimelineAgent()
        # Should have validation methods (to be implemented)
        assert hasattr(agent, "run_with_grounding_check") or hasattr(agent, "_validate_run_output")

    def test_data_analysis_validation(self):
        agent = DataAnalysisAgent()
        # Should have validation methods (to be implemented)
        assert hasattr(agent, "run_with_grounding_check") or hasattr(agent, "_validate_run_output")

class TestPhase2AuditTrailFormat:
    """Verify audit logs are written correctly."""

    def test_audit_log_creation(self, clean_audit_logs):
        # Initialize an agent which should create a log file
        agent = MedicalResearchAgent()
        
        # Simulate a log entry
        agent.audit_logger.log_query_received("test query", "test_project")
        
        # Check file exists
        log_file = Path(f".claude/agent_audit_logs/{agent.agent_key}_audit.jsonl")
        assert log_file.exists()
        
        # Check content
        with open(log_file, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry["action_type"] == "query_received"
            assert entry["agent_key"] == agent.agent_key
