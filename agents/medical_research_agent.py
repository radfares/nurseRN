"""
Literature Synthesis Agent - Article Analysis and Synthesis
Specialized for synthesizing multiple research articles into structured comparisons
Perfect for creating literature review comparisons and identifying research gaps

REPURPOSED (2025-12-13):
- Converted from Medical Research Agent
- Now synthesizes 4+ articles instead of searching
- Outputs comparison tables, themes, gaps, evidence strength
- Temperature set to 0 (factual synthesis only)
- Strict grounding enforcement (no invented article data)

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
PHASE 2 COMPLETE (2025-11-23): Refactored to use BaseAgent inheritance
"""

import os
import re
import sys
import time
import traceback
from textwrap import dedent
from typing import Any, Dict, List, Optional

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

# Import centralized configuration
from agent_config import get_db_path

from pydantic import BaseModel, ConfigDict, Field

# Import BaseAgent for inheritance pattern
from agents.base_agent import BaseAgent

# Import resilience infrastructure
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Import audit logging
from src.services.agent_audit_logger import get_audit_logger
# Import tools and API utilities
from src.services.api_tools import (
    build_tools_list,
    create_pubmed_tools_safe,
    get_api_status,
)
from src.tools.literature_tools import LiteratureTools
from src.tools.document_synthesis_tools import create_document_synthesis_tools_safe


# =============================================================================
# STRUCTURED OUTPUT SCHEMAS FOR FILE-BASED SYNTHESIS
# =============================================================================
# OpenAI strict mode requirements:
#   1. ALL fields required (no defaults)
#   2. NO Dict types (use explicit models instead)
#   3. additionalProperties: false on all objects
# =============================================================================


class DocumentSource(BaseModel):
    """Source document metadata for tracking what was analyzed."""
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File extension (pdf, docx, txt, etc.)")
    page_count: int = Field(..., description="Number of pages or sections")
    word_count: int = Field(..., description="Approximate word count")

    model_config = ConfigDict(extra="forbid")


class ArticleComparison(BaseModel):
    """Enhanced comparison row with quality scoring."""
    article_title: str = Field(..., description="Title or filename of the document")
    authors: str = Field(..., description="Authors if found, else 'Not specified'")
    year: str = Field(..., description="Publication year if found, else 'Unknown'")
    sample_size: str = Field(..., description="Sample size or 'N/A'")
    method: str = Field(..., description="Study methodology (RCT, cohort, review, etc.)")
    key_finding: str = Field(..., description="Primary finding or conclusion")
    quality_score: str = Field(..., description="High, Medium, or Low based on methodology")
    quality_rationale: str = Field(..., description="Brief explanation of quality rating")

    model_config = ConfigDict(extra="forbid")


class Contradiction(BaseModel):
    """Detected contradiction or disagreement between documents."""
    topic: str = Field(..., description="The specific topic of disagreement")
    document_a: str = Field(..., description="First document's position with source name")
    document_b: str = Field(..., description="Second document's position with source name")
    significance: str = Field(..., description="High, Medium, or Low impact on conclusions")

    model_config = ConfigDict(extra="forbid")


class ExtractedCitation(BaseModel):
    """Citation or reference found within a document."""
    citation_text: str = Field(..., description="Full citation text as written")
    source_document: str = Field(..., description="Document filename containing this citation")
    citation_type: str = Field(..., description="Journal, Book, Website, Report, or Unknown")

    model_config = ConfigDict(extra="forbid")


class SynthesisResult(BaseModel):
    """
    Enhanced structured output for file-based literature synthesis.

    Supports:
    - Document inventory tracking
    - Quality-scored comparisons
    - Contradiction detection
    - Citation extraction
    - Actionable recommendations
    """
    # Document inventory
    documents_analyzed: List[DocumentSource] = Field(..., description="All documents processed")

    # Core synthesis
    comparison_table: List[ArticleComparison] = Field(..., description="Side-by-side document comparison")
    themes: List[str] = Field(..., description="Common themes across documents")
    gaps: List[str] = Field(..., description="Research gaps or missing perspectives")

    # Evidence strength
    strong_evidence_count: int = Field(..., description="High-quality studies (RCTs, systematic reviews)")
    moderate_evidence_count: int = Field(..., description="Moderate-quality (cohort, case-control)")
    weak_evidence_count: int = Field(..., description="Low-quality (case series, opinion, grey lit)")

    # New analysis features
    contradictions: List[Contradiction] = Field(..., description="Conflicting findings between documents")
    extracted_citations: List[ExtractedCitation] = Field(..., description="References found in documents")

    # Summary and next steps
    synthesis_statement: str = Field(..., description="2-3 sentence overall summary")
    recommendations: List[str] = Field(..., description="Actionable next steps based on synthesis")

    model_config = ConfigDict(extra="forbid")


