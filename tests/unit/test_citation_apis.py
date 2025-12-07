"""
Unit tests for Citation API clients - Phase 3
Tests API integration with mocked responses.

Gate 3 Checkpoint Tests:
- G3.1: PubMed retraction checker with mocked API
- G3.2: Rate limiting verification
- G3.3: Circuit breaker integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time


class TestPubMedRetractionChecker:
    """Test PubMed retraction checking with mocked API"""
    
    @patch('src.services.citation_apis.httpx.get')
    def test_non_retracted_article(self, mock_get):
        """Non-retracted article should return is_retracted=False"""
        from src.services.citation_apis import PubMedRetractionChecker
        
        # Mock response for non-retracted article
        mock_response = Mock()
        mock_response.json.return_value = {
            "esearchresult": {"count": "0", "idlist": []}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        checker = PubMedRetractionChecker()
        result = checker.check_retraction("12345678")
        
        assert result.is_retracted == False
        assert result.source == "pubmed"
    
    @patch('src.services.citation_apis.httpx.get')
    def test_retracted_article(self, mock_get):
        """Retracted article should return is_retracted=True"""
        from src.services.citation_apis import PubMedRetractionChecker
        
        # Mock response for retracted article
        mock_response = Mock()
        mock_response.json.return_value = {
            "esearchresult": {"count": "1", "idlist": ["99999999"]}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        checker =PubMedRetractionChecker()
        result = checker.check_retraction("12345678")
        
        assert result.is_retracted == True
        assert result.retraction_type == "retraction"
        assert result.source == "pubmed"
    
    @patch('src.services.citation_apis.call_with_breaker')
    def test_api_http_error_handling(self, mock_call_with_breaker):
        """HTTP errors should be handled by circuit breaker"""
        from src.services.citation_apis import PubMedRetractionChecker
        
        # Mock circuit breaker returning fallback on error
        mock_call_with_breaker.return_value = "PubMed retraction check unavailable"
        
        checker = PubMedRetractionChecker()
        result = checker.check_retraction("12345678")
        
        assert result.is_retracted == False
        assert result.source == "circuit_breaker_fallback"
    
    @patch('src.services.citation_apis.call_with_breaker')
    def test_api_generic_error_handling(self, mock_call_with_breaker):
        """Generic errors should be handled by circuit breaker"""
        from src.services.citation_apis import PubMedRetractionChecker
        
        # Mock circuit breaker returning fallback
        mock_call_with_breaker.return_value = "Service unavailable"
        
        checker = PubMedRetractionChecker()
        result = checker.check_retraction("12345678")
        
        assert result.is_retracted == False
        assert result.source == "circuit_breaker_fallback"
    
    def test_rate_limiting_enforced(self):
        """Rate limiting should enforce delay between requests"""
        from src.services.citation_apis import PubMedRetractionChecker
        
        checker = PubMedRetractionChecker()
        checker._last_request_time = time.time()
        
        start = time.time()
        checker._rate_limit()
        elapsed = time.time() - start
        
        # Should have waited at least 0.3 seconds
        assert elapsed >= 0.3
    
    @patch('src.services.citation_apis.httpx.get')
    def test_batch_checking(self, mock_get):
        """Batch checking should process multiple PMIDs"""
        from src.services.citation_apis import PubMedRetractionChecker
        
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "esearchresult": {"count": "0", "idlist": []}
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        checker = PubMedRetractionChecker()
        results = checker.check_batch(["111", "222", "333"])
        
        assert len(results) == 3
        assert "111" in results
        assert "222" in results
        assert "333" in results


class TestCircuitBreakerIntegration:
    """Test circuit breaker integration"""
    
    @patch('src.services.citation_apis.call_with_breaker')
    def test_circuit_breaker_used(self, mock_call_with_breaker):
        """Retraction checker should use circuit breaker"""
        from src.services.citation_apis import PubMedRetractionChecker
        
        # Mock circuit breaker returning successful result
        mock_call_with_breaker.return_value = {
            "esearchresult": {"count": "0", "idlist": []}
        }
        
        checker = PubMedRetractionChecker()
        result = checker.check_retraction("12345678")
        
        # Verify circuit breaker was called
        assert mock_call_with_breaker.called
        assert result.is_retracted == False
    
    @patch('src.services.citation_apis.call_with_breaker')
    def test_circuit_breaker_fallback(self, mock_call_with_breaker):
        """Circuit breaker fallback should be handled"""
        from src.services.citation_apis import PubMedRetractionChecker
        
        # Mock circuit breaker returning fallback string
        mock_call_with_breaker.return_value = "Service unavailable"
        
        checker = PubMedRetractionChecker()
        result = checker.check_retraction("12345678")
        
        assert result.is_retracted == False
        assert result.source == "circuit_breaker_fallback"


class TestValidationToolsWithRetraction:
    """Test validation tools integration with retraction checking"""
    
    @patch('src.services.citation_apis.PubMedRetractionChecker.check_retraction')
    def test_validation_checks_retraction(self, mock_check):
        """ValidationTools should call retraction checker"""
        from src.tools.validation_tools import ValidationTools
        from src.services.citation_apis import RetractionStatus
        
        # Mock non-retracted
        mock_check.return_value = RetractionStatus(
            is_retracted=False,
            source="pubmed"
        )
        
        tool = ValidationTools()
        result = tool.validate_article(
            pmid="12345678",
            title="Test Article",
            abstract="This is a test.",
            publication_date="2024-01-01",
            check_retraction=True
        )
        
        # Should have called retraction checker
        assert mock_check.called
        assert result.is_retracted == False
    
    @patch('src.services.citation_apis.PubMedRetractionChecker.check_retraction')
    def test_validation_detects_retraction(self, mock_check):
        """ValidationTools should detect retracted articles"""
        from src.tools.validation_tools import ValidationTools
        from src.services.citation_apis import RetractionStatus
        
        # Mock retracted
        mock_check.return_value = RetractionStatus(
            is_retracted=True,
            retraction_type="retraction",
            retraction_reason="Data fabrication",
            source="pubmed"
        )
        
        tool = ValidationTools()
        result = tool.validate_article(
            pmid="99999999",
            title="Retracted Article",
            abstract="This article was retracted.",
            publication_date="2024-01-01",
            check_retraction=True
        )
        
        assert result.is_retracted == True
        assert result.recommendation == "exclude"
        assert "RETRACTED" in result.issues[0]
    
    def test_validation_skip_retraction_check(self):
        """ValidationTools should allow skipping retraction check"""
        from src.tools.validation_tools import ValidationTools
        
        tool = ValidationTools()
        result = tool.validate_article(
            pmid="12345678",
            title="Test Article",
            abstract="This is a test.",
            publication_date="2024-01-01",
            check_retraction=False  # Skip API call
        )
        
        # Should complete without calling API
        assert result.is_retracted == False
