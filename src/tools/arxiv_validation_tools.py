"""
Arxiv Validation Tools - Check preprint status and metadata quality.
Phase 1: Agent 3 Enhancement
Date: 2025-12-09
"""

from typing import Dict, Any, List


class ArxivValidationTools:
    """Validate Arxiv papers for peer-review status and quality indicators."""

    @staticmethod
    def assess_preprint_status(arxiv_id: str, title: str = "", abstract: str = "") -> Dict[str, Any]:
        """
        Assess if Arxiv paper has been peer-reviewed or remains a preprint.
        """
        warnings = []
        quality_score = 0.5

        is_preprint = True
        warnings.append("PREPRINT: Not peer-reviewed. Verify findings independently.")

        publication_indicators = [
            "published in", "accepted to", "appeared in", "proceedings of", "journal of"
        ]

        combined_text = (title + " " + abstract).lower()
        if any(indicator in combined_text for indicator in publication_indicators):
            warnings.append("May have been peer-reviewed (check journal publication)")
            quality_score = 0.7

        try:
            if '.' in arxiv_id:
                year_month = arxiv_id.split('.')[0]
                year = int(year_month[:2])
                if year < 20:
                    warnings.append("OLD PREPRINT: Consider finding updated version")
                    quality_score -= 0.2
        except (ValueError, IndexError):
            pass

        if abstract and len(abstract) < 100:
            warnings.append("SHORT ABSTRACT: Limited information available")
            quality_score -= 0.1

        return {
            "arxiv_id": arxiv_id,
            "is_preprint": is_preprint,
            "warnings": warnings,
            "quality_score": max(0.0, min(1.0, quality_score))
        }

    @staticmethod
    def format_preprint_warning(arxiv_ids: List[str]) -> str:
        """Generate warning text for preprint citations."""
        if not arxiv_ids:
            return ""

        warning = "\n\n## PREPRINT STATUS WARNINGS\n"
        warning += "The following are Arxiv preprints (NOT peer-reviewed):\n"
        for arxiv_id in arxiv_ids:
            warning += f"- **{arxiv_id}**: Verify findings with peer-reviewed sources\n"

        return warning
