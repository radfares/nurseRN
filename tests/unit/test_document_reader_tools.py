import os
from pathlib import Path
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

from src.tools.readers_tools.document_reader_tools import DocumentReaderTools


class SimpleDoc:
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content


def make_abs(path: str) -> str:
    return str((Path.cwd() / path).resolve())


def test_search_arxiv_smoke(monkeypatch):
    tools = DocumentReaderTools(project_name="Test", project_db_path=make_abs("project.db"))

    def fake_read(**kwargs):
        return [SimpleDoc("Method Paper", "Content about methods")]  # type: ignore

    monkeypatch.setattr(tools.arxiv_reader, "read", fake_read)

    result = tools.search_arxiv(["power analysis"], max_results=1)
    assert "Paper: Method Paper" in result
    assert "methods" in result.lower()


def test_read_csv_smoke(tmp_path, monkeypatch):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("col1,col2\nA,1\nB,2\n", encoding="utf-8")

    tools = DocumentReaderTools(project_name="Test", project_db_path=make_abs("project.db"))

    def fake_csv_read(path_str: str):  # type: ignore
        content = Path(path_str).read_text(encoding="utf-8")
        return [SimpleDoc("test.csv", content)]

    monkeypatch.setattr(tools.csv_reader, "read", fake_csv_read)

    result = tools.read_csv(str(csv_file))
    assert "col1,col2" in result
    assert "A,1" in result


def test_read_json_smoke(tmp_path, monkeypatch):
    json_file = tmp_path / "test.json"
    json_file.write_text("{""study"": ""Fall Prevention"", ""n"": 120}", encoding="utf-8")

    tools = DocumentReaderTools(project_name="Test", project_db_path=make_abs("project.db"))

    def fake_json_read(path_str: str):  # type: ignore
        content = Path(path_str).read_text(encoding="utf-8")
        return [SimpleDoc("test.json", content)]

    monkeypatch.setattr(tools.json_reader, "read", fake_json_read)

    result = tools.read_json(str(json_file))
    assert "Fall Prevention" in result
