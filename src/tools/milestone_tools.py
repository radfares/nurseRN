"""
Milestone Tools - Database tools for querying and managing project milestones.

Provides Agent 5 (Project Timeline Agent) with ability to query the milestones
table instead of using hardcoded dates.

Created: 2025-11-26
Part of: Agent 5 Database Integration (BUG-1 fix)
"""

import json
import logging
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from agno.tools import Toolkit

from project_manager import get_project_manager

logger = logging.getLogger(__name__)


class MilestoneTools(Toolkit):
    """
    Tools for querying and managing project milestones.

    Provides methods to:
    - Get all milestones with status
    - Find next incomplete milestone
    - Get milestones by date range
    - Update milestone status
    - Add custom milestones
    """

    def __init__(self, project_name: Optional[str] = None):
        """
        Initialize MilestoneTools.

        Args:
            project_name: Project name, or None to use active project
        """
        super().__init__(name="milestone_tools")
        self.project_name = project_name
        self.pm = get_project_manager()
        logger.info(f"MilestoneTools initialized for project: {project_name or 'active'}")

    def get_all_milestones(self) -> str:
        """
        Get all milestones for the current project.

        Returns:
            JSON string with list of milestones containing:
            - milestone_id, milestone_name, description, due_date
            - status, completion_date, deliverables, notes

        Example:
            [
                {
                    "id": 1,
                    "name": "PICOT Development",
                    "due_date": "2025-12-17",
                    "status": "in_progress",
                    "deliverables": ["PICOT statement", "NM form"]
                }
            ]
        """
        try:
            conn = self.pm.get_project_connection(self.project_name)
            cursor = conn.execute("""
                SELECT
                    milestone_id, milestone_name, description, due_date,
                    status, completion_date, deliverables, notes,
                    created_at, updated_at
                FROM milestones
                ORDER BY due_date
            """)

            milestones = []
            for row in cursor.fetchall():
                milestone = {
                    "id": row["milestone_id"],
                    "name": row["milestone_name"],
                    "description": row["description"],
                    "due_date": row["due_date"],
                    "status": row["status"],
                    "completion_date": row["completion_date"],
                    "deliverables": json.loads(row["deliverables"]) if row["deliverables"] else [],
                    "notes": row["notes"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                milestones.append(milestone)

            conn.close()

            logger.info(f"Retrieved {len(milestones)} milestones")
            return json.dumps(milestones, indent=2)

        except Exception as e:
            logger.error(f"Error getting milestones: {e}")
            return json.dumps({"error": str(e)})

    def get_next_milestone(self) -> str:
        """
        Get the next incomplete milestone (not completed).

        Returns:
            JSON string with next milestone details, or empty if all complete.

        Example:
            {
                "id": 2,
                "name": "Literature Search",
                "due_date": "2026-01-21",
                "status": "pending",
                "days_until_due": 45
            }
        """
        try:
            conn = self.pm.get_project_connection(self.project_name)
            cursor = conn.execute("""
                SELECT
                    milestone_id, milestone_name, description, due_date,
                    status, deliverables, notes
                FROM milestones
                WHERE status != 'completed'
                ORDER BY due_date
                LIMIT 1
            """)

            row = cursor.fetchone()
            conn.close()

            if not row:
                return json.dumps({"message": "All milestones completed!"})

            # Calculate days until due
            due_date = datetime.strptime(row["due_date"], "%Y-%m-%d").date()
            today = date.today()
            days_until = (due_date - today).days

            milestone = {
                "id": row["milestone_id"],
                "name": row["milestone_name"],
                "description": row["description"],
                "due_date": row["due_date"],
                "status": row["status"],
                "deliverables": json.loads(row["deliverables"]) if row["deliverables"] else [],
                "notes": row["notes"],
                "days_until_due": days_until,
                "is_overdue": days_until < 0
            }

            logger.info(f"Next milestone: {milestone['name']} ({days_until} days)")
            return json.dumps(milestone, indent=2)

        except Exception as e:
            logger.error(f"Error getting next milestone: {e}")
            return json.dumps({"error": str(e)})

    def get_milestones_by_date_range(self, start_date: str, end_date: str) -> str:
        """
        Get milestones within a date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            JSON string with list of milestones in date range

        Example:
            get_milestones_by_date_range("2025-12-01", "2026-01-31")
        """
        try:
            conn = self.pm.get_project_connection(self.project_name)
            cursor = conn.execute("""
                SELECT
                    milestone_id, milestone_name, description, due_date,
                    status, completion_date, deliverables, notes
                FROM milestones
                WHERE due_date BETWEEN ? AND ?
                ORDER BY due_date
            """, (start_date, end_date))

            milestones = []
            for row in cursor.fetchall():
                milestone = {
                    "id": row["milestone_id"],
                    "name": row["milestone_name"],
                    "description": row["description"],
                    "due_date": row["due_date"],
                    "status": row["status"],
                    "completion_date": row["completion_date"],
                    "deliverables": json.loads(row["deliverables"]) if row["deliverables"] else [],
                    "notes": row["notes"]
                }
                milestones.append(milestone)

            conn.close()

            logger.info(f"Found {len(milestones)} milestones between {start_date} and {end_date}")
            return json.dumps(milestones, indent=2)

        except Exception as e:
            logger.error(f"Error getting milestones by date range: {e}")
            return json.dumps({"error": str(e)})

    def update_milestone_status(self, milestone_id: int, new_status: str) -> str:
        """
        Update the status of a milestone.

        Args:
            milestone_id: ID of milestone to update
            new_status: New status ('pending', 'in_progress', 'completed', 'overdue')

        Returns:
            JSON string with success/error message

        Example:
            update_milestone_status(1, "completed")
        """
        valid_statuses = ['pending', 'in_progress', 'completed', 'overdue']
        if new_status not in valid_statuses:
            return json.dumps({
                "error": f"Invalid status. Must be one of: {valid_statuses}"
            })

        try:
            conn = self.pm.get_project_connection(self.project_name)

            # If marking as completed, set completion_date
            if new_status == 'completed':
                conn.execute("""
                    UPDATE milestones
                    SET status = ?,
                        completion_date = DATE('now'),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE milestone_id = ?
                """, (new_status, milestone_id))
            else:
                conn.execute("""
                    UPDATE milestones
                    SET status = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE milestone_id = ?
                """, (new_status, milestone_id))

            conn.commit()

            # Get updated milestone
            cursor = conn.execute("""
                SELECT milestone_name, status, completion_date
                FROM milestones
                WHERE milestone_id = ?
            """, (milestone_id,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                return json.dumps({"error": f"Milestone {milestone_id} not found"})

            result = {
                "success": True,
                "milestone_id": milestone_id,
                "name": row["milestone_name"],
                "new_status": row["status"],
                "completion_date": row["completion_date"]
            }

            logger.info(f"Updated milestone {milestone_id} to status: {new_status}")
            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error updating milestone status: {e}")
            return json.dumps({"error": str(e)})

    def add_milestone(self, name: str, due_date: str, description: str = "",
                     deliverables: List[str] = None) -> str:
        """
        Add a custom milestone to the project.

        Args:
            name: Milestone name
            due_date: Due date in YYYY-MM-DD format
            description: Optional description
            deliverables: Optional list of deliverable items

        Returns:
            JSON string with created milestone details

        Example:
            add_milestone("Mid-project Check-in", "2026-02-15",
                         "Review progress with mentor",
                         ["Progress report", "Updated timeline"])
        """
        try:
            conn = self.pm.get_project_connection(self.project_name)

            deliverables_json = json.dumps(deliverables or [])

            cursor = conn.execute("""
                INSERT INTO milestones (milestone_name, description, due_date, deliverables, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (name, description, due_date, deliverables_json))

            milestone_id = cursor.lastrowid
            conn.commit()
            conn.close()

            result = {
                "success": True,
                "milestone_id": milestone_id,
                "name": name,
                "due_date": due_date,
                "description": description,
                "deliverables": deliverables or [],
                "status": "pending"
            }

            logger.info(f"Added new milestone: {name} (ID: {milestone_id})")
            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error adding milestone: {e}")
            return json.dumps({"error": str(e)})
