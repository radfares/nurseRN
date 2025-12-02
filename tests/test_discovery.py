
import pytest
import inspect
from unittest.mock import MagicMock
from src.services.api_tools import apply_in_place_wrapper

class DiscoveryTool:
    def method_one(self): pass
    def method_two(self): pass

def test_methods_present():
    tool = DiscoveryTool()
    apply_in_place_wrapper(tool, ["method_one", "method_two"], lambda: MagicMock())
    
    methods = [m for m in dir(tool) if not m.startswith("_")]
    assert "method_one" in methods
    assert "method_two" in methods
    
    members = dict(inspect.getmembers(tool, inspect.isroutine))
    assert "method_one" in members
    assert "method_two" in members
