"""
Nursing Research Agent System - Integration Test Suite
Tests all 6 agents and their integration points
"""

import os
import sys
import pytest


def test_agent_imports():
    """Test that all agents can be imported"""
    agents = [
        ('agents.nursing_research_agent', 'NursingResearchAgent'),
        ('agents.nursing_project_timeline_agent', 'ProjectTimelineAgent'),
        ('agents.medical_research_agent', 'MedicalResearchAgent'),
        ('agents.academic_research_agent', 'AcademicResearchAgent'),
        ('agents.research_writing_agent', 'ResearchWritingAgent'),
        ('agents.data_analysis_agent', 'DataAnalysisAgent'),
    ]

    for module_name, class_name in agents:
        # ASSERTION: Module should import without error
        try:
            module = __import__(module_name, fromlist=[class_name])
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")

        # ASSERTION: Class should exist in module
        assert hasattr(module, class_name), \
            f"Agent class {class_name} not found in module {module_name}"

        # ASSERTION: Class should be instantiable
        agent_class = getattr(module, class_name)
        assert callable(agent_class), \
            f"{class_name} should be a callable class"


def test_agent_response():
    """Test that nursing research agent can respond to queries"""
    from agents.nursing_research_agent import NursingResearchAgent

    agent = NursingResearchAgent()

    # ASSERTION 1: Agent should have 'agent' attribute
    assert hasattr(agent, 'agent'), \
        "NursingResearchAgent should have 'agent' attribute"

    # ASSERTION 2: Agent should have 'run' method
    assert hasattr(agent.agent, 'run'), \
        "Agent should have 'run' method for queries"

    # ASSERTION 3: Agent should respond to simple query
    test_query = "What is a PICOT question?"
    response = agent.agent.run(test_query)

    assert response is not None, \
        "Agent should return a response (not None)"

    # ASSERTION 4: Response should have content
    assert hasattr(response, 'content'), \
        "Response should have 'content' attribute"

    assert response.content is not None, \
        "Response content should not be None"

    assert len(response.content) > 0, \
        "Response content should not be empty"


def test_all_agents():
    """Test that all agent classes exist and are instantiable"""
    from agents.nursing_research_agent import NursingResearchAgent
    from agents.medical_research_agent import MedicalResearchAgent
    from agents.academic_research_agent import AcademicResearchAgent
    from agents.research_writing_agent import ResearchWritingAgent
    from agents.nursing_project_timeline_agent import ProjectTimelineAgent
    from agents.data_analysis_agent import DataAnalysisAgent

    agents = [
        NursingResearchAgent,
        MedicalResearchAgent,
        AcademicResearchAgent,
        ResearchWritingAgent,
        ProjectTimelineAgent,
        DataAnalysisAgent,
    ]

    for agent_class in agents:
        # ASSERTION 1: Agent should instantiate
        agent_instance = agent_class()
        assert agent_instance is not None, \
            f"{agent_class.__name__} should instantiate successfully"

        # ASSERTION 2: Agent should have agent_name attribute
        assert hasattr(agent_instance, 'agent_name'), \
            f"{agent_class.__name__} should have 'agent_name' attribute"

        # ASSERTION 3: Agent name should be non-empty string
        assert isinstance(agent_instance.agent_name, str), \
            f"{agent_class.__name__}.agent_name should be a string"

        assert len(agent_instance.agent_name) > 0, \
            f"{agent_class.__name__}.agent_name should not be empty"


def test_menu_system():
    """Test the main menu runner exists and has required functions"""
    # ASSERTION 1: Module should import
    try:
        import run_nursing_project
    except ImportError as e:
        pytest.fail(f"Failed to import run_nursing_project: {e}")

    # ASSERTION 2: Should have main function
    assert hasattr(run_nursing_project, 'main'), \
        "run_nursing_project should have 'main' function"

    # ASSERTION 3: main should be callable
    assert callable(run_nursing_project.main), \
        "run_nursing_project.main should be callable"

    # ASSERTION 4: Should have run_agent_interaction function
    assert hasattr(run_nursing_project, 'run_agent_interaction'), \
        "run_nursing_project should have 'run_agent_interaction' function"

    assert callable(run_nursing_project.run_agent_interaction), \
        "run_nursing_project.run_agent_interaction should be callable"
