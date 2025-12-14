"""
Agent Handoff Protocol

Defines structured data contracts for agent-to-agent communication.
Replaces string-based handoffs with typed objects.

Created: 2025-12-07 (Phase D - Agent Optimization)
"""
import re
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """A single citation reference."""
    pmid: Optional[str] = None
    doi: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[str] = None
    year: Optional[str] = None
    journal: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class AgentHandoff:
    """
    Structured handoff between agents.
    
    Instead of passing raw strings, agents pass this structured object
    that includes both the content and extracted metadata.
    
    Attributes:
        agent_name: Name of the sending agent
        content: The full text content
        structured_data: Optional parsed JSON data
        citations: List of Citation objects extracted from content
        confidence: Agent's confidence in the output (0.0-1.0)
        timestamp: When the handoff was created
        metadata: Additional key-value metadata
    """
    agent_name: str
    content: str
    structured_data: Optional[Dict] = None
    citations: List[Citation] = field(default_factory=list)
    confidence: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "agent_name": self.agent_name,
            "content": self.content,
            "structured_data": self.structured_data,
            "citations": [c.to_dict() for c in self.citations],
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AgentHandoff":
        """Create from dictionary."""
        citations = [
            Citation(**c) if isinstance(c, dict) else c 
            for c in data.get("citations", [])
        ]
        return cls(
            agent_name=data["agent_name"],
            content=data["content"],
            structured_data=data.get("structured_data"),
            citations=citations,
            confidence=data.get("confidence", 1.0),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
        )
    
    def get_pmids(self) -> List[str]:
        """Get all PMIDs from citations."""
        return [c.pmid for c in self.citations if c.pmid]
    
    def get_dois(self) -> List[str]:
        """Get all DOIs from citations."""
        return [c.doi for c in self.citations if c.doi]
    
    def has_citations(self) -> bool:
        """Check if handoff contains any citations."""
        return len(self.citations) > 0


def extract_citations_from_text(text: str) -> List[Citation]:
    """
    Extract citations from prose text.
    
    Finds PMIDs, DOIs, and author-year patterns and creates Citation objects.
    
    Args:
        text: Prose text containing citations
        
    Returns:
        List of Citation objects
    """
    citations = []
    seen_pmids = set()
    seen_dois = set()
    
    # Pattern 1: PMID mentions
    pmid_pattern = r'PMID[:\s]*(\d{7,8})'
    for match in re.finditer(pmid_pattern, text, re.IGNORECASE):
        pmid = match.group(1)
        if pmid not in seen_pmids:
            seen_pmids.add(pmid)
            
            # Try to extract title from nearby context
            start = max(0, match.start() - 200)
            end = min(len(text), match.end() + 50)
            context = text[start:end]
            
            # Look for title pattern: "Title" or Title:
            title_match = re.search(r'["\']([^"\']{10,100})["\']', context)
            title = title_match.group(1) if title_match else None
            
            citations.append(Citation(pmid=pmid, title=title))
    
    # Pattern 2: DOI mentions
    doi_pattern = r'(?:doi[:\s]*)?10\.\d{4,}/[^\s\]\)>]+'
    for match in re.finditer(doi_pattern, text, re.IGNORECASE):
        doi = match.group(0).lower()
        if doi.startswith('doi'):
            doi = re.sub(r'^doi[:\s]*', '', doi)
        if doi not in seen_dois:
            seen_dois.add(doi)
            citations.append(Citation(doi=doi))
    
    # Pattern 3: Author-year for context (not as Citation unless PMID/DOI found)
    # These are informational only
    
    return citations


def create_handoff(
    agent_name: str,
    content: str,
    structured_data: Optional[Dict] = None,
    confidence: float = 1.0,
    **metadata
) -> AgentHandoff:
    """
    Factory function to create a handoff with auto-extracted citations.
    
    Args:
        agent_name: Name of the sending agent
        content: The full text content
        structured_data: Optional parsed data
        confidence: Confidence level (0.0-1.0)
        **metadata: Additional key-value pairs
        
    Returns:
        AgentHandoff with extracted citations
    """
    citations = extract_citations_from_text(content)
    
    return AgentHandoff(
        agent_name=agent_name,
        content=content,
        structured_data=structured_data,
        citations=citations,
        confidence=confidence,
        metadata=metadata,
    )


# Convenience function for agents
def parse_handoff_content(content: str) -> Dict:
    """
    Parse agent output content to extract structured data.
    
    Attempts to parse JSON from content, with fallback to text extraction.
    
    Returns:
        Dictionary with extracted/parsed data
    """
    result = {
        "raw_content": content,
        "has_json": False,
        "extracted_data": {},
    }
    
    # Try to find JSON block in content
    json_pattern = r'```json\s*([\s\S]*?)\s*```'
    json_match = re.search(json_pattern, content)
    
    if json_match:
        try:
            result["extracted_data"] = json.loads(json_match.group(1))
            result["has_json"] = True
        except json.JSONDecodeError:
            pass
    
    # Also try direct JSON parsing
    if not result["has_json"]:
        try:
            result["extracted_data"] = json.loads(content)
            result["has_json"] = True
        except json.JSONDecodeError:
            pass
    
    return result
