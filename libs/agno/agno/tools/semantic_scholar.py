import json
import os
from typing import Any, Dict, List, Optional

import httpx

from agno.tools import Toolkit
from agno.utils.log import log_debug, logger


class SemanticScholarTools(Toolkit):
    """Toolkit for searching Semantic Scholar academic search engine."""

    def __init__(
        self,
        enable_search_semantic_scholar: bool = True,
        max_results: Optional[int] = 10,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        self.max_results: Optional[int] = max_results or 10
        self.api_key: Optional[str] = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")

        tools: List[Any] = []
        if enable_search_semantic_scholar:
            tools.append(self.search_semantic_scholar)

        super().__init__(name="semantic_scholar", tools=tools, **kwargs)

    def search_semantic_scholar(self, query: str, max_results: Optional[int] = None) -> str:
        """Use this function to search Semantic Scholar for academic papers.

        Args:
            query (str): The search query.
            max_results (int, optional): Maximum number of results to return. Defaults to 10.

        Returns:
            str: A JSON string containing the search results with paper details.
        """
        try:
            log_debug(f"Searching Semantic Scholar for: {query}")
            max_results = max_results or self.max_results or 10

            # Semantic Scholar API endpoint
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": query,
                "limit": min(max_results, 100),  # API limit
                "fields": "title,authors,year,abstract,venue,citationCount,referenceCount,url,doi,externalIds",
            }

            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key

            response = httpx.get(url, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            papers = []
            results = data.get("data", [])[:max_results]

            for paper in results:
                # Extract key information
                paper_id = paper.get("paperId", "N/A")
                title = paper.get("title", "No title available")
                authors = paper.get("authors", [])
                author_names = (
                    ", ".join([author.get("name", "") for author in authors[:5]]) if authors else "Not available"
                )
                if len(authors) > 5:
                    author_names += f" et al. ({len(authors)} total authors)"

                year = paper.get("year", "Unknown")
                venue = paper.get("venue", "Not specified")
                abstract = paper.get("abstract", "No abstract available")
                citation_count = paper.get("citationCount", 0)
                reference_count = paper.get("referenceCount", 0)
                url = paper.get("url", "Not available")
                doi = paper.get("doi", "Not available")
                external_ids = paper.get("externalIds", {})

                # Get PubMed ID if available
                pubmed_id = external_ids.get("PubMed", "Not available") if external_ids else "Not available"

                paper_data = {
                    "Paper_ID": paper_id,
                    "Title": title,
                    "Authors": author_names,
                    "Year": year,
                    "Venue": venue,
                    "Abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
                    "Citation_Count": citation_count,
                    "Reference_Count": reference_count,
                    "DOI": doi,
                    "PubMed_ID": pubmed_id,
                    "URL": url,
                }
                papers.append(paper_data)

            if not papers:
                return json.dumps({"message": "No papers found for the query.", "query": query})

            return json.dumps(papers, indent=2)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching Semantic Scholar: {e}")
            if e.response.status_code == 429:
                return json.dumps({"error": "rate_limit", "message": "Rate limit exceeded. Please try again later."})
            return json.dumps({"error": f"HTTP error: {e.response.status_code}", "message": "Could not fetch papers."})
        except httpx.TimeoutException:
            logger.error("Timeout searching Semantic Scholar")
            return json.dumps({"error": "timeout", "message": "Request to Semantic Scholar timed out."})
        except Exception as e:
            logger.error(f"Error searching Semantic Scholar: {e}", exc_info=True)
            return json.dumps({"error": str(e), "message": "Could not fetch papers."})
