"""
Nursing Research Agent System - Agent Module

This module contains all 7 specialized AI agents plus the base agent class.

Architecture:
- BaseAgent: Abstract base class providing common functionality
- 7 Specialized Agents: Each inherits from BaseAgent

Agents:
1. NursingResearchAgent - PICOT development, healthcare standards
2. MedicalResearchAgent - PubMed searches for clinical studies
3. AcademicResearchAgent - ArXiv searches for statistical methods
4. ResearchWritingAgent - Literature synthesis and writing
5. ProjectTimelineAgent - Milestone tracking (Nov 2025 - June 2026)
6. DataAnalysisAgent - Statistical test selection and sample size
7. CitationValidationAgent - Evidence grading, retraction detection

Created: 2025-11-26
Last Modified: 2025-12-11
"""

__version__ = "1.1.0"

__all__ = [
    # Classes
    'BaseAgent',
    'NursingResearchAgent',
    'MedicalResearchAgent',
    'AcademicResearchAgent',
    'ResearchWritingAgent',
    'ProjectTimelineAgent',
    'DataAnalysisAgent',
    'CitationValidationAgent',
    # Factory functions
    'get_nursing_research_agent',
    'get_medical_research_agent',
    'get_academic_research_agent',
    'get_research_writing_agent',
    'get_project_timeline_agent',
    'get_data_analysis_agent',
    'get_citation_validation_agent',
]


# Note: Individual agents are imported from their respective modules
# Example: from agents.nursing_research_agent import NursingResearchAgent
#
# Preferred: Use factory functions for consistent access pattern
# Example: from agents.nursing_research_agent import get_nursing_research_agent
#          agent = get_nursing_research_agent()
#
# Or use the central registry:
# Example: from src.orchestration.agent_registry import get_agent
#          agent = get_agent('nursing_research')
