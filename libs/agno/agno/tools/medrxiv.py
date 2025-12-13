import json
from typing import Any, Dict, List, Optional

import httpx

from agno.tools import Toolkit
from agno.utils.log import log_debug, logger


class MedRxivTools(Toolkit):
    """Toolkit for searching medRxiv and bioRxiv preprint servers."""

    def __init__(
        self,
        enable_search_medrxiv: bool = True,
        enable_search_biorxiv: bool = True,
        max_results: Optional[int] = 10,
        **kwargs,
    ):
        self.max_results: Optional[int] = max_results or 10
        self.enable_search_medrxiv = enable_search_medrxiv
        self.enable_search_biorxiv = enable_search_biorxiv

        tools: List[Any] = []
        if enable_search_medrxiv or enable_search_biorxiv:
            tools.append(self.search_medrxiv)

        super().__init__(name="medrxiv", tools=tools, **kwargs)

    def search_medrxiv(self, query: str, max_results: Optional[int] = None, server: str = "medrxiv") -> str:
        """Use this function to search medRxiv or bioRxiv for medical/biological preprints.

        Args:
            query (str): The search query. REQUIRED - must be a non-empty string.
            max_results (int, optional): Maximum number of results to return. Defaults to 10.
            server (str, optional): Which server to search - "medrxiv" or "biorxiv". Defaults to "medrxiv".

        Returns:
            str: A JSON string containing the search results with preprint details.
        """
        # Defensive guard: validate query parameter
        if not query or not isinstance(query, str):
            raise ValueError("search_medrxiv requires a non-empty string query")

        try:
            log_debug(f"Searching {server} for: {query}")
            max_results = max_results or self.max_results or 10

            # medRxiv/bioRxiv API endpoint
            # Note: The API uses cursor-based pagination
            url = f"https://api.biorxiv.org/details/{server}"
            params = {
                "query": query,
                "limit": min(max_results, 100),  # API limit
                "format": "json",
            }

            response = httpx.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            preprints = []
            collection = data.get("collection", [])

            for item in collection[:max_results]:
                # Extract key information
                doi = item.get("doi", "N/A")
                title = item.get("title", "No title available")
                authors = item.get("authors", "Not available")
                date = item.get("date", "Unknown")
                category = item.get("category", "Not specified")
                abstract = item.get("abstract", "No abstract available")
                published = item.get("published", "Not available")
                version = item.get("version", "1")

                # Construct URLs
                doi_url = f"https://doi.org/{doi}" if doi != "N/A" else "Not available"
                pdf_url = (
                    item.get("jatsxml", "").replace(".xml", ".full.pdf") if item.get("jatsxml") else "Not available"
                )

                preprint = {
                    "DOI": doi,
                    "Title": title,
                    "Authors": authors,
                    "Date": date,
                    "Published": published,
                    "Category": category,
                    "Version": version,
                    "Abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
                    "DOI_URL": doi_url,
                    "PDF_URL": pdf_url,
                    "Server": server,
                }
                preprints.append(preprint)

            if not preprints:
                return json.dumps({"message": f"No preprints found on {server} for the query.", "query": query})

            return json.dumps(preprints, indent=2)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching {server}: {e}")
            return json.dumps(
                {
                    "error": f"HTTP error: {e.response.status_code}",
                    "message": f"Could not fetch preprints from {server}.",
                }
            )
        except httpx.TimeoutException:
            logger.error(f"Timeout searching {server}")
            return json.dumps({"error": "timeout", "message": f"Request to {server} timed out."})
        except Exception as e:
            logger.error(f"Error searching {server}: {e}", exc_info=True)
            return json.dumps({"error": str(e), "message": f"Could not fetch preprints from {server}."})
