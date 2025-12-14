"""
Document Reader Service with Circuit Breaker Protection
Integrates document reader tools with the nurseRN service layer.

Created: 2025-12-11
Updated: 2025-12-11 - Integrated with global circuit breakers
Updated: 2025-12-12 - Made project context optional for agent integration
Purpose: Provide resilient document reading capabilities with error handling
"""

import logging
from typing import Optional, List
from pybreaker import CircuitBreakerError
from src.services.circuit_breaker import (
    PDF_READER_BREAKER,
    PPTX_READER_BREAKER,
    WEBSITE_READER_BREAKER,
    TAVILY_READER_BREAKER,
    WEB_SEARCH_READER_BREAKER,
    ARXIV_READER_BREAKER,
    CSV_READER_BREAKER,
    JSON_READER_BREAKER,
)
from src.tools.readers_tools.document_reader_tools import DocumentReaderTools
from project_manager import get_project_manager

logger = logging.getLogger(__name__)


def create_document_reader_tools_safe(
    project_name: Optional[str] = None,
    project_db_path: Optional[str] = None,
    required: bool = False
) -> Optional[DocumentReaderTools]:
    """
    Create DocumentReaderTools with circuit breaker protection.

    This wraps all document reader methods with circuit breakers to prevent
    cascading failures when external services (Tavily, web requests) fail.

    Args:
        project_name: Name of the active project (or None to use active project)
        project_db_path: Path to project database (or None to get from project manager)
        required: If True, raises exception on failure. If False, returns None.

    Returns:
        DocumentReaderTools instance with circuit breaker protection, or None if creation fails and not required

    Raises:
        RuntimeError: If required=True and document readers cannot be initialized
    """
    try:
        # Get project context if not provided
        pm = get_project_manager()
        if project_name is None:
            project_name = pm.get_active_project() or "default_project"
        if project_db_path is None:
            project_db_path = pm.get_project_db_path() if pm.get_active_project() else ""

        # Create base tools
        tools = DocumentReaderTools(
            project_name=project_name,
            project_db_path=project_db_path
        )
    except Exception as e:
        logger.warning(f"Document reader tools creation failed: {e}")
        if required:
            raise RuntimeError(f"Document reader tools initialization failed: {e}") from e
        return None

    # Use global circuit breakers (configured in src/services/circuit_breaker.py)
    pdf_breaker = PDF_READER_BREAKER
    pptx_breaker = PPTX_READER_BREAKER
    website_breaker = WEBSITE_READER_BREAKER
    tavily_breaker = TAVILY_READER_BREAKER
    web_search_breaker = WEB_SEARCH_READER_BREAKER
    arxiv_breaker = ARXIV_READER_BREAKER
    csv_breaker = CSV_READER_BREAKER
    json_breaker = JSON_READER_BREAKER
    
    # Wrap methods with circuit breakers
    original_read_pdf = tools.read_pdf
    original_read_pdf_password = tools.read_pdf_with_password
    original_read_pptx = tools.read_pptx
    original_read_website = tools.read_website
    original_extract_url = tools.extract_url_content
    original_search = tools.search_and_extract
    original_search_arxiv = tools.search_arxiv
    original_read_csv = tools.read_csv
    original_read_json = tools.read_json
    
    def safe_read_pdf(file_path: str) -> str:
        try:
            return pdf_breaker.call(original_read_pdf, file_path)
        except CircuitBreakerError:
            logger.error("PDF reader circuit breaker open - too many failures")
            return "Error: PDF reading service temporarily unavailable. Please try again later."
        except Exception as e:
            logger.error(f"Error in safe_read_pdf: {e}", exc_info=True)
            return f"Error reading PDF: {str(e)}"
    
    def safe_read_pdf_password(file_path: str, password: str) -> str:
        try:
            return pdf_breaker.call(original_read_pdf_password, file_path, password)
        except CircuitBreakerError:
            logger.error("PDF reader circuit breaker open")
            return "Error: PDF reading service temporarily unavailable."
        except Exception as e:
            logger.error(f"Error in safe_read_pdf_password: {e}", exc_info=True)
            return f"Error reading protected PDF: {str(e)}"
    
    def safe_read_pptx(file_path: str) -> str:
        try:
            return pptx_breaker.call(original_read_pptx, file_path)
        except CircuitBreakerError:
            logger.error("PPTX reader circuit breaker open")
            return "Error: PPTX reading service temporarily unavailable."
        except Exception as e:
            logger.error(f"Error in safe_read_pptx: {e}", exc_info=True)
            return f"Error reading PPTX: {str(e)}"
    
    def safe_read_website(url: str) -> str:
        try:
            return website_breaker.call(original_read_website, url)
        except CircuitBreakerError:
            logger.error("Website reader circuit breaker open")
            return "Error: Website reading service temporarily unavailable."
        except Exception as e:
            logger.error(f"Error in safe_read_website: {e}", exc_info=True)
            return f"Error reading website: {str(e)}"
    
    def safe_extract_url(url: str, format: str) -> str:
        # OpenAI requires all parameters in 'required' array, so no defaults in signature
        format = format or "markdown"  # Handle empty string or None
        try:
            return tavily_breaker.call(original_extract_url, url, format)
        except CircuitBreakerError:
            logger.error("Tavily reader circuit breaker open")
            return "Error: Content extraction service temporarily unavailable."
        except Exception as e:
            logger.error(f"Error in safe_extract_url: {e}", exc_info=True)
            return f"Error extracting content: {str(e)}"
    
    def safe_search(query: str, max_results: int = 5, search_engine: str = "duckduckgo") -> str:
        try:
            return web_search_breaker.call(original_search, query, max_results, search_engine)
        except CircuitBreakerError:
            logger.error("Web search circuit breaker open")
            return "Error: Web search service temporarily unavailable."
        except Exception as e:
            logger.error(f"Error in safe_search: {e}", exc_info=True)
            return f"Error performing search: {str(e)}"

    def safe_search_arxiv(topics: List[str], max_results: int = 5) -> str:
        try:
            return arxiv_breaker.call(original_search_arxiv, topics, max_results)
        except CircuitBreakerError:
            logger.error("ArXiv reader circuit breaker open")
            return "Error: ArXiv search service temporarily unavailable."
        except Exception as e:
            logger.error(f"Error in safe_search_arxiv: {e}", exc_info=True)
            return f"Error searching ArXiv: {str(e)}"

    def safe_read_csv(file_path: str) -> str:
        try:
            return csv_breaker.call(original_read_csv, file_path)
        except CircuitBreakerError:
            logger.error("CSV reader circuit breaker open")
            return "Error: CSV reading service temporarily unavailable."
        except Exception as e:
            logger.error(f"Error in safe_read_csv: {e}", exc_info=True)
            return f"Error reading CSV: {str(e)}"

    def safe_read_json(file_path: str) -> str:
        try:
            return json_breaker.call(original_read_json, file_path)
        except CircuitBreakerError:
            logger.error("JSON reader circuit breaker open")
            return "Error: JSON reading service temporarily unavailable."
        except Exception as e:
            logger.error(f"Error in safe_read_json: {e}", exc_info=True)
            return f"Error reading JSON: {str(e)}"
    
    # Replace methods with safe versions
    tools.read_pdf = safe_read_pdf
    tools.read_pdf_with_password = safe_read_pdf_password
    tools.read_pptx = safe_read_pptx
    tools.read_website = safe_read_website
    tools.extract_url_content = safe_extract_url
    tools.search_and_extract = safe_search
    tools.search_arxiv = safe_search_arxiv
    tools.read_csv = safe_read_csv
    tools.read_json = safe_read_json

    logger.info(f"Document reader tools created with circuit breaker protection (project: {project_name})")
    return tools
