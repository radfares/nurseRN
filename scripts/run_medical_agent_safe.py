#!/usr/bin/env python3
import sys, json, traceback
from typing import Any
try:
    from agents.medical_research_agent import get_medical_research_agent
except Exception as e:
    print("ERROR: failed to import medical_research_agent:", e)
    sys.exit(2)

def _print_result(res: Any) -> None:
    if isinstance(res, dict):
        # Prefer explicit content field
        if res.get("content"):
            print(res.get("content"))
            return
        # Fallback to messages if present
        msgs = res.get("messages") or res.get("message") or res.get("messages_list")
        if isinstance(msgs, list):
            for m in msgs:
                if isinstance(m, dict):
                    print(m.get("content") or m.get("text") or json.dumps(m, ensure_ascii=False))
                else:
                    print(str(m))
            return
        if msgs:
            print(str(msgs))
            return
        # Print whole dict for debugging (sanitized)
        print(json.dumps(res, indent=2, default=str))
        return
    print(str(res))

def main(query: str):
    agent = get_medical_research_agent()
    if agent is None:
        print("ERROR: agent not initialized")
        sys.exit(3)
    try:
        res = agent.run_with_grounding_check(query, project_name="test_project")
    except Exception as e:
        print("ERROR: model_provider_error")
        print(str(e))
        traceback.print_exc()
        sys.exit(4)
    # Defensive handling for missing messages
    if not isinstance(res, dict) or "messages" not in res:
        # Try to surface useful fields or show a clear error
        if isinstance(res, dict) and (res.get("tool_results") or res.get("content") or res.get("response")):
            _print_result(res)
            sys.exit(0)
        print("ERROR: missing_messages")
        _print_result(res)
        sys.exit(5)
    _print_result(res)
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: run_medical_agent_safe.py \"your query\"")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    main(query)
