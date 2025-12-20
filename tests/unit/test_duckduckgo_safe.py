import pytest

from src.services.api_tools import create_duckduckgo_tools_safe


def test_duckduckgo_search_returns_fallback_on_error(monkeypatch):
    """DuckDuckGo search should not raise even if the underlying call fails."""
    from agno.tools.duckduckgo import DuckDuckGoTools

    def boom(self, query, max_results=5):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(DuckDuckGoTools, "duckduckgo_search", boom)

    tool = create_duckduckgo_tools_safe(required=True)
    result = tool.duckduckgo_search("fall prevention")

    assert isinstance(result, dict)
    assert result.get("error") in {"api_error", "service_unavailable"}
    assert "unavailable" in result.get("message", "")
