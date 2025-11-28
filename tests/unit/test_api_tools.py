"""
Unit tests for api_tools.py
Tests the safe wrapper functions for new healthcare research APIs
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
import os

# Mock all external dependencies before importing
sys.modules['agno'] = MagicMock()
sys.modules['agno.tools'] = MagicMock()
sys.modules['agno.tools.clinicaltrials'] = MagicMock()
sys.modules['agno.tools.medrxiv'] = MagicMock()
sys.modules['agno.tools.semantic_scholar'] = MagicMock()
sys.modules['agno.tools.core'] = MagicMock()
sys.modules['agno.tools.doaj'] = MagicMock()

from src.services.api_tools import (
    create_clinicaltrials_tools_safe,
    create_medrxiv_tools_safe,
    create_semantic_scholar_tools_safe,
    create_core_tools_safe,
    create_doaj_tools_safe,
    build_tools_list,
    get_api_status,
)


class TestClinicalTrialsToolsSafe:
    """Test create_clinicaltrials_tools_safe function"""

    @patch('src.services.api_tools.CLINICALTRIALS_BREAKER')
    @patch('src.services.api_tools.CircuitProtectedToolWrapper')
    @patch('agno.tools.clinicaltrials.ClinicalTrialsTools')
    def test_create_clinicaltrials_tools_success(self, mock_tool_class, mock_wrapper, mock_breaker):
        """Test successful creation of ClinicalTrialsTools"""
        mock_tool_instance = Mock()
        mock_tool_class.return_value = mock_tool_instance
        mock_wrapped = Mock()
        mock_wrapper.return_value = mock_wrapped

        result = create_clinicaltrials_tools_safe(required=False)

        assert result == mock_wrapped
        mock_tool_class.assert_called_once_with(
            enable_search_clinicaltrials=True,
            max_results=10,
        )
        mock_wrapper.assert_called_once_with(mock_tool_instance, mock_breaker, "ClinicalTrials.gov API")

    @patch('agno.tools.clinicaltrials.ClinicalTrialsTools', side_effect=ImportError("Module not found"))
    def test_create_clinicaltrials_tools_import_error(self, mock_tool_class):
        """Test handling of ImportError"""
        result = create_clinicaltrials_tools_safe(required=False)
        assert result is None

    @patch('agno.tools.clinicaltrials.ClinicalTrialsTools', side_effect=ImportError("Module not found"))
    def test_create_clinicaltrials_tools_import_error_required(self, mock_tool_class):
        """Test that ImportError is raised when required=True"""
        with pytest.raises(ImportError):
            create_clinicaltrials_tools_safe(required=True)


class TestMedRxivToolsSafe:
    """Test create_medrxiv_tools_safe function"""

    @patch('src.services.api_tools.MEDRXIV_BREAKER')
    @patch('src.services.api_tools.CircuitProtectedToolWrapper')
    @patch('agno.tools.medrxiv.MedRxivTools')
    def test_create_medrxiv_tools_success(self, mock_tool_class, mock_wrapper, mock_breaker):
        """Test successful creation of MedRxivTools"""
        mock_tool_instance = Mock()
        mock_tool_class.return_value = mock_tool_instance
        mock_wrapped = Mock()
        mock_wrapper.return_value = mock_wrapped

        result = create_medrxiv_tools_safe(required=False)

        assert result == mock_wrapped
        mock_tool_class.assert_called_once_with(
            enable_search_medrxiv=True,
            enable_search_biorxiv=True,
            max_results=10,
        )
        mock_wrapper.assert_called_once_with(mock_tool_instance, mock_breaker, "medRxiv API")

    @patch('agno.tools.medrxiv.MedRxivTools', side_effect=ImportError("Module not found"))
    def test_create_medrxiv_tools_import_error(self, mock_tool_class):
        """Test handling of ImportError"""
        result = create_medrxiv_tools_safe(required=False)
        assert result is None


class TestSemanticScholarToolsSafe:
    """Test create_semantic_scholar_tools_safe function"""

    @patch('src.services.api_tools.SEMANTIC_SCHOLAR_BREAKER')
    @patch('src.services.api_tools.CircuitProtectedToolWrapper')
    @patch('agno.tools.semantic_scholar.SemanticScholarTools')
    @patch.dict(os.environ, {}, clear=True)
    def test_create_semantic_scholar_tools_success_no_key(self, mock_tool_class, mock_wrapper, mock_breaker):
        """Test successful creation without API key"""
        mock_tool_instance = Mock()
        mock_tool_class.return_value = mock_tool_instance
        mock_wrapped = Mock()
        mock_wrapper.return_value = mock_wrapped

        result = create_semantic_scholar_tools_safe(required=False)

        assert result == mock_wrapped
        mock_tool_class.assert_called_once_with(
            enable_search_semantic_scholar=True,
            max_results=10,
            api_key=None,
        )

    @patch('src.services.api_tools.SEMANTIC_SCHOLAR_BREAKER')
    @patch('src.services.api_tools.CircuitProtectedToolWrapper')
    @patch('agno.tools.semantic_scholar.SemanticScholarTools')
    @patch.dict(os.environ, {'SEMANTIC_SCHOLAR_API_KEY': 'test-key'}, clear=False)
    def test_create_semantic_scholar_tools_success_with_key(self, mock_tool_class, mock_wrapper, mock_breaker):
        """Test successful creation with API key"""
        mock_tool_instance = Mock()
        mock_tool_class.return_value = mock_tool_instance
        mock_wrapped = Mock()
        mock_wrapper.return_value = mock_wrapped

        result = create_semantic_scholar_tools_safe(required=False)

        assert result == mock_wrapped
        mock_tool_class.assert_called_once_with(
            enable_search_semantic_scholar=True,
            max_results=10,
            api_key='test-key',
        )


class TestCoreToolsSafe:
    """Test create_core_tools_safe function"""

    @patch('src.services.api_tools.CORE_BREAKER')
    @patch('src.services.api_tools.CircuitProtectedToolWrapper')
    @patch('agno.tools.core.CoreTools')
    @patch.dict(os.environ, {}, clear=True)
    def test_create_core_tools_success_no_key(self, mock_tool_class, mock_wrapper, mock_breaker):
        """Test successful creation without API key"""
        mock_tool_instance = Mock()
        mock_tool_class.return_value = mock_tool_instance
        mock_wrapped = Mock()
        mock_wrapper.return_value = mock_wrapped

        result = create_core_tools_safe(required=False)

        assert result == mock_wrapped
        mock_tool_class.assert_called_once_with(
            enable_search_core=True,
            max_results=10,
            api_key=None,
        )


class TestDoajToolsSafe:
    """Test create_doaj_tools_safe function"""

    @patch('src.services.api_tools.DOAJ_BREAKER')
    @patch('src.services.api_tools.CircuitProtectedToolWrapper')
    @patch('agno.tools.doaj.DoajTools')
    def test_create_doaj_tools_success(self, mock_tool_class, mock_wrapper, mock_breaker):
        """Test successful creation of DoajTools"""
        mock_tool_instance = Mock()
        mock_tool_class.return_value = mock_tool_instance
        mock_wrapped = Mock()
        mock_wrapper.return_value = mock_wrapped

        result = create_doaj_tools_safe(required=False)

        assert result == mock_wrapped
        mock_tool_class.assert_called_once_with(
            enable_search_doaj=True,
            max_results=10,
        )
        mock_wrapper.assert_called_once_with(mock_tool_instance, mock_breaker, "DOAJ API")


class TestGetApiStatus:
    """Test get_api_status function"""

    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_status_no_keys(self):
        """Test API status when no keys are set"""
        status = get_api_status()

        assert status['openai']['key_set'] is False
        assert status['clinicaltrials']['key_set'] is True  # Free API
        assert status['medrxiv']['key_set'] is True  # Free API
        assert status['semantic_scholar']['key_set'] is False
        assert status['core']['key_set'] is False
        assert status['doaj']['key_set'] is True  # Free API

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-key',
        'SEMANTIC_SCHOLAR_API_KEY': 'test-key',
        'CORE_API_KEY': 'test-key',
    }, clear=False)
    def test_get_api_status_with_keys(self):
        """Test API status when keys are set"""
        status = get_api_status()

        assert status['openai']['key_set'] is True
        assert status['semantic_scholar']['key_set'] is True
        assert status['core']['key_set'] is True


class TestBuildToolsList:
    """Test build_tools_list function"""

    def test_build_tools_list_filters_none(self):
        """Test that build_tools_list filters out None values"""
        tool1 = Mock()
        tool2 = Mock()
        result = build_tools_list(tool1, None, tool2, None)

        assert len(result) == 2
        assert tool1 in result
        assert tool2 in result
        assert None not in result

    def test_build_tools_list_all_none(self):
        """Test build_tools_list with all None values"""
        result = build_tools_list(None, None, None)
        assert len(result) == 0

    def test_build_tools_list_all_valid(self):
        """Test build_tools_list with all valid tools"""
        tool1 = Mock()
        tool2 = Mock()
        tool3 = Mock()
        result = build_tools_list(tool1, tool2, tool3)

        assert len(result) == 3
        assert tool1 in result
        assert tool2 in result
        assert tool3 in result

