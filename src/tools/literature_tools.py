"""
Literature Tools - Database tools for saving and managing research findings.

Provides research agents (Medical, Academic, Nursing) with ability to save
findings to the project database's `literature_findings` table.

Created: 2025-12-02
Part of: Agent-to-Project Database Bridge Implementation
Pattern: Follows MilestoneTools structure from src/tools/milestone_tools.py
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from agno.tools import Toolkit

from project_manager import get_project_manager

logger = logging.getLogger(__name__)


class LiteratureTools(Toolkit):
    """
    Tools for saving and managing literature findings in the project database.

    Provides methods to:
    - Save literature findings from research agents
    - Retrieve saved findings with filtering
    - Mark findings as selected for project
    - Search across saved findings
    - Delete findings
    """

    def __init__(self, project_name: Optional[str] = None):
        """
        Initialize LiteratureTools.

        Args:
            project_name: Project name, or None to use active project
        """
        super().__init__(name="literature_tools")
        self.project_name = project_name
        self.pm = get_project_manager()
        logger.info(f"LiteratureTools initialized for project: {project_name or 'active'}")

    def save_finding(
        self,
        agent_source: str,
        title: str,
        finding_type: str = "article",
        authors: Optional[str] = None,
        publication_date: Optional[str] = None,
        journal_source: Optional[str] = None,
        doi: Optional[str] = None,
        pmid: Optional[str] = None,
        arxiv_id: Optional[str] = None,
        url: Optional[str] = None,
        abstract: Optional[str] = None,
        key_findings: Optional[List[str]] = None,
        methodology: Optional[str] = None,
        clinical_implications: Optional[str] = None,
        tags: Optional[List[str]] = None,
        relevance_score: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> str:
        """
        Save a literature finding to the project database.

        Args:
            agent_source: Name of agent that found this (e.g., "medical_research", "academic_research")
            title: Article/finding title (required)
            finding_type: One of: 'article', 'standard', 'guideline', 'synthesis', 'best_practice'
            authors: Author names (comma-separated string)
            publication_date: Publication date (YYYY-MM-DD format)
            journal_source: Journal or source name
            doi: Digital Object Identifier
            pmid: PubMed ID
            arxiv_id: ArXiv ID
            url: URL to the finding
            abstract: Abstract text
            key_findings: List of key findings/conclusions
            methodology: Methodology description
            clinical_implications: Clinical implications
            tags: List of tags for organization
            relevance_score: Relevance score (0.0 to 1.0)
            notes: User notes

        Returns:
            JSON string with success status and finding_id, or error message
        """
        # Validate finding_type
        valid_types = ['article', 'standard', 'guideline', 'synthesis', 'best_practice']
        if finding_type not in valid_types:
            return json.dumps({
                "error": f"Invalid finding_type. Must be one of: {valid_types}"
            })

        # Validate relevance_score if provided
        if relevance_score is not None and not (0 <= relevance_score <= 1):
            return json.dumps({
                "error": "relevance_score must be between 0.0 and 1.0"
            })

        try:
            conn = self.pm.get_project_connection(self.project_name)

            # Check for duplicates based on PMID or DOI
            if pmid:
                cursor = conn.execute(
                    "SELECT finding_id FROM literature_findings WHERE pmid = ?",
                    (pmid,)
                )
                existing = cursor.fetchone()
                if existing:
                    conn.close()
                    return json.dumps({
                        "warning": "duplicate",
                        "message": f"Finding with PMID {pmid} already exists",
                        "existing_finding_id": existing["finding_id"]
                    })

            if doi:
                cursor = conn.execute(
                    "SELECT finding_id FROM literature_findings WHERE doi = ?",
                    (doi,)
                )
                existing = cursor.fetchone()
                if existing:
                    conn.close()
                    return json.dumps({
                        "warning": "duplicate",
                        "message": f"Finding with DOI {doi} already exists",
                        "existing_finding_id": existing["finding_id"]
                    })

            # Insert the finding
            cursor = conn.execute("""
                INSERT INTO literature_findings (
                    agent_source, finding_type, title, authors, publication_date,
                    journal_source, doi, pmid, arxiv_id, url, abstract,
                    key_findings, methodology, clinical_implications,
                    tags, relevance_score, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_source,
                finding_type,
                title,
                authors,
                publication_date,
                journal_source,
                doi,
                pmid,
                arxiv_id,
                url,
                abstract,
                json.dumps(key_findings) if key_findings else None,
                methodology,
                clinical_implications,
                json.dumps(tags) if tags else None,
                relevance_score,
                notes
            ))

            finding_id = cursor.lastrowid
            conn.commit()
            conn.close()

            result = {
                "success": True,
                "finding_id": finding_id,
                "title": title,
                "agent_source": agent_source,
                "pmid": pmid,
                "doi": doi,
                "message": f"Finding saved successfully with ID {finding_id}"
            }

            logger.info(f"Saved finding: {title[:50]}... (ID: {finding_id})")
            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error saving finding: {e}")
            return json.dumps({"error": str(e)})

    def get_saved_findings(
        self,
        agent_source: Optional[str] = None,
        selected_only: bool = False,
        finding_type: Optional[str] = None,
        limit: int = 50
    ) -> str:
        """
        Get saved literature findings from the project database.

        Args:
            agent_source: Filter by agent source (e.g., "medical_research")
            selected_only: If True, only return findings marked for project
            finding_type: Filter by finding type
            limit: Maximum number of results (default 50)

        Returns:
            JSON string with list of findings
        """
        try:
            conn = self.pm.get_project_connection(self.project_name)

            # Build query with filters
            query = """
                SELECT
                    finding_id, agent_source, finding_type, title, authors,
                    publication_date, journal_source, doi, pmid, arxiv_id, url,
                    abstract, key_findings, relevance_score, selected_for_project,
                    notes, created_at
                FROM literature_findings
                WHERE 1=1
            """
            params = []

            if agent_source:
                query += " AND agent_source = ?"
                params.append(agent_source)

            if selected_only:
                query += " AND selected_for_project = 1"

            if finding_type:
                query += " AND finding_type = ?"
                params.append(finding_type)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, params)

            findings = []
            for row in cursor.fetchall():
                finding = {
                    "finding_id": row["finding_id"],
                    "agent_source": row["agent_source"],
                    "finding_type": row["finding_type"],
                    "title": row["title"],
                    "authors": row["authors"],
                    "publication_date": row["publication_date"],
                    "journal_source": row["journal_source"],
                    "doi": row["doi"],
                    "pmid": row["pmid"],
                    "arxiv_id": row["arxiv_id"],
                    "url": row["url"],
                    "abstract": row["abstract"][:200] + "..." if row["abstract"] and len(row["abstract"]) > 200 else row["abstract"],
                    "key_findings": json.loads(row["key_findings"]) if row["key_findings"] else [],
                    "relevance_score": row["relevance_score"],
                    "selected_for_project": bool(row["selected_for_project"]),
                    "notes": row["notes"],
                    "created_at": row["created_at"]
                }
                findings.append(finding)

            conn.close()

            logger.info(f"Retrieved {len(findings)} findings")
            return json.dumps({
                "count": len(findings),
                "findings": findings
            }, indent=2)

        except Exception as e:
            logger.error(f"Error getting findings: {e}")
            return json.dumps({"error": str(e)})

    def mark_finding_selected(
        self,
        finding_id: int,
        selected: bool = True,
        notes: Optional[str] = None
    ) -> str:
        """
        Mark a finding as selected (or deselected) for the project.

        Args:
            finding_id: ID of the finding to update
            selected: True to select, False to deselect
            notes: Optional notes to add

        Returns:
            JSON string with success/error message
        """
        try:
            conn = self.pm.get_project_connection(self.project_name)

            # Update the finding
            if notes:
                conn.execute("""
                    UPDATE literature_findings
                    SET selected_for_project = ?,
                        notes = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE finding_id = ?
                """, (1 if selected else 0, notes, finding_id))
            else:
                conn.execute("""
                    UPDATE literature_findings
                    SET selected_for_project = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE finding_id = ?
                """, (1 if selected else 0, finding_id))

            conn.commit()

            # Get updated finding
            cursor = conn.execute("""
                SELECT finding_id, title, selected_for_project, notes
                FROM literature_findings
                WHERE finding_id = ?
            """, (finding_id,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                return json.dumps({"error": f"Finding {finding_id} not found"})

            result = {
                "success": True,
                "finding_id": finding_id,
                "title": row["title"],
                "selected_for_project": bool(row["selected_for_project"]),
                "notes": row["notes"]
            }

            logger.info(f"Updated finding {finding_id}: selected={selected}")
            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error updating finding: {e}")
            return json.dumps({"error": str(e)})

    def search_findings(self, query: str, limit: int = 20) -> str:
        """
        Search across saved findings by title and abstract.

        Args:
            query: Search query string
            limit: Maximum results (default 20)

        Returns:
            JSON string with matching findings
        """
        try:
            conn = self.pm.get_project_connection(self.project_name)

            # Simple LIKE search
            search_pattern = f"%{query}%"
            cursor = conn.execute("""
                SELECT
                    finding_id, agent_source, title, authors, pmid, doi,
                    abstract, selected_for_project, created_at
                FROM literature_findings
                WHERE title LIKE ? OR abstract LIKE ? OR authors LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (search_pattern, search_pattern, search_pattern, limit))

            findings = []
            for row in cursor.fetchall():
                finding = {
                    "finding_id": row["finding_id"],
                    "agent_source": row["agent_source"],
                    "title": row["title"],
                    "authors": row["authors"],
                    "pmid": row["pmid"],
                    "doi": row["doi"],
                    "abstract_preview": row["abstract"][:150] + "..." if row["abstract"] and len(row["abstract"]) > 150 else row["abstract"],
                    "selected_for_project": bool(row["selected_for_project"]),
                    "created_at": row["created_at"]
                }
                findings.append(finding)

            conn.close()

            logger.info(f"Search '{query}' returned {len(findings)} results")
            return json.dumps({
                "query": query,
                "count": len(findings),
                "findings": findings
            }, indent=2)

        except Exception as e:
            logger.error(f"Error searching findings: {e}")
            return json.dumps({"error": str(e)})

    def delete_finding(self, finding_id: int) -> str:
        """
        Delete a finding from the project database.

        Args:
            finding_id: ID of the finding to delete

        Returns:
            JSON string with success/error message
        """
        try:
            conn = self.pm.get_project_connection(self.project_name)

            # Get finding info before deletion
            cursor = conn.execute("""
                SELECT finding_id, title, pmid
                FROM literature_findings
                WHERE finding_id = ?
            """, (finding_id,))

            row = cursor.fetchone()
            if not row:
                conn.close()
                return json.dumps({"error": f"Finding {finding_id} not found"})

            title = row["title"]

            # Delete the finding
            conn.execute("DELETE FROM literature_findings WHERE finding_id = ?", (finding_id,))
            conn.commit()
            conn.close()

            result = {
                "success": True,
                "deleted_finding_id": finding_id,
                "deleted_title": title,
                "message": f"Finding deleted successfully"
            }

            logger.info(f"Deleted finding {finding_id}: {title[:30]}...")
            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error deleting finding: {e}")
            return json.dumps({"error": str(e)})

    def get_finding_count(self) -> str:
        """
        Get count of findings in the project database.

        Returns:
            JSON string with counts by agent and selection status
        """
        try:
            conn = self.pm.get_project_connection(self.project_name)

            # Total count
            cursor = conn.execute("SELECT COUNT(*) as total FROM literature_findings")
            total = cursor.fetchone()["total"]

            # Count by agent
            cursor = conn.execute("""
                SELECT agent_source, COUNT(*) as count
                FROM literature_findings
                GROUP BY agent_source
            """)
            by_agent = {row["agent_source"]: row["count"] for row in cursor.fetchall()}

            # Count selected
            cursor = conn.execute("""
                SELECT COUNT(*) as selected
                FROM literature_findings
                WHERE selected_for_project = 1
            """)
            selected = cursor.fetchone()["selected"]

            conn.close()

            result = {
                "total_findings": total,
                "selected_for_project": selected,
                "by_agent": by_agent
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error getting finding count: {e}")
            return json.dumps({"error": str(e)})
