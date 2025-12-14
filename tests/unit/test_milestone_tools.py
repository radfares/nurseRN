"""
Unit tests for MilestoneTools
Tests the database query methods for milestone management
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import after path setup
from src.tools.milestone_tools import MilestoneTools


class TestMilestoneToolsInitialization:
    """Test MilestoneTools initialization"""

    @patch('src.tools.milestone_tools.get_project_manager')
    def test_initialization_with_project_name(self, mock_get_pm):
        """Test that MilestoneTools initializes with project name"""
        mock_pm = Mock()
        mock_get_pm.return_value = mock_pm

        tools = MilestoneTools(project_name="test_project")

        assert tools.project_name == "test_project"
        assert tools.pm == mock_pm
        mock_get_pm.assert_called_once()

    @patch('src.tools.milestone_tools.get_project_manager')
    def test_initialization_without_project_name(self, mock_get_pm):
        """Test that MilestoneTools initializes without project name (uses active)"""
        mock_pm = Mock()
        mock_get_pm.return_value = mock_pm

        tools = MilestoneTools()

        assert tools.project_name is None
        assert tools.pm == mock_pm


class TestGetAllMilestones:
    """Test get_all_milestones method"""

    @patch('src.tools.milestone_tools.get_project_manager')
    def test_get_all_milestones_success(self, mock_get_pm):
        """Test successful retrieval of all milestones"""
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pm = Mock()
        mock_pm.get_project_connection.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_get_pm.return_value = mock_pm

        # Mock milestone data
        mock_row = {
            "milestone_id": 1,
            "milestone_name": "PICOT Development",
            "description": "Develop PICOT question",
            "due_date": "2025-12-17",
            "status": "in_progress",
            "completion_date": None,
            "deliverables": '["PICOT statement", "NM form"]',
            "notes": "Contact NM for approval",
            "created_at": "2025-11-20",
            "updated_at": "2025-11-20"
        }
        mock_cursor.fetchall.return_value = [mock_row]

        tools = MilestoneTools()
        result_json = tools.get_all_milestones()
        result = json.loads(result_json)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["name"] == "PICOT Development"
        assert result[0]["deliverables"] == ["PICOT statement", "NM form"]
        mock_conn.close.assert_called_once()

    @patch('src.tools.milestone_tools.get_project_manager')
    def test_get_all_milestones_error_handling(self, mock_get_pm):
        """Test error handling in get_all_milestones"""
        mock_pm = Mock()
        mock_pm.get_project_connection.side_effect = Exception("Database error")
        mock_get_pm.return_value = mock_pm

        tools = MilestoneTools()
        result_json = tools.get_all_milestones()
        result = json.loads(result_json)

        assert "error" in result
        assert "Database error" in result["error"]


class TestGetNextMilestone:
    """Test get_next_milestone method"""

    @patch('src.tools.milestone_tools.get_project_manager')
    def test_get_next_milestone_found(self, mock_get_pm):
        """Test retrieval of next incomplete milestone"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pm = Mock()
        mock_pm.get_project_connection.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_get_pm.return_value = mock_pm

        # Mock milestone data
        mock_row = {
            "milestone_id": 2,
            "milestone_name": "Literature Search",
            "description": "Find 10 articles",
            "due_date": "2026-01-21",
            "status": "pending",
            "deliverables": '["10 peer-reviewed articles"]',
            "notes": "Use PubMed"
        }
        mock_cursor.fetchone.return_value = mock_row

        tools = MilestoneTools()
        result_json = tools.get_next_milestone()
        result = json.loads(result_json)

        assert result["id"] == 2
        assert result["name"] == "Literature Search"
        assert "days_until_due" in result
        assert "is_overdue" in result
        mock_conn.close.assert_called_once()

    @patch('src.tools.milestone_tools.get_project_manager')
    def test_get_next_milestone_all_completed(self, mock_get_pm):
        """Test when all milestones are completed"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pm = Mock()
        mock_pm.get_project_connection.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_get_pm.return_value = mock_pm

        mock_cursor.fetchone.return_value = None

        tools = MilestoneTools()
        result_json = tools.get_next_milestone()
        result = json.loads(result_json)

        assert "message" in result
        assert "completed" in result["message"].lower()


class TestGetMilestonesByDateRange:
    """Test get_milestones_by_date_range method"""

    @patch('src.tools.milestone_tools.get_project_manager')
    def test_get_milestones_by_date_range(self, mock_get_pm):
        """Test retrieval of milestones in date range"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pm = Mock()
        mock_pm.get_project_connection.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_get_pm.return_value = mock_pm

        mock_row = {
            "milestone_id": 1,
            "milestone_name": "December Milestone",
            "description": "Due in December",
            "due_date": "2025-12-17",
            "status": "pending",
            "completion_date": None,
            "deliverables": '["Task 1"]',
            "notes": ""
        }
        mock_cursor.fetchall.return_value = [mock_row]

        tools = MilestoneTools()
        result_json = tools.get_milestones_by_date_range("2025-12-01", "2025-12-31")
        result = json.loads(result_json)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["due_date"] == "2025-12-17"
        mock_conn.execute.assert_called_once()


