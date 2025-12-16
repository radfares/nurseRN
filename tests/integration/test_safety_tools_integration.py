"""
Integration test: SafetyTools wiring (offline-safe).

This verifies the SafetyTools wrapper can be created and exposes expected methods,
without making any external OpenFDA network calls.
"""

from src.services.api_tools import create_safety_tools_safe


def test_create_safety_tools_safe_instantiates():
    tool = create_safety_tools_safe(required=False)
    assert tool is not None

    # Contract: tool exposes these methods, but we don't call them (they may hit network).
    assert hasattr(tool, "verify_access")
    assert hasattr(tool, "get_device_recalls")
    assert hasattr(tool, "get_drug_adverse_events")