class LiteratureSynthesisAgent(BaseAgent):
    """
    Document Synthesis Agent - Synthesizes user-provided documents.

    REDESIGNED (2025-12-13):
    - File-based synthesis: Drop in any number of documents
    - Supports: PDF, DOCX, TXT, MD, PPTX, CSV, JSON
    - Two input methods: Direct file paths OR indexed library search
    - Enhanced analysis: Contradictions, citations, quality scoring
    - No minimum article requirement

    SYNTHESIS FEATURES:
    - Comparison tables with quality scoring
    - Theme identification across documents
    - Research gap analysis
    - Contradiction detection between sources
    - Citation extraction from documents
    - Actionable recommendations
    """

    def __init__(self):
        tools = self._create_tools()
        super().__init__(
            agent_name="Document Synthesis Agent",
            agent_key="document_synthesis",
            tools=tools,
        )
        # Initialize audit logger
        self.audit_logger = get_audit_logger(
            "document_synthesis", "Document Synthesis Agent"
        )

    def _create_tools(self) -> list:
        """Create tools for file-based document synthesis."""
        # ReasoningTools for analytical reasoning
        reasoning_tools = ReasoningTools(add_instructions=True)

        # DocumentSynthesisTools for loading files (PRIMARY TOOL)
        doc_synthesis = create_document_synthesis_tools_safe()
        if doc_synthesis:
            print("✅ Document Synthesis Tools available (load files, search library)")
        else:
            print("⚠️ Document Synthesis Tools unavailable")

        # LiteratureTools for saving findings to project database
        try:
            literature_tools = LiteratureTools()
            print("✅ LiteratureTools available (save findings to project DB)")
        except Exception as exc:
            literature_tools = None
            print(f"⚠️ LiteratureTools unavailable: {exc}")

        # Optional: PubMed for supplementary searches
        pubmed_tool = create_pubmed_tools_safe(required=False)
        if pubmed_tool:
            print("✅ PubMed search available (supplementary)")

        # Build tools list - DocumentSynthesisTools is primary
        tools = build_tools_list(
            reasoning_tools,
            doc_synthesis,      # PRIMARY: File loading
            literature_tools,   # Save findings
            pubmed_tool,        # Supplementary search
        )

        if not doc_synthesis:
            print("❌ Document synthesis tools unavailable! Agent will have limited functionality.")

        return tools

    def _create_agent(self) -> Agent:
        """Create and configure the Document Synthesis Agent."""
        return Agent(
            name="Document Synthesis Agent",
            role="Synthesize user-provided documents into comprehensive analysis",
            model=OpenAIChat(
                id="gpt-4o",
                temperature=0,  # Factual synthesis only
            ),
            reasoning=True,
            reasoning_model=OpenAIChat(id="gpt-4o", max_tokens=2000),
            reasoning_max_steps=5,
            tool_call_limit=10,  # More tool calls for file loading
            tools=self.tools,
            # NOTE: output_schema removed for flexibility with file-based synthesis
            # The agent uses structured prompts instead
            description=dedent("""\
                You are a Document Synthesis Specialist for research.
                You analyze user-provided documents (any number) and create
                comprehensive synthesis with comparison tables, themes,
                contradictions, and actionable recommendations.
                """),
            instructions=dedent("""\
                DOCUMENT SYNTHESIS SPECIALIST
                =============================

                YOUR JOB: Synthesize user-provided documents into structured analysis

                INPUT METHODS (use the appropriate tool):
                =========================================
                1. FILE PATHS: User provides paths like "/path/to/doc1.pdf, /path/to/doc2.pdf"
                   → Use load_files_for_synthesis() tool

                2. LIBRARY SEARCH: User asks to synthesize from their library
                   → Use search_library_for_synthesis() tool

                3. MIXED: User provides files AND asks to include library docs
                   → Use both tools

                SUPPORTED FILE TYPES:
                ====================
                PDF, DOCX, TXT, MD, PPTX, CSV, JSON

                REQUIRED OUTPUT FORMAT:
                ======================

                ## DOCUMENTS ANALYZED
                List each document with filename, type, and word count.

                ## COMPARISON TABLE
                | Document | Authors | Year | Sample Size | Method | Key Finding | Quality |
                |----------|---------|------|-------------|--------|-------------|---------|

                Quality: Rate each as High/Medium/Low with brief rationale

                ## COMMON THEMES
                - Theme 1: [Finding that appears across multiple documents]
                - Theme 2: [Common methodology or approach]
                - Theme 3: [Shared population or setting]

                ## CONTRADICTIONS FOUND
                For each contradiction:
                - Topic: [What they disagree about]
                - Document A says: [Position from first source]
                - Document B says: [Position from second source]
                - Significance: High/Medium/Low

                ## RESEARCH GAPS
                - Gap 1: [What's missing from this body of work]
                - Gap 2: [Unstudied populations or settings]
                - Gap 3: [Methodological limitations]

                ## EVIDENCE STRENGTH
                - Strong (RCTs, systematic reviews, meta-analyses): X documents
                - Moderate (cohort, case-control, quality guidelines): X documents
                - Weak (case series, opinion, grey literature): X documents

                ## CITATIONS FOUND
                List key references extracted from the documents.

                ## SYNTHESIS STATEMENT
                2-3 sentences summarizing the collective evidence.

                ## RECOMMENDATIONS
                - Recommendation 1: [Actionable next step]
                - Recommendation 2: [Further research needed]
                - Recommendation 3: [Practice implication]

                QUALITY SCORING RUBRIC:
                =======================
                HIGH:
                - Randomized controlled trials (RCTs)
                - Systematic reviews with meta-analysis
                - Large sample sizes (n > 500)
                - Peer-reviewed, high-impact journals
                - Clear methodology

                MEDIUM:
                - Cohort or case-control studies
                - Narrative reviews from reputable sources
                - Moderate sample sizes (n = 100-500)
                - Clinical guidelines from professional bodies

                LOW:
                - Case series or case reports (n < 30)
                - Opinion pieces or editorials
                - Grey literature (white papers, reports)
                - Unclear or weak methodology
                - Potential conflicts of interest

                ABSOLUTE GROUNDING RULES:
                ========================
                1. ONLY analyze content from provided documents
                2. DO NOT invent findings, statistics, or citations
                3. If information is missing, say "Not specified in documents"
                4. Quote or paraphrase directly from document content
                5. Always attribute claims to specific source documents

                CONTRADICTION DETECTION:
                =======================
                Look for:
                - Conflicting statistics or outcomes
                - Opposing recommendations
                - Different conclusions from similar studies
                - Methodological disagreements

                CITATION EXTRACTION:
                ===================
                Look for:
                - References sections
                - In-text citations (Author, Year)
                - Bibliography entries
                - Footnotes with sources
                """),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True,
            db=SqliteDb(db_file=get_db_path("document_synthesis")),
        )

    @staticmethod
    def _build_full_query(query: str, file_paths: Optional[List[str]]) -> str:
        if file_paths:
            paths_str = ", ".join(file_paths)
            return f"{query}\n\nFiles to synthesize: {paths_str}"
        return query

    @staticmethod
    def _extract_response_text(run_output: Any) -> str:
        return str(run_output.content if hasattr(run_output, "content") else run_output)

    @staticmethod
    def _duration_ms(start_time: float) -> int:
        return int((time.time() - start_time) * 1000)

    def _new_session_id(self) -> str:
        return f"doc_synthesis_{int(time.time() * 1000)}"

    def synthesize(
        self,
        query: str,
        file_paths: Optional[List[str]] = None,
        project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for document synthesis.

        Synthesizes documents from:
        1. Direct file paths provided
        2. Library search based on query
        3. Both combined

        Args:
            query: Synthesis query or instructions
            file_paths: Optional list of file paths to synthesize
            project_name: Associated project for context

        Returns:
            Synthesis results with content and metadata
        """
        start_time = time.time()
        session_id = self._new_session_id()

        try:
            # Input validation
            if not query or not isinstance(query, str):
                return {
                    "content": "Please provide a synthesis query or instructions.",
                    "success": False,
                    "error": "invalid_input"
                }

            # Set audit context
            self.audit_logger.set_session(session_id, project_name)
            self.audit_logger.log_query_received(query, project_name)

            full_query = self._build_full_query(query, file_paths)

            # Run agent
            run_output = self.agent.run(full_query)
            response_text = self._extract_response_text(run_output)

            # Extract document sources from tool results
            documents_used = self._extract_documents_from_output(run_output)

            duration_ms = self._duration_ms(start_time)

            # Log response
            self.audit_logger.log_response_generated(
                response=response_text,
                response_type="synthesis",
                validation_passed=True,
                duration_ms=duration_ms,
            )

            return {
                "content": response_text,
                "success": True,
                "documents_used": documents_used,
                "duration_ms": duration_ms,
            }

        except Exception as e:
            duration_ms = self._duration_ms(start_time)
            self.audit_logger.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
            )
            return {
                "content": f"Error during synthesis: {str(e)}",
                "success": False,
                "error": str(e),
                "duration_ms": duration_ms,
            }

    def run_with_grounding_check(
        self, query: str, project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Backward-compatible alias for synthesize().

        Kept for compatibility with existing code that uses this method.
        """
        return self.synthesize(query, project_name=project_name)

    def _extract_documents_from_output(self, run_output: Any) -> List[str]:
        """
        Extract document filenames from tool results.

        Args:
            run_output: The RunOutput object from agent.run()

        Returns:
            List of document filenames that were processed
        """
        documents = []

        try:
            if not hasattr(run_output, "messages") or not run_output.messages:
                return documents

            for message in run_output.messages:
                message_str = str(message)

                # Look for filename patterns in tool results
                # Pattern: "filename": "something.pdf"
                filename_matches = re.findall(
                    r'"filename":\s*"([^"]+)"',
                    message_str
                )
                documents.extend(filename_matches)

        except Exception as e:
            self.audit_logger.log_error(
                error_type="DocumentExtractionError",
                error_message=f"Failed to extract documents: {str(e)}",
            )

        return list(set(documents))  # Deduplicate

    def print_response(self, query: str, project_name: Optional[str] = None, stream: bool = False) -> None:
        """
        Interactive UI adapter for synthesis.

        Args:
            query: User's query
            project_name: Associated project for context
            stream: Whether to stream the response
        """
        try:
            result = self.synthesize(query, project_name=project_name)
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
            return

        content = result.get("content") if isinstance(result, dict) else str(result)
        success = result.get("success", True) if isinstance(result, dict) else True

        if not success:
            print(f"Synthesis failed: {result.get('error', 'unknown')}")

        print(content if content else "(no content returned)")

    def show_usage_examples(self):
        """Display usage examples for the Document Synthesis Agent."""
        api_status = get_api_status()

        print("\n" + "=" * 60)
        print("DOCUMENT SYNTHESIS AGENT")
        print("=" * 60)

        print("\n API STATUS:")
        if api_status["openai"]["key_set"]:
            print("  OpenAI API - Configured")
        else:
            print("  OpenAI API - NOT configured (required)")

        print("\n SUPPORTED FILES:")
        print("  PDF, DOCX, TXT, MD, PPTX, CSV, JSON")

        print("\n FEATURES:")
        print("  - Comparison tables with quality scoring")
        print("  - Theme identification across documents")
        print("  - Contradiction detection between sources")
        print("  - Citation extraction from documents")
        print("  - Research gap analysis")
        print("  - Actionable recommendations")

        print("\n EXAMPLE QUERIES:")
        print('  1. "Synthesize /path/to/doc1.pdf, /path/to/doc2.pdf"')
        print('  2. "Synthesize articles about fall prevention from my library"')
        print('  3. "Compare these files and find contradictions"')
        print('  4. "What themes are common across my indexed documents?"')

        print("\n TO ADD DOCUMENTS TO LIBRARY:")
        print("  python scripts/ingest_documents.py add /path/to/file.pdf")
        print("  python scripts/ingest_documents.py add-folder /path/to/docs/")

        print("=" * 60 + "\n")


# =============================================================================
# GLOBAL INSTANCE AND GETTERS
# =============================================================================

_document_synthesis_agent_instance: Optional["LiteratureSynthesisAgent"] = None
_medical_research_agent_instance: Optional["LiteratureSynthesisAgent"] = None


def get_document_synthesis_agent() -> Optional["LiteratureSynthesisAgent"]:
    """
    Return the Document Synthesis Agent instance with lazy initialization.
    """
    global _document_synthesis_agent_instance, _medical_research_agent_instance
    if _document_synthesis_agent_instance is None:
        try:
            _document_synthesis_agent_instance = LiteratureSynthesisAgent()
            _medical_research_agent_instance = _document_synthesis_agent_instance
        except Exception as _init_error:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to initialize Document Synthesis Agent: {_init_error}")
            return None
    return _document_synthesis_agent_instance


# Backward compatibility aliases
def get_literature_synthesis_agent() -> Optional["LiteratureSynthesisAgent"]:
    """Alias for get_document_synthesis_agent()."""
    return get_document_synthesis_agent()


def get_medical_research_agent() -> Optional["LiteratureSynthesisAgent"]:
    """DEPRECATED: Use get_document_synthesis_agent() instead."""
    return get_document_synthesis_agent()


# Backward compatibility alias for class name
MedicalResearchAgent = LiteratureSynthesisAgent


# Exports
__all__ = [
    "LiteratureSynthesisAgent",
    "MedicalResearchAgent",  # Backward compatibility alias
    "get_document_synthesis_agent",
    "get_literature_synthesis_agent",
    "get_medical_research_agent",
    "SynthesisResult",
    "ArticleComparison",
    "DocumentSource",
    "Contradiction",
    "ExtractedCitation",
]


if __name__ == "__main__":
    agent = get_document_synthesis_agent()
    if agent is not None:
        agent.show_usage_examples()
    else:
        print("Agent failed to initialize. Check logs for details.")
