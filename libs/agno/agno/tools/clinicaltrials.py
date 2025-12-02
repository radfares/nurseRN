import json
from typing import Any, Dict, List, Optional

import httpx

from agno.tools import Toolkit
from agno.utils.log import log_debug, logger


class ClinicalTrialsTools(Toolkit):
    """Toolkit for searching ClinicalTrials.gov database."""

    def __init__(
        self,
        enable_search_clinicaltrials: bool = True,
        max_results: Optional[int] = 10,
        **kwargs,
    ):
        self.max_results: Optional[int] = max_results or 10

        tools: List[Any] = []
        if enable_search_clinicaltrials:
            tools.append(self.search_clinicaltrials)

        super().__init__(name="clinicaltrials", tools=tools, **kwargs)

    def search_clinicaltrials(self, query: str, max_results: Optional[int] = None) -> str:
        """Use this function to search ClinicalTrials.gov for clinical trials.

        Args:
            query (str): The search query (condition, intervention, or study details).
            max_results (int, optional): Maximum number of results to return. Defaults to 10.

        Returns:
            str: A JSON string containing the search results with trial details.
        """
        try:
            log_debug(f"Searching ClinicalTrials.gov for: {query}")
            max_results = max_results or self.max_results or 10

            # ClinicalTrials.gov API endpoint
            url = "https://clinicaltrials.gov/api/v2/studies"
            params = {
                "query.cond": query,
                "pageSize": min(max_results, 100),  # API limit is 100
                "format": "json",
            }

            response = httpx.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()

            trials = []
            studies = data.get("studies", [])[:max_results]

            for study in studies:
                protocol = study.get("protocolSection", {})
                identification = protocol.get("identificationModule", {})
                status = protocol.get("statusModule", {})
                design = protocol.get("designModule", {})
                eligibility = protocol.get("eligibilityModule", {})
                description = protocol.get("descriptionModule", {})

                # Extract key information
                nct_id = identification.get("nctId", "N/A")
                title = identification.get("briefTitle", "No title available")
                official_title = identification.get("officialTitle", title)

                # Status information
                overall_status = status.get("overallStatus", "Unknown")
                start_date = status.get("startDateStruct", {}).get("date", "Unknown")
                completion_date = status.get("completionDateStruct", {}).get("date", "Not available")

                # Design information
                study_type = design.get("studyType", "Not specified")
                phases = design.get("phases", [])

                # Eligibility
                eligibility_criteria = eligibility.get("eligibilityCriteria", "Not available")
                healthy_volunteers = eligibility.get("healthyVolunteers", "Not specified")

                # Description
                brief_summary = description.get("briefSummary", "No summary available")

                # Sponsors
                sponsor = (
                    protocol.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", "Not specified")
                )

                # Locations
                locations = protocol.get("contactsLocationsModule", {}).get("locations", [])
                location_countries = [loc.get("country", "") for loc in locations if loc.get("country")]

                trial = {
                    "NCT_ID": nct_id,
                    "Title": title,
                    "Official_Title": official_title,
                    "Status": overall_status,
                    "Start_Date": start_date,
                    "Completion_Date": completion_date,
                    "Study_Type": study_type,
                    "Phases": ", ".join(phases) if phases else "Not specified",
                    "Sponsor": sponsor,
                    "Countries": ", ".join(set(location_countries)) if location_countries else "Not specified",
                    "Eligibility_Criteria": eligibility_criteria[:500] + "..."
                    if len(eligibility_criteria) > 500
                    else eligibility_criteria,
                    "Summary": brief_summary,
                    "URL": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id != "N/A" else "Not available",
                }
                trials.append(trial)

            if not trials:
                return json.dumps({"message": "No clinical trials found for the query.", "query": query})

            return json.dumps(trials, indent=2)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching ClinicalTrials.gov: {e}")
            return json.dumps(
                {"error": f"HTTP error: {e.response.status_code}", "message": "Could not fetch clinical trials."}
            )
        except httpx.TimeoutException:
            logger.error("Timeout searching ClinicalTrials.gov")
            return json.dumps({"error": "timeout", "message": "Request to ClinicalTrials.gov timed out."})
        except Exception as e:
            logger.error(f"Error searching ClinicalTrials.gov: {e}", exc_info=True)
            return json.dumps({"error": str(e), "message": "Could not fetch clinical trials."})
