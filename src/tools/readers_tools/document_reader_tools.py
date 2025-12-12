"""
Document Reader Tools for Nursing Research
Integrated PDF, PPTX, and Web reading capabilities with circuit breaker protection.

Created: 2025-12-11
Purpose: Enable agents to read and extract information from research documents
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from agno.tools import Toolkit
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.reader.pptx_reader import PPTXReader
from agno.knowledge.reader.website_reader import WebsiteReader
from agno.knowledge.reader.tavily_reader import TavilyReader
from agno.knowledge.reader.web_search_reader import WebSearchReader
from agno.knowledge.reader.arxiv_reader import ArxivReader
from agno.knowledge.reader.csv_reader import CSVReader
from agno.knowledge.reader.json_reader import JSONReader

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
        tavily_api_key: Optional[str] = None
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
        
        # Initialize readers
        self.pdf_reader = PDFReader()
        self.pptx_reader = PPTXReader()
        self.website_reader = WebsiteReader()
        self.arxiv_reader = ArxivReader()
        self.csv_reader = CSVReader()
        self.json_reader = JSONReader()
        
        # Initialize Tavily reader if API key available
        if self.tavily_api_key:
            extract_format = os.getenv("TAVILY_EXTRACT_FORMAT", "markdown")
            extract_depth = os.getenv("TAVILY_EXTRACT_DEPTH", "basic")
            self.tavily_reader = TavilyReader(
                api_key=self.tavily_api_key,
                extract_format=extract_format,
                extract_depth=extract_depth,
                chunk=True
            )
        else:
            self.tavily_reader = None
            logger.warning("Tavily API key not found - web extraction disabled")
        
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
            
            logger.info(f"Successfully read PDF: {file_path} ({len(content)} chars)")
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
        try:
            # Resolve path
            path = self._resolve_path(file_path)
            
            if not path.exists():
                return f"Error: PDF file not found: {file_path}"
            
            # Read password-protected PDF
            reader = PDFReader(password=password)
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
                self.tavily_reader = TavilyReader(
                    api_key=self.tavily_api_key,
                    extract_format=format,
                    extract_depth="basic",
                    chunk=True
                )
            
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
