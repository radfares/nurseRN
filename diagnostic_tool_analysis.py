
import sys
import os
import inspect
import json
import pickle
import logging
import time
import threading
from functools import wraps
from unittest.mock import MagicMock, patch

# Setup logging to capture telemetry
log_capture = []
class ListHandler(logging.Handler):
    def emit(self, record):
        log_capture.append(record.getMessage())

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("src.services.api_tools")
logger.addHandler(ListHandler())

# Add project root
sys.path.insert(0, os.getcwd())

# Mock Breaker
class MockBreaker:
    def __init__(self, name="MockBreaker"):
        self.name = name
        self.state = "closed"
        self.calls = 0
        self.failures = 0
    
    def call(self, func, *args, **kwargs):
        self.calls += 1
        return func(*args, **kwargs)

def mock_call_with_breaker(breaker, func, fallback, *args, **kwargs):
    if breaker:
        return breaker.call(func, *args, **kwargs)
    return func(*args, **kwargs)

def run_diagnostics():
    # Patch environment
    env_patch = {
        "EXA_API_KEY": "dummy",
        "SERP_API_KEY": "dummy",
        "PUBMED_EMAIL": "dummy@example.com",
        "OPENAI_API_KEY": "dummy",
        "SEMANTIC_SCHOLAR_API_KEY": "dummy",
        "CORE_API_KEY": "dummy",
    }
    
    with patch.dict(os.environ, env_patch):
        # Import api_tools
        try:
            import src.services.api_tools as api_tools
        except ImportError as e:
            print(json.dumps([{"error": f"Import failed: {e}"}]))
            return

        # Inject mocks
        api_tools.EXA_BREAKER = MockBreaker("EXA")
        api_tools.SERP_BREAKER = MockBreaker("SERP")
        api_tools.PUBMED_BREAKER = MockBreaker("PUBMED")
        api_tools.ARXIV_BREAKER = MockBreaker("ARXIV")
        api_tools.CLINICALTRIALS_BREAKER = MockBreaker("CLINICALTRIALS")
        api_tools.MEDRXIV_BREAKER = MockBreaker("MEDRXIV")
        api_tools.SEMANTIC_SCHOLAR_BREAKER = MockBreaker("SEMANTIC_SCHOLAR")
        api_tools.CORE_BREAKER = MockBreaker("CORE")
        api_tools.DOAJ_BREAKER = MockBreaker("DOAJ")
        
        api_tools.call_with_breaker = mock_call_with_breaker

        creators = [
            ("PubMed", api_tools.create_pubmed_tools_safe),
            ("Exa", api_tools.create_exa_tools_safe),
            ("Serp", api_tools.create_serp_tools_safe),
        ]

        results = []

        for name, creator in creators:
            report = {
                "tool_name": name,
                "expected_methods": [],
                "observed_methods": [],
                "identity_preserved": False,
                "signature_mismatches": [],
                "binding_issues": [],
                "execution_result": {"success": False, "logs": "", "exceptions": []},
                "breaker_behavior": {"calls": 0, "state": "unknown"},
                "concurrency_issues": [],
                "serialization_ok": False,
                "telemetry_ok": False,
                "unwrap_api_present": False,
                "notes": ""
            }

            try:
                # Create tool
                tool = creator()
                if not tool:
                    report["notes"] = "Tool creation returned None"
                    results.append(report)
                    continue

                # 1. Identity
                # In-place wrapping should preserve the class name (not end in Wrapper)
                report["identity_preserved"] = not type(tool).__name__.endswith("Wrapper")

                # 2. Discovery
                # Get expected methods from the class
                tool_class = type(tool)
                expected = [m[0] for m in inspect.getmembers(tool_class, predicate=inspect.isroutine) if not m[0].startswith("_")]
                report["expected_methods"] = expected
                
                # Get observed methods from the instance
                observed = [m for m in dir(tool) if not m.startswith("_") and callable(getattr(tool, m))]
                report["observed_methods"] = observed

                # 3. Integrity & Binding
                for method_name in observed:
                    method = getattr(tool, method_name)
                    
                    # Check if wrapped
                    is_wrapped = hasattr(method, "__wrapped__")
                    if is_wrapped:
                        report["unwrap_api_present"] = True
                    
                    # Check signature
                    try:
                        inspect.signature(method)
                    except ValueError:
                        report["signature_mismatches"].append(method_name)
                    
                    # Check binding
                    if not inspect.ismethod(method):
                        # If it's a function on an instance, it might be an issue, 
                        # but functools.wraps on a method often returns a function if not carefully bound.
                        # However, Python 3 handles this well.
                        # Let's flag it if it's NOT a bound method.
                        report["binding_issues"].append(f"{method_name} (type: {type(method)})")

                # 4. Execution & Breaker
                # Try to call a method to trigger breaker
                if observed:
                    method_name = observed[0]
                    method = getattr(tool, method_name)
                    
                    # Reset logs
                    log_capture.clear()
                    
                    try:
                        # Call with no args - likely raises TypeError but should trigger breaker first
                        method()
                    except:
                        pass
                    
                    # Check breaker
                    breaker = getattr(api_tools, f"{name.upper()}_BREAKER", None)
                    if breaker:
                        report["breaker_behavior"]["calls"] = breaker.calls
                        report["breaker_behavior"]["state"] = breaker.state
                        if breaker.calls > 0:
                            report["execution_result"]["success"] = True
                            report["execution_result"]["logs"] = "Breaker invoked"
                    
                    # Check telemetry
                    if any(name in l for l in log_capture):
                        report["telemetry_ok"] = True

                # 5. Serialization
                try:
                    pickle.dumps(tool)
                    report["serialization_ok"] = True
                except Exception as e:
                    report["serialization_ok"] = False
                    report["notes"] += f" Serialization failed: {e}"

                results.append(report)

            except Exception as e:
                report["notes"] = f"Analysis failed: {e}"
                results.append(report)

        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_diagnostics()
