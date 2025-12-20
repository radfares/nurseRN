import pytest

from src.services import api_tools


def test_tavily_returns_none_without_key(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    assert api_tools.create_tavily_tools_safe(required=False) is None
    with pytest.raises(ValueError):
        api_tools.create_tavily_tools_safe(required=True)


def test_tavily_wrapped_with_breaker(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    class DummyTavily:
        def __init__(self, *args, **kwargs):
            pass

        def web_search_using_tavily(self, query: str, max_results: int = 5):
            raise RuntimeError("boom")

        def extract_url_content(self, urls: str):
            raise RuntimeError("boom")

    monkeypatch.setattr("agno.tools.tavily.TavilyTools", DummyTavily)

    tool = api_tools.create_tavily_tools_safe(required=True)

    res_search = tool.web_search_using_tavily("test")
    res_extract = tool.extract_url_content("https://example.com")

    assert isinstance(res_search, dict)
    assert res_search.get("error") in {"api_error", "service_unavailable"}
    assert isinstance(res_extract, dict)
    assert res_extract.get("error") in {"api_error", "service_unavailable"}
