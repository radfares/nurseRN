"""
Document Reader Tools for Nursing Research
Integrated PDF, PPTX, and Web reading capabilities with circuit breaker protection.

Created: 2025-12-11
Updated: 2025-12-12 - Fixed module-level imports to be lazy for optional dependencies
Purpose: Enable agents to read and extract information from research documents
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from agno.tools import Toolkit

# Import core readers that should always work
try:
    from agno.knowledge.reader.pdf_reader import PDFReader
    PDF_READER_AVAILABLE = True
except ImportError:
    PDF_READER_AVAILABLE = False
    PDFReader = None

try:
    from agno.knowledge.reader.website_reader import WebsiteReader
    WEBSITE_READER_AVAILABLE = True
except ImportError:
    WEBSITE_READER_AVAILABLE = False
    WebsiteReader = None

try:
    from agno.knowledge.reader.web_search_reader import WebSearchReader
    WEB_SEARCH_READER_AVAILABLE = True
except ImportError:
    WEB_SEARCH_READER_AVAILABLE = False
    WebSearchReader = None

# Import chunking
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.chunking.row import RowChunking

# Lazy imports for optional dependencies (will import when needed)
# This prevents import failures when tavily-python or python-pptx are not installed

logger = logging.getLogger(__name__)


class DocumentReaderTools(Toolkit):
    """
    Toolkit for reading and extracting content from various document formats.
    
    Capabilities:
    - Read PDF files (local and password-protected)
    - Read PowerPoint presentations
    - Read website content
    - Extract content from URLs using Tavily
    - Perform web searches and extract results
    
    Use Cases for Nursing Research:
    - Extract text from research PDFs
    - Read guidelines from healthcare websites
    - Search for recent articles and extract content
    - Process presentation materials
    """
    
    def __init__(
        self,
        project_name: str,
        project_db_path: str,
        tavily_api_key: Optional[str] = None,
        semantic_similarity_threshold: float = 0.5,
    ):
        """
        Initialize document reader tools.
        
        Args:
            project_name: Name of the active project
            project_db_path: Path to project database
            tavily_api_key: Optional Tavily API key for web extraction
        """
        super().__init__(name="document_reader_tools")
        
        self.project_name = project_name
        self.project_db_path = project_db_path
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")

        # Initialize chunking strategies
        self.semantic_chunking = SemanticChunking(similarity_threshold=semantic_similarity_threshold)
        self.row_chunking = RowChunking()

        # Initialize core readers (always available)
        if PDF_READER_AVAILABLE:
            self.pdf_reader = PDFReader(chunking_strategy=self.semantic_chunking)
        else:
            self.pdf_reader = None
            logger.warning("PDF reader unavailable: pypdf package not installed")
            
        if WEBSITE_READER_AVAILABLE:
            self.website_reader = WebsiteReader(chunking_strategy=self.semantic_chunking)
        else:
            self.website_reader = None
            logger.warning("Website reader unavailable: beautifulsoup4 package not installed")

        # Initialize PPTX reader (optional - requires python-pptx)
        try:
            from agno.knowledge.reader.pptx_reader import PPTXReader
            self.pptx_reader = PPTXReader(chunking_strategy=self.semantic_chunking)
        except ImportError as e:
            self.pptx_reader = None
            logger.warning(f"PPTX reader unavailable: {e}")

        # Initialize ArXiv reader (optional)
        try:
            from agno.knowledge.reader.arxiv_reader import ArxivReader
            self.arxiv_reader = ArxivReader(chunking_strategy=self.semantic_chunking)
        except ImportError as e:
            self.arxiv_reader = None
            logger.warning(f"ArXiv reader unavailable: {e}")

        # Initialize CSV reader (optional)
        try:
            from agno.knowledge.reader.csv_reader import CSVReader
            self.csv_reader = CSVReader(chunking_strategy=self.row_chunking)
        except ImportError as e:
            self.csv_reader = None
            logger.warning(f"CSV reader unavailable: {e}")

        # Initialize JSON reader (optional)
        try:
            from agno.knowledge.reader.json_reader import JSONReader
            self.json_reader = JSONReader()
        except ImportError as e:
            self.json_reader = None
            logger.warning(f"JSON reader unavailable: {e}")

        # Initialize Tavily reader if API key available (optional - requires tavily-python)
        self.tavily_reader = None
        if self.tavily_api_key:
            try:
                from agno.knowledge.reader.tavily_reader import TavilyReader
                extract_format = os.getenv("TAVILY_EXTRACT_FORMAT", "markdown")
                extract_depth = os.getenv("TAVILY_EXTRACT_DEPTH", "basic")
                self.tavily_reader = TavilyReader(
                    api_key=self.tavily_api_key,
                    extract_format=extract_format,
                    extract_depth=extract_depth,
                    chunk=True
                )
            except ImportError as e:
                logger.warning(f"Tavily reader unavailable: {e}")
        else:
            logger.info("Tavily API key not found - web extraction disabled")
        
        # Initialize web search defaults from environment
        try:
            default_max = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))
        except ValueError:
            default_max = 5
        default_engine = os.getenv("WEB_SEARCH_ENGINE", "duckduckgo")
        self._web_search_defaults = {"max_results": default_max, "search_engine": default_engine}
        
        # Register tools
        self.register(self.read_pdf)
        self.register(self.read_pdf_with_password)
        self.register(self.read_pptx)
        self.register(self.read_website)
        self.register(self.extract_url_content)
        self.register(self.search_and_extract)
        self.register(self.search_arxiv)
        self.register(self.read_csv)
        self.register(self.read_json)

    def _resolve_path(self, file_path: str) -> Path:
        """Resolve a file path relative to project root if not absolute."""
        path = Path(file_path)
        if path.is_absolute():
            return path
        # Try relative to project root inferred from DB path
        project_root = Path(self.project_db_path).parent.parent.parent
        return project_root / file_path
    
    def read_pdf(self, file_path: str) -> str:
        """
        Read and extract text from a PDF file.
        
        Args:
            file_path: Path to PDF file (absolute or relative to project)
        
        Returns:
            Extracted text content from the PDF
        
        Example:
            text = read_pdf("data/research_article.pdf")
        """
        if not PDF_READER_AVAILABLE or self.pdf_reader is None:
            return "Error: PDF reader unavailable - pypdf package not installed"
            
        try:
            # Resolve path
            path = self._resolve_path(file_path)
            
            if not path.exists():
                return f"Error: PDF file not found: {file_path}"
            
            # Read PDF
            documents = self.pdf_reader.read(str(path))
            
            if not documents:
                return "Error: No content extracted from PDF"
            
            # Combine all document content
            content = "\n\n".join([doc.content for doc in documents])
            
            logger.info(
                f"Successfully read PDF with semantic chunking: {file_path} "
                f"({len(documents)} chunks, {len(content)} chars)"
            )
            return content
            
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}", exc_info=True)
            return f"Error reading PDF: {str(e)}"
    
    def read_pdf_with_password(self, file_path: str, password: str) -> str:
        """
        Read and extract text from a password-protected PDF file.
        
        Args:
            file_path: Path to password-protected PDF file
            password: Password to decrypt the PDF
        
        Returns:
            Extracted text content from the PDF
        
        Example:
            text = read_pdf_with_password("data/confidential.pdf", "secret123")
        """
        if not PDF_READER_AVAILABLE:
            return "Error: PDF reader unavailable - pypdf package not installed"
            
        try:
            # Resolve path
            path = self._resolve_path(file_path)
            
            if not path.exists():
                return f"Error: PDF file not found: {file_path}"
            
            # Read password-protected PDF
            reader = PDFReader(password=password, chunking_strategy=self.semantic_chunking)
            documents = reader.read(str(path))
            
            if not documents:
                return "Error: No content extracted from PDF (wrong password?)"
            
            # Combine all document content
            content = "\n\n".join([doc.content for doc in documents])
            
            logger.info(f"Successfully read protected PDF: {file_path}")
            return content
            
        except Exception as e:
            logger.error(f"Error reading protected PDF {file_path}: {e}", exc_info=True)
            return f"Error reading protected PDF: {str(e)}"
    
    def read_pptx(self, file_path: str) -> str:
        """
        Read and extract text from a PowerPoint presentation.

        Args:
            file_path: Path to PPTX file

        Returns:
            Extracted text content from all slides

        Example:
            text = read_pptx("data/research_presentation.pptx")
        """
        if not self.pptx_reader:
            return "Error: PPTX reader unavailable. Install python-pptx: pip install python-pptx"

        try:
            # Resolve path
            path = self._resolve_path(file_path)
            
            if not path.exists():
                return f"Error: PPTX file not found: {file_path}"
            
            # Read PPTX
            documents = self.pptx_reader.read(str(path))
            
            if not documents:
                return "Error: No content extracted from PPTX"
            
            # Combine all slide content
            content = "\n\n".join([doc.content for doc in documents])
            
            logger.info(f"Successfully read PPTX: {file_path} ({len(content)} chars)")
            return content
            
        except Exception as e:
            logger.error(f"Error reading PPTX {file_path}: {e}", exc_info=True)
            return f"Error reading PPTX: {str(e)}"
    
    def read_website(self, url: str) -> str:
        """
        Read and extract text content from a website.
        
        Args:
            url: Website URL to read
        
        Returns:
            Extracted text content from the website
        
        Example:
            text = read_website("https://www.cdc.gov/hai/prevent/prevention.html")
        """
        if not WEBSITE_READER_AVAILABLE or self.website_reader is None:
            return "Error: Website reader unavailable - beautifulsoup4 package not installed"
            
        try:
            # Read website
            documents = self.website_reader.read(url)
            
            if not documents:
                return f"Error: No content extracted from {url}"
            
            # Combine all content
            content = "\n\n".join([doc.content for doc in documents])
            
            logger.info(f"Successfully read website: {url} ({len(content)} chars)")
            return content
            
        except Exception as e:
            logger.error(f"Error reading website {url}: {e}", exc_info=True)
            return f"Error reading website: {str(e)}"
    
    def extract_url_content(self, url: str, format: str = "markdown") -> str:
        """
        Extract content from a URL using Tavily (more comprehensive than basic website reading).
        
        Args:
            url: URL to extract content from
            format: Output format ("markdown" or "text")
        
        Returns:
            Extracted content in specified format
        
        Example:
            content = extract_url_content("https://www.jointcommission.org/standards/")
        
        Note:
            Requires TAVILY_API_KEY environment variable
        """
        if not self.tavily_reader:
            return "Error: Tavily API key not configured. Set TAVILY_API_KEY environment variable."
        
        try:
            # Update format if needed
            if format != self.tavily_reader.extract_format:
                try:
                    from agno.knowledge.reader.tavily_reader import TavilyReader
                    self.tavily_reader = TavilyReader(
                        api_key=self.tavily_api_key,
                        extract_format=format,
                        extract_depth="basic",
                        chunk=True
                    )
                except ImportError as e:
                    return f"Error: Tavily reader unavailable: {e}"

            # Extract content
            documents = self.tavily_reader.read(url)
            
            if not documents:
                return f"Error: No content extracted from {url}"
            
            # Combine all content
            content = "\n\n".join([doc.content for doc in documents])
            
            logger.info(f"Successfully extracted content from {url} ({len(content)} chars)")
            return content
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}", exc_info=True)
            return f"Error extracting content: {str(e)}"
    
    def search_and_extract(
        self, 
        query: str, 
        max_results: int = 5,
        search_engine: str = "duckduckgo"
    ) -> str:
        """
        Search the web and extract content from top results.
        
        Args:
            query: Search query
            max_results: Maximum number of results to extract (default: 5)
            search_engine: Search engine to use ("duckduckgo", "google", "bing")
        
        Returns:
            Combined extracted content from search results
        
        Example:
            content = search_and_extract("fall prevention in elderly patients", max_results=3)
        
        Use Cases:
            - Find recent articles on a topic
            - Get current guidelines and standards
            - Research best practices
        """
        if not WEB_SEARCH_READER_AVAILABLE:
            return "Error: Web search reader unavailable - ddgs package not installed"
            
        try:
            # Create reader with specified parameters (fall back to env defaults)
            reader = WebSearchReader(
                max_results=max_results or self._web_search_defaults["max_results"],
                search_engine=search_engine or self._web_search_defaults["search_engine"],
                chunk=True
            )
            
            # Perform search and extract
            documents = reader.read(query)
            
            if not documents:
                return f"No results found for query: {query}"
            
            # Combine all content with source URLs
            results = []
            for doc in documents:
                results.append(f"Source: {doc.name}\n{doc.content}")
            
            content = "\n\n" + "="*80 + "\n\n".join(results)
            
            logger.info(f"Search '{query}' returned {len(documents)} results ({len(content)} chars)")
            return content
            
        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}", exc_info=True)
            return f"Error performing search: {str(e)}"

    def search_arxiv(
        self,
        topics: List[str],
        max_results: int = 5
    ) -> str:
        """
        Search ArXiv for academic papers on specified topics.
        """
        if not self.arxiv_reader:
            return "Error: ArXiv reader unavailable. Check dependencies."

        try:
            documents = self.arxiv_reader.read(topics=topics, max_results=max_results)
            if not documents:
                return f"No ArXiv papers found for topics: {', '.join(topics)}"

            results = []
            for doc in documents:
                results.append(f"Paper: {doc.name}\n{doc.content}")
            content = "\n\n" + "="*80 + "\n\n".join(results)
            logger.info(f"ArXiv search returned {len(documents)} papers ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Error searching ArXiv: {e}", exc_info=True)
            return f"Error searching ArXiv: {str(e)}"

    def read_csv(self, file_path: str) -> str:
        """Read and parse a CSV data file."""
        if not self.csv_reader:
            return "Error: CSV reader unavailable. Check dependencies."

        try:
            path = self._resolve_path(file_path)
            if not path.exists():
                return f"Error: CSV file not found: {file_path}"

            documents = self.csv_reader.read(str(path))
            if not documents:
                return "Error: No content extracted from CSV"

            content = "\n\n".join([doc.content for doc in documents])
            logger.info(f"Successfully read CSV: {file_path} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Error reading CSV {file_path}: {e}", exc_info=True)
            return f"Error reading CSV: {str(e)}"

    def read_json(self, file_path: str) -> str:
        """Read and parse a JSON data file."""
        if not self.json_reader:
            return "Error: JSON reader unavailable. Check dependencies."

        try:
            path = self._resolve_path(file_path)
            if not path.exists():
                return f"Error: JSON file not found: {file_path}"

            documents = self.json_reader.read(str(path))
            if not documents:
                return "Error: No content extracted from JSON"

            content = "\n\n".join([doc.content for doc in documents])
            logger.info(f"Successfully read JSON: {file_path} ({len(content)} chars)")
            return content
        except Exception as e:
            logger.error(f"Error reading JSON {file_path}: {e}", exc_info=True)
            return f"Error reading JSON: {str(e)}"


def create_document_reader_tools(
    project_name: str,
    project_db_path: str
) -> DocumentReaderTools:
    """
    Factory function to create DocumentReaderTools instance.
    
    Args:
        project_name: Name of the active project
        project_db_path: Path to project database
    
    Returns:
        Configured DocumentReaderTools instance
    """
    return DocumentReaderTools(
        project_name=project_name,
        project_db_path=project_db_path
    )
