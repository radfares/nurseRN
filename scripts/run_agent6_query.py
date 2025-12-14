#!/usr/bin/env python3
"""
Helper to run DataAnalysisAgent (Agent 6) with a given query and
print the validated structured JSON (DataAnalysisOutput).

Usage:
  python3 scripts/run_agent6_query.py
  python3 scripts/run_agent6_query.py "your question here"
"""

import json
import os
import sys

from dotenv import load_dotenv, find_dotenv
from agents.data_analysis_agent import (
    data_analysis_agent,
    DataAnalysisOutput,
    MethodInfo,
    Parameters,
    SampleSize,
)


# Load environment variables from .env if present (project root or parent)
load_dotenv(find_dotenv(usecwd=True), override=False)

DEFAULT_QUERY = (
    "I need to compare hand hygiene compliance rates between two hospital units. "
    "Unit A has 30 nurses, Unit B has 25 nurses. I'll measure compliance before and after an intervention. "
    "What statistical test should I use and what sample size do I need?"
)


def main() -> int:
    if os.getenv("OPENAI_API_KEY") in (None, ""):
        print("[WARN] OPENAI_API_KEY not set; model call will fail.")

    query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUERY

    if data_analysis_agent is None:
        print("❌ DataAnalysisAgent failed to initialize. Check logs and configuration.")
        return 2

    print("[INFO] Running DataAnalysisAgent with provided query...\n")
    response = data_analysis_agent.run(query)

    content = response.content
    if not isinstance(content, DataAnalysisOutput):
        print("❌ output_schema validation did not produce a DataAnalysisOutput instance.")
        # Print raw content for debugging
        print("Raw content:")
        print(response.get_content_as_string(indent=2))
        return 3

    # Verify key nested models exist and are correctly typed
    if not isinstance(content.method, MethodInfo):
        print("❌ Missing/invalid MethodInfo in response.")
        return 4
    if not isinstance(content.parameters, Parameters):
        print("❌ Missing/invalid Parameters in response.")
        return 5
    if not isinstance(content.sample_size, SampleSize):
        print("❌ Missing/invalid SampleSize in response.")
        return 6

    # Print structured JSON
    print("\n[OK] output_schema validation passed. Structured JSON:")
    print(content.model_dump_json(indent=2, exclude_none=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
