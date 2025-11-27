import json
from typing import Any, Dict, List, Optional

import httpx

from agno.tools import Toolkit
from agno.utils.log import log_debug, logger


class DoajTools(Toolkit):
    """Toolkit for searching DOAJ (Directory of Open Access Journals)."""

    def __init__(
        self,
        enable_search_doaj: bool = True,
        max_results: Optional[int] = 10,
        **kwargs,
    ):
        self.max_results: Optional[int] = max_results or 10

        tools: List[Any] = []
        if enable_search_doaj:
            tools.append(self.search_doaj)

        super().__init__(name="doaj", tools=tools, **kwargs)

    def search_doaj(self, query: str, max_results: Optional[int] = None) -> str:
        """Use this function to search DOAJ for open-access journal articles.

        Args:
            query (str): The search query.
            max_results (int, optional): Maximum number of results to return. Defaults to 10.

        Returns:
            str: A JSON string containing the search results with article details.
        """
        try:
            log_debug(f"Searching DOAJ for: {query}")
            max_results = max_results or self.max_results or 10

            # DOAJ API endpoint
            url = "https://doaj.org/api/v2/search/articles"
            params = {
                "q": query,
                "pageSize": min(max_results, 100),  # API limit
                "page": 1,
            }

            response = httpx.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            articles = []
            results = data.get("results", [])[:max_results]

            for result in results:
                # Extract key information
                article_id = result.get("id", "N/A")
                title = result.get("bibjson", {}).get("title", "No title available")
                authors = result.get("bibjson", {}).get("author", [])
                author_names = ", ".join([author.get("name", "") for author in authors[:5]]) if authors else "Not available"
                if len(authors) > 5:
                    author_names += f" et al. ({len(authors)} total authors)"

                year = result.get("bibjson", {}).get("year", "Unknown")
                abstract = result.get("bibjson", {}).get("abstract", "No abstract available")
                doi = result.get("bibjson", {}).get("identifier", [])
                doi_value = "Not available"
                for identifier in doi:
                    if identifier.get("type") == "doi":
                        doi_value = identifier.get("id", "Not available")
                        break

                journal = result.get("bibjson", {}).get("journal", {})
                journal_title = journal.get("title", "Not specified") if isinstance(journal, dict) else "Not specified"
                publisher = journal.get("publisher", "Not specified") if isinstance(journal, dict) else "Not specified"

                keywords = result.get("bibjson", {}).get("keywords", [])
                keywords_str = ", ".join(keywords[:10]) if keywords else "Not available"

                # Links
                link = result.get("bibjson", {}).get("link", [])
                url = "Not available"
                for l in link:
                    if l.get("type") == "fulltext":
                        url = l.get("url", "Not available")
                        break

                article = {
                    "Article_ID": article_id,
                    "Title": title,
                    "Authors": author_names,
                    "Year": year,
                    "Journal": journal_title,
                    "Publisher": publisher,
                    "Abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
                    "DOI": doi_value,
                    "Keywords": keywords_str,
                    "URL": url,
                }
                articles.append(article)

            if not articles:
                return json.dumps({"message": "No articles found for the query.", "query": query})

            return json.dumps(articles, indent=2)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching DOAJ: {e}")
            return json.dumps({"error": f"HTTP error: {e.response.status_code}", "message": "Could not fetch articles."})
        except httpx.TimeoutException:
            logger.error("Timeout searching DOAJ")
            return json.dumps({"error": "timeout", "message": "Request to DOAJ timed out."})
        except Exception as e:
            logger.error(f"Error searching DOAJ: {e}", exc_info=True)
            return json.dumps({"error": str(e), "message": "Could not fetch articles."})

