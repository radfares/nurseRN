import json
import os
from typing import Any, Dict, List, Optional

import httpx

from agno.tools import Toolkit
from agno.utils.log import log_debug, logger


class CoreTools(Toolkit):
    """Toolkit for searching CORE (Connecting REpositories) open-access database."""

    def __init__(
        self,
        enable_search_core: bool = True,
        max_results: Optional[int] = 10,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        self.max_results: Optional[int] = max_results or 10
        self.api_key: Optional[str] = api_key or os.getenv("CORE_API_KEY")

        tools: List[Any] = []
        if enable_search_core:
            tools.append(self.search_core)

        super().__init__(name="core", tools=tools, **kwargs)

    def search_core(self, query: str, max_results: Optional[int] = None) -> str:
        """Use this function to search CORE for open-access research papers.

        Args:
            query (str): The search query.
            max_results (int, optional): Maximum number of results to return. Defaults to 10.

        Returns:
            str: A JSON string containing the search results with paper details.
        """
        try:
            log_debug(f"Searching CORE for: {query}")
            max_results = max_results or self.max_results or 10

            # CORE API endpoint
            url = "https://api.core.ac.uk/v3/search/works"
            params = {
                "q": query,
                "limit": min(max_results, 100),  # API limit
                "page": 1,
            }

            headers = {
                "Content-Type": "application/json",
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = httpx.get(url, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            papers = []
            results = data.get("results", [])[:max_results]

            for result in results:
                # Extract key information
                core_id = result.get("id", "N/A")
                title = result.get("title", "No title available")
                authors = result.get("authors", [])
                author_names = (
                    ", ".join([author.get("name", "") for author in authors[:5]]) if authors else "Not available"
                )
                if len(authors) > 5:
                    author_names += f" et al. ({len(authors)} total authors)"

                year = result.get("yearPublished", "Unknown")
                abstract = result.get("abstract", "No abstract available")
                doi = result.get("doi", "Not available")
                url = result.get("downloadUrl", result.get("url", "Not available"))
                language = result.get("language", {}).get("code", "Unknown")
                repositories = result.get("repositories", [])
                repo_names = (
                    ", ".join([repo.get("name", "") for repo in repositories[:3]]) if repositories else "Not specified"
                )

                # Full text availability
                fulltext_available = result.get("fullText", False)

                paper = {
                    "CORE_ID": core_id,
                    "Title": title,
                    "Authors": author_names,
                    "Year": year,
                    "Abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
                    "DOI": doi,
                    "URL": url,
                    "Language": language,
                    "Repositories": repo_names,
                    "Full_Text_Available": fulltext_available,
                }
                papers.append(paper)

            if not papers:
                return json.dumps({"message": "No papers found for the query.", "query": query})

            return json.dumps(papers, indent=2)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching CORE: {e}")
            if e.response.status_code == 429:
                return json.dumps({"error": "rate_limit", "message": "Rate limit exceeded. Please try again later."})
            return json.dumps({"error": f"HTTP error: {e.response.status_code}", "message": "Could not fetch papers."})
        except httpx.TimeoutException:
            logger.error("Timeout searching CORE")
            return json.dumps({"error": "timeout", "message": "Request to CORE timed out."})
        except Exception as e:
            logger.error(f"Error searching CORE: {e}", exc_info=True)
            return json.dumps({"error": str(e), "message": "Could not fetch papers."})
