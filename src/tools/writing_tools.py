"""
Writing Tools for Research Writing Agent

Provides citation formatting, extraction, and validation tools.
Enables structured communication with Citation Validation Agent.

Created: 2025-12-07 (Phase A - Agent Optimization)
"""
import re
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

from agno.tools import Toolkit

logger = logging.getLogger(__name__)


class WritingTools(Toolkit):
    """
    Tools for research writing and citation management.
    
    Features:
    - Extract citations from prose text
    - Format citations in APA 7th edition
    - Validate citation format
    """
    
    def __init__(self):
        super().__init__(name="writing_tools")
        
        # Register tools
        self.register(self.extract_citations)
        self.register(self.format_citation_apa7)
        self.register(self.validate_citation_format)
        self.register(self.create_reference_list)
        
        logger.info("✅ WritingTools initialized with 4 tools")
    
    def extract_citations(self, text: str) -> str:
        """
        Extract citations from prose text.
        
        Finds PMIDs, DOIs, and author-year citations in text and returns
        structured data that can be passed to Citation Validation Agent.
        
        Args:
            text: Prose text containing citations
            
        Returns:
            JSON string with list of extracted citations
        """
        citations = []
        
        # Pattern 1: PMID mentions (PMID: 12345 or PMID 12345)
        pmid_pattern = r'PMID[:\s]*(\d{7,8})'
        for match in re.finditer(pmid_pattern, text, re.IGNORECASE):
            pmid = match.group(1)
            # Get surrounding context (50 chars before/after)
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end].strip()
            
            citations.append({
                "type": "pmid",
                "pmid": pmid,
                "context": context,
                "position": match.start()
            })
        
        # Pattern 2: DOI mentions
        doi_pattern = r'(?:doi[:\s]*)?10\.\d{4,}/[^\s]+'
        for match in re.finditer(doi_pattern, text, re.IGNORECASE):
            doi = match.group(0).lower()
            if doi.startswith('doi'):
                doi = re.sub(r'^doi[:\s]*', '', doi)
            
            citations.append({
                "type": "doi",
                "doi": doi,
                "position": match.start()
            })
        
        # Pattern 3: Author-year citations (Smith et al., 2024)
        author_year_pattern = r'([A-Z][a-z]+(?:\s+et\s+al\.?)?)\s*\((\d{4})\)'
        for match in re.finditer(author_year_pattern, text):
            citations.append({
                "type": "author_year",
                "author": match.group(1),
                "year": match.group(2),
                "position": match.start()
            })
        
        # Remove duplicates
        seen = set()
        unique_citations = []
        for c in citations:
            key = json.dumps(c, sort_keys=True)
            if key not in seen:
                seen.add(key)
                unique_citations.append(c)
        
        result = {
            "total_citations": len(unique_citations),
            "citations": unique_citations,
            "pmid_count": sum(1 for c in unique_citations if c["type"] == "pmid"),
            "doi_count": sum(1 for c in unique_citations if c["type"] == "doi"),
            "author_year_count": sum(1 for c in unique_citations if c["type"] == "author_year"),
        }
        
        return json.dumps(result, indent=2)
    
    def format_citation_apa7(
        self,
        title: str,
        authors: str,
        year: str,
        journal: str = "",
        volume: str = "",
        issue: str = "",
        pages: str = "",
        doi: str = "",
        pmid: str = ""
    ) -> str:
        """
        Format a citation in APA 7th edition style.
        
        Args:
            title: Article title
            authors: Author names (e.g., "Smith, J., & Jones, M.")
            year: Publication year
            journal: Journal name (italicized in output)
            volume: Volume number
            issue: Issue number
            pages: Page range
            doi: Digital Object Identifier
            pmid: PubMed ID
            
        Returns:
            Formatted APA 7 citation string
        """
        # Build citation parts
        parts = []
        
        # Authors and year
        if authors:
            parts.append(f"{authors} ({year}).")
        else:
            parts.append(f"({year}).")
        
        # Title (sentence case, no italics for articles)
        if title:
            # Ensure ends with period
            title_clean = title.rstrip('.')
            parts.append(f"{title_clean}.")
        
        # Journal (italicized), volume, issue, pages
        journal_part = ""
        if journal:
            journal_part = f"*{journal}*"
            if volume:
                journal_part += f", *{volume}*"
                if issue:
                    journal_part += f"({issue})"
            if pages:
                journal_part += f", {pages}"
            journal_part += "."
            parts.append(journal_part)
        
        # DOI (preferred) or PMID
        if doi:
            if not doi.startswith("https://"):
                doi = f"https://doi.org/{doi}"
            parts.append(doi)
        elif pmid:
            parts.append(f"PMID: {pmid}")
        
        citation = " ".join(parts)
        
        return json.dumps({
            "formatted_citation": citation,
            "style": "APA 7th Edition",
            "has_doi": bool(doi),
            "has_pmid": bool(pmid)
        })
    
    def validate_citation_format(self, citation_text: str) -> str:
        """
        Validate that a citation follows proper format.
        
        Checks for common issues:
        - Missing year
        - Missing authors
        - Incomplete reference
        - URL format issues
        
        Args:
            citation_text: Citation text to validate
            
        Returns:
            JSON validation report
        """
        issues = []
        warnings = []
        
        # Check for year
        year_pattern = r'\((\d{4})\)'
        if not re.search(year_pattern, citation_text):
            issues.append("Missing publication year in parentheses")
        
        # Check for authors (starts with capital letter, comma)
        if not re.match(r'^[A-Z][a-z]+,?\s', citation_text):
            warnings.append("Citation may not start with author name")
        
        # Check for journal italics (markdown format)
        if '*' not in citation_text and 'journal' in citation_text.lower():
            warnings.append("Journal name should be italicized (*Journal Name*)")
        
        # Check for DOI/PMID
        has_doi = 'doi.org' in citation_text.lower() or '10.' in citation_text
        has_pmid = 'pmid' in citation_text.lower()
        
        if not has_doi and not has_pmid:
            warnings.append("Consider adding DOI or PMID for verification")
        
        # Check for "et al." usage
        if 'et al' in citation_text and '.' not in citation_text[citation_text.find('et al'):citation_text.find('et al')+7]:
            issues.append("'et al.' should include period")
        
        is_valid = len(issues) == 0
        
        return json.dumps({
            "is_valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "has_doi": has_doi,
            "has_pmid": has_pmid
        })
    
    def create_reference_list(self, citations: List[Dict]) -> str:
        """
        Create a formatted reference list from citation data.
        
        Args:
            citations: List of citation dicts with title, authors, year, etc.
            
        Returns:
            Formatted reference list in APA 7 style
        """
        if not citations:
            return json.dumps({"reference_list": "", "count": 0})
        
        formatted_refs = []
        
        for i, cite in enumerate(citations, 1):
            # Format each citation
            ref = self.format_citation_apa7(
                title=cite.get("title", ""),
                authors=cite.get("authors", ""),
                year=cite.get("year", ""),
                journal=cite.get("journal", ""),
                volume=cite.get("volume", ""),
                issue=cite.get("issue", ""),
                pages=cite.get("pages", ""),
                doi=cite.get("doi", ""),
                pmid=cite.get("pmid", "")
            )
            ref_data = json.loads(ref)
            formatted_refs.append(ref_data["formatted_citation"])
        
        # Sort alphabetically by first author
        formatted_refs.sort()
        
        # Create numbered list
        reference_list = "\n".join(f"{i}. {ref}" for i, ref in enumerate(formatted_refs, 1))
        
        return json.dumps({
            "reference_list": reference_list,
            "count": len(formatted_refs),
            "style": "APA 7th Edition"
        })


def create_writing_tools() -> WritingTools:
    """Factory function to create WritingTools instance."""
    return WritingTools()