class TestUpdateMilestoneStatus:
    """Test update_milestone_status method"""

    @patch('src.tools.milestone_tools.get_project_manager')
    def test_update_status_to_completed(self, mock_get_pm):
        """Test updating milestone status to completed"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pm = Mock()
        mock_pm.get_project_connection.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_get_pm.return_value = mock_pm

        # Mock the SELECT query result
        mock_row = {
            "milestone_name": "PICOT Development",
            "status": "completed",
            "completion_date": "2025-11-27"
        }
        mock_cursor.fetchone.return_value = mock_row

        tools = MilestoneTools()
        result_json = tools.update_milestone_status(1, "completed")
        result = json.loads(result_json)

        assert result["success"] is True
        assert result["milestone_id"] == 1
        assert result["new_status"] == "completed"
        assert result["completion_date"] == "2025-11-27"
        mock_conn.commit.assert_called_once()

    @patch('src.tools.milestone_tools.get_project_manager')
    def test_update_status_invalid_status(self, mock_get_pm):
        """Test updating with invalid status"""
        mock_pm = Mock()
        mock_get_pm.return_value = mock_pm

        tools = MilestoneTools()
        result_json = tools.update_milestone_status(1, "invalid_status")
        result = json.loads(result_json)

        assert "error" in result
        assert "Invalid status" in result["error"]


class TestAddMilestone:
    """Test add_milestone method"""

    @patch('src.tools.milestone_tools.get_project_manager')
    def test_add_milestone_success(self, mock_get_pm):
        """Test successful milestone addition"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pm = Mock()
        mock_pm.get_project_connection.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_get_pm.return_value = mock_pm

        mock_cursor.lastrowid = 7

        tools = MilestoneTools()
        result_json = tools.add_milestone(
            name="Custom Milestone",
            due_date="2026-03-15",
            description="Custom task",
            deliverables=["Deliverable 1", "Deliverable 2"]
        )
        result = json.loads(result_json)

        assert result["success"] is True
        assert result["milestone_id"] == 7
        assert result["name"] == "Custom Milestone"
        assert result["deliverables"] == ["Deliverable 1", "Deliverable 2"]
        assert result["status"] == "pending"
        mock_conn.commit.assert_called_once()

    @patch('src.tools.milestone_tools.get_project_manager')
    def test_add_milestone_without_deliverables(self, mock_get_pm):
        """Test adding milestone without deliverables"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pm = Mock()
        mock_pm.get_project_connection.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor
        mock_get_pm.return_value = mock_pm

        mock_cursor.lastrowid = 8

        tools = MilestoneTools()
        result_json = tools.add_milestone(
            name="Simple Milestone",
            due_date="2026-04-01"
        )
        result = json.loads(result_json)

        assert result["success"] is True
        assert result["deliverables"] == []
