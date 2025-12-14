
import pytest
import inspect
import pickle
import threading
from unittest.mock import MagicMock, patch
from src.services.api_tools import apply_in_place_wrapper

class MockBreaker:
    def __init__(self):
        self.calls = 0
    def call(self, func, *args, **kwargs):
        self.calls += 1
        return func(*args, **kwargs)

class SimpleTool:
    def __init__(self):
        self.value = 0
    
    def action(self, x):
        """Original docstring."""
        self.value += x
        return self.value

@pytest.fixture
def tool():
    return SimpleTool()

def get_mock_breaker():
    return MockBreaker()

def test_methods_are_bound(tool):
    apply_in_place_wrapper(tool, ["action"], get_mock_breaker)
    assert inspect.ismethod(tool.action)
    assert tool.action.__self__ is tool

def test_signature_preserved(tool):
    # Compare against BOUND original method signature
    # inspect.signature on a bound method drops 'self', which is what we want
    orig_sig = inspect.signature(SimpleTool().action)
    apply_in_place_wrapper(tool, ["action"], get_mock_breaker)
    new_sig = inspect.signature(tool.action)
    assert str(orig_sig) == str(new_sig)
    assert tool.action.__doc__ == "Original docstring."

def test_delegation_calls_underlying(tool):
    apply_in_place_wrapper(tool, ["action"], get_mock_breaker)
    
    res = tool.action(5)
    assert res == 5
    assert tool.value == 5
    
    breaker = getattr(tool, "_breaker_action")
    assert breaker.calls == 1

def test_pickling_roundtrip(tool):
    apply_in_place_wrapper(tool, ["action"], get_mock_breaker)
    
    # Pickle and unpickle
    dumped = pickle.dumps(tool)
    loaded = pickle.loads(dumped)
    
    assert loaded.value == 0
    
    # Action should still work
    res = loaded.action(10)
    assert res == 10
    assert loaded.value == 10

def test_unwrap_restores_original(tool):
    apply_in_place_wrapper(tool, ["action"], get_mock_breaker)
    assert hasattr(tool, "_orig_action")
    
    tool._unwrap_method("action")
    assert not hasattr(tool, "_orig_action")
    assert tool.action(3) == 3
    # Should be original method now
    assert not hasattr(tool.action, "__wrapped__")
