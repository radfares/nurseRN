from pathlib import Path

import types

import sys
import types

# Stub TavilyReader to avoid external dependency during import
tavily_stub = types.ModuleType('agno.knowledge.reader.tavily_reader')

class _StubTavilyReader:
    def __init__(self, api_key: str, extract_format: str = "markdown", extract_depth: str = "basic", chunk: bool = True):
        self.api_key = api_key
        self.extract_format = extract_format
        self.extract_depth = extract_depth

    def read(self, url: str):
        return []

tavily_stub.TavilyReader = _StubTavilyReader
sys.modules['agno.knowledge.reader.tavily_reader'] = tavily_stub

from src.tools.readers_tools.document_reader_service import create_document_reader_tools_safe
import src.tools.readers_tools.document_reader_service as drs
import src.services.circuit_breaker as cb


class PassThroughBreaker:
    def __init__(self, name: str = "breaker"):
        self.name = name

    def call(self, func, *args, **kwargs):
        return func(*args, **kwargs)


class FailingBreaker:
    def __init__(self, name: str = "breaker"):
        self.name = name

    def call(self, func, *args, **kwargs):
        raise cb.CircuitBreakerError("open")


class SimpleDoc:
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content


def setup_pass_breakers(monkeypatch):
    monkeypatch.setattr(drs, "PDF_READER_BREAKER", PassThroughBreaker("pdf"))
    monkeypatch.setattr(drs, "PPTX_READER_BREAKER", PassThroughBreaker("pptx"))
    monkeypatch.setattr(drs, "WEBSITE_READER_BREAKER", PassThroughBreaker("web"))
    monkeypatch.setattr(drs, "TAVILY_READER_BREAKER", PassThroughBreaker("tavily"))
    monkeypatch.setattr(drs, "WEB_SEARCH_READER_BREAKER", PassThroughBreaker("search"))
    monkeypatch.setattr(drs, "ARXIV_READER_BREAKER", PassThroughBreaker("arxiv"))
    monkeypatch.setattr(drs, "CSV_READER_BREAKER", PassThroughBreaker("csv"))
    monkeypatch.setattr(drs, "JSON_READER_BREAKER", PassThroughBreaker("json"))


def setup_fail_breakers(monkeypatch):
    monkeypatch.setattr(drs, "PDF_READER_BREAKER", FailingBreaker("pdf"))
    monkeypatch.setattr(drs, "PPTX_READER_BREAKER", FailingBreaker("pptx"))
    monkeypatch.setattr(drs, "WEBSITE_READER_BREAKER", FailingBreaker("web"))
    monkeypatch.setattr(drs, "TAVILY_READER_BREAKER", FailingBreaker("tavily"))
    monkeypatch.setattr(drs, "WEB_SEARCH_READER_BREAKER", FailingBreaker("search"))
    monkeypatch.setattr(drs, "ARXIV_READER_BREAKER", FailingBreaker("arxiv"))
    monkeypatch.setattr(drs, "CSV_READER_BREAKER", FailingBreaker("csv"))
    monkeypatch.setattr(drs, "JSON_READER_BREAKER", FailingBreaker("json"))


def test_service_e2e_success(tmp_path, monkeypatch):
    setup_pass_breakers(monkeypatch)

    # Create temp CSV/JSON
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("x,y\n1,2\n", encoding="utf-8")
    json_path = tmp_path / "data.json"
    json_path.write_text("{""study"": ""Unit Test""}", encoding="utf-8")

    tools = create_document_reader_tools_safe("Test", str(Path.cwd() / "project.db"))

    # Patch underlying readers to avoid network
    def fake_arxiv_read(**kwargs):
        return [SimpleDoc("Paper A", "Methods")]

    tools.arxiv_reader.read = fake_arxiv_read  # type: ignore

    def fake_csv_read(path_str: str):  # type: ignore
        return [SimpleDoc("data.csv", Path(path_str).read_text(encoding="utf-8"))]

    def fake_json_read(path_str: str):  # type: ignore
        return [SimpleDoc("data.json", Path(path_str).read_text(encoding="utf-8"))]

    tools.csv_reader.read = fake_csv_read  # type: ignore
    tools.json_reader.read = fake_json_read  # type: ignore

    arxiv = tools.search_arxiv(["stats"], max_results=1)
    assert "Paper: Paper A" in arxiv

    csv_out = tools.read_csv(str(csv_path))
    assert "x,y" in csv_out
    assert "1,2" in csv_out

    json_out = tools.read_json(str(json_path))
    assert "Unit Test" in json_out


def test_service_e2e_circuit_open(monkeypatch):
    setup_fail_breakers(monkeypatch)

    tools = create_document_reader_tools_safe("Test", str(Path.cwd() / "project.db"))

    # Patch underlying readers so wrappers would attempt calls
    tools.arxiv_reader.read = lambda **kwargs: [SimpleDoc("Any", "X")]  # type: ignore
    tools.csv_reader.read = lambda p: [SimpleDoc("Any", "X")]  # type: ignore
    tools.json_reader.read = lambda p: [SimpleDoc("Any", "X")]  # type: ignore

    assert "temporarily unavailable" in tools.search_arxiv(["x"]).lower()
    assert "temporarily unavailable" in tools.read_csv("/tmp/does_not_matter.csv").lower()
    assert "temporarily unavailable" in tools.read_json("/tmp/does_not_matter.json").lower()
