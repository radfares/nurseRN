"""
Nursing Research Agent System - Agent Module

This module contains all 6 specialized AI agents plus the base agent class.

Architecture:
- BaseAgent: Abstract base class providing common functionality
- 6 Specialized Agents: Each inherits from BaseAgent

Agents:
1. NursingResearchAgent - PICOT development, healthcare standards
2. MedicalResearchAgent - PubMed searches for clinical studies
3. AcademicResearchAgent - ArXiv searches for statistical methods
4. ResearchWritingAgent - Literature synthesis and writing
5. ProjectTimelineAgent - Milestone tracking (Nov 2025 - June 2026)
6. DataAnalysisAgent - Statistical test selection and sample size

Created: 2025-11-26
Last Modified: 2025-11-26
"""

__version__ = "1.0.0"

__all__ = [
    'BaseAgent',
    'NursingResearchAgent',
    'MedicalResearchAgent',
    'AcademicResearchAgent',
    'ResearchWritingAgent',
    'ProjectTimelineAgent',
    'DataAnalysisAgent',
    'CitationValidationAgent',
]


# Note: Individual agents are imported from their respective modules
# Example: from agents.nursing_research_agent import NursingResearchAgent
