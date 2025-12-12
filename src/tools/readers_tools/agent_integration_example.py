"""
Agent Integration Examples for Document Reader Tools
Shows how to add document reading capabilities to existing agents.

Created: 2025-12-11
Purpose: Demonstrate integration patterns for document reader tools
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.tools.document_reader_service import create_document_reader_tools_safe


# Example 1: Add to Nursing Research Agent
def create_nursing_research_agent_with_docs(project_name: str, project_db_path: str):
    """
    Create nursing research agent with document reading capabilities.
    """
    # Create document reader tools
    doc_tools = create_document_reader_tools_safe(
        project_name=project_name,
        project_db_path=project_db_path
    )
    
    # Create agent with document tools
    agent = Agent(
        name="Nursing Research Agent with Document Reading",
        model=OpenAIChat(id="gpt-4o"),
        tools=[doc_tools],
        instructions=[
            "You are a nursing research assistant specializing in evidence-based practice.",
            "You can read PDF research articles, PowerPoint presentations, and websites.",
            "Use the document reader tools to extract information from research materials.",
            "Always cite sources when using extracted content.",
        ],
        markdown=True,
        show_tool_calls=True
    )
    
    return agent


# Example 2: Add to Medical Research Agent
def create_medical_research_agent_with_docs(project_name: str, project_db_path: str):
    """
    Create medical research agent with document reading capabilities.
    """
    doc_tools = create_document_reader_tools_safe(
        project_name=project_name,
        project_db_path=project_db_path
    )
    
    agent = Agent(
        name="Medical Research Agent with Document Reading",
        model=OpenAIChat(id="gpt-4o"),
        tools=[doc_tools],
        instructions=[
            "You are a medical research specialist focused on clinical studies.",
            "You can read research PDFs, extract content from medical websites, and search for articles.",
            "Use document reader tools to access full-text articles when PMIDs are not sufficient.",
            "Validate information from multiple sources.",
        ],
        markdown=True,
        show_tool_calls=True
    )
    
    return agent


# Example 3: Standalone Document Analysis Agent
def create_document_analysis_agent(project_name: str, project_db_path: str):
    """
    Create specialized agent for document analysis and extraction.
    """
    doc_tools = create_document_reader_tools_safe(
        project_name=project_name,
        project_db_path=project_db_path
    )
    
    agent = Agent(
        name="Document Analysis Agent",
        model=OpenAIChat(id="gpt-4o"),
        tools=[doc_tools],
        instructions=[
            "You are a document analysis specialist.",
            "You can read PDFs, PowerPoint presentations, websites, and perform web searches.",
            "Extract key information, summarize content, and identify important findings.",
            "When analyzing research articles, focus on:",
            "  - Study design and methodology",
            "  - Sample size and population",
            "  - Key findings and results",
            "  - Limitations and implications",
            "  - Evidence level and quality",
        ],
        markdown=True,
        show_tool_calls=True
    )
    
    return agent


# Example 4: Usage in Existing Agent
def add_document_tools_to_existing_agent(
    agent: Agent,
    project_name: str,
    project_db_path: str
) -> Agent:
    """
    Add document reader tools to an existing agent.
    
    Args:
        agent: Existing agent instance
        project_name: Project name
        project_db_path: Project database path
    
    Returns:
        Agent with document tools added
    """
    # Create document tools
    doc_tools = create_document_reader_tools_safe(
        project_name=project_name,
        project_db_path=project_db_path
    )
    
    # Add to agent's tools
    if agent.tools is None:
        agent.tools = [doc_tools]
    else:
        agent.tools.append(doc_tools)
    
    # Update instructions
    additional_instructions = [
        "You now have access to document reading tools.",
        "You can read PDFs, PowerPoint files, websites, and perform web searches.",
        "Use these tools to access research materials and extract information.",
    ]
    
    if agent.instructions is None:
        agent.instructions = additional_instructions
    else:
        agent.instructions.extend(additional_instructions)
    
    return agent


# Example 5: Usage Patterns
def example_usage():
    """
    Example usage patterns for document reader tools.
    """
    project_name = "Fall Prevention Study"
    project_db_path = "data/projects/fall_prevention_study/fall_prevention_study.db"
    
    # Create agent with document tools
    agent = create_document_analysis_agent(project_name, project_db_path)
    
    # Example 1: Read a local PDF
    response = agent.run(
        "Read the PDF at data/research/cameron_2018_falls.pdf and summarize the key findings."
    )
    print(response.content)
    
    # Example 2: Read a website
    response = agent.run(
        "Read the CDC fall prevention guidelines at https://www.cdc.gov/falls/index.html "
        "and extract the main recommendations."
    )
    print(response.content)
    
    # Example 3: Search and extract
    response = agent.run(
        "Search for 'multifactorial fall prevention programs in hospitals' and "
        "summarize the top 3 results."
    )
    print(response.content)
    
    # Example 4: Extract from specific URL
    response = agent.run(
        "Extract content from https://www.jointcommission.org/standards/standard-faqs/hospital-and-hospital-clinics/national-patient-safety-goals-npsg/000001688/ "
        "and summarize the fall prevention requirements."
    )
    print(response.content)
    
    # Example 5: Read PowerPoint
    response = agent.run(
        "Read the PowerPoint presentation at data/presentations/fall_prevention_training.pptx "
        "and create a summary of the training content."
    )
    print(response.content)


# Example 6: Integration with Existing Nursing Research Agent
def integrate_with_nursing_research_agent():
    """
    Show how to integrate document tools with existing nursing research agent.
    """
    from agents.nursing_research_agent import nursing_research_agent
    from project_manager import get_project_manager
    
    # Get active project
    pm = get_project_manager()
    project_name = pm.get_active_project()
    project_db_path = pm.get_project_db_path()
    
    # Add document tools to existing agent
    enhanced_agent = add_document_tools_to_existing_agent(
        agent=nursing_research_agent,
        project_name=project_name,
        project_db_path=project_db_path
    )
    
    # Now the agent can use document reading capabilities
    response = enhanced_agent.run(
        "Read the fall prevention guideline PDF in data/guidelines/ and "
        "compare it with current research on multifactorial interventions."
    )
    
    return response


if __name__ == "__main__":
    # Run example usage
    example_usage()
