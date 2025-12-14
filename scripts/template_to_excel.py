#!/usr/bin/env python3
"""
Generate an Excel data-collection template from Agent 6 (DataAnalysisAgent)
for a given nursing research question. Prints:
  1) Data collection template (columns)
  2) Recommended statistical method
  3) Analysis steps
and creates data_template.xlsx with a data sheet and a codebook sheet.

Usage:
  python3 scripts/template_to_excel.py "YOUR QUESTION HERE"
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

# Ensure project root is on path and load .env
try:
    from dotenv import load_dotenv, find_dotenv  # type: ignore
except Exception:
    print("[WARN] python-dotenv not found; continuing without auto .env loading")
    def load_dotenv(*args, **kwargs):
        return False
    def find_dotenv(*args, **kwargs):
        return ""

ROOT = Path(__file__).resolve().parents[1]
AGNO_PATH = ROOT / "libs" / "agno"
if str(AGNO_PATH) not in sys.path:
    sys.path.insert(0, str(AGNO_PATH))

load_dotenv(find_dotenv(usecwd=True), override=False)

from agents.data_analysis_agent import data_analysis_agent  # type: ignore
from xlsxwriter import Workbook  # type: ignore


def to_list(val):
    return list(val) if isinstance(val, (list, tuple)) else ([] if val is None else [val])


def build_excel_from_template(columns: List[dict], xlsx_path: Path) -> dict:
    """Create an Excel workbook with a data sheet and a codebook sheet.

    Returns a dictionary with:
      - headers: list of column names
      - dropdowns: mapping of column name -> allowed values (if any)
    """
    wb = Workbook(str(xlsx_path))
    ws = wb.add_worksheet("data")
    codebook = wb.add_worksheet("codebook")

    header_fmt = wb.add_format({"bold": True, "bg_color": "#DCE6F1", "border": 1})
    normal_fmt = wb.add_format({"border": 1})

    headers = [c.get("name", "") for c in columns]
    for col_idx, h in enumerate(headers):
        ws.write(0, col_idx, h, header_fmt)
        ws.set_column(col_idx, col_idx, max(10, len(h) + 2))
    ws.freeze_panes(1, 0)

    # Codebook headers
    cb_headers = ["name", "type", "allowed", "notes"]
    for i, h in enumerate(cb_headers):
        codebook.write(0, i, h, header_fmt)

    dropdowns = {}
    for r, col in enumerate(columns, start=1):
        name = col.get("name", "")
        ctype = col.get("type", "")
        allowed = col.get("allowed") or []
        notes = col.get("notes") or ""

        codebook.write(r, 0, name, normal_fmt)
        codebook.write(r, 1, ctype, normal_fmt)
        codebook.write(r, 2, ", ".join(allowed), normal_fmt)
        codebook.write(r, 3, notes, normal_fmt)

        # Add dropdown validation for categorical columns with allowed values
        if ctype == "categorical" and isinstance(allowed, list) and allowed:
            dropdowns[name] = allowed
            col_index = headers.index(name)
            # Apply validation for rows 2..1000 (adjust as needed)
            ws.data_validation(1, col_index, 999, col_index, {
                "validate": "list",
                "source": allowed,
                "error_title": "Invalid value",
                "error_message": f"Choose a value from the dropdown for {name}",
                "show_error": True,
            })

    wb.close()
    return {"headers": headers, "dropdowns": dropdowns}


def main() -> int:
    if data_analysis_agent is None:
        print("❌ DataAnalysisAgent failed to initialize. Check setup.")
        return 2

    if len(sys.argv) < 2:
        print("Usage: python3 scripts/template_to_excel.py \"YOUR QUESTION\"")
        return 64

    question = sys.argv[1]
    print("[INFO] Running Agent 6 (DataAnalysisAgent) ...\n")
    run = data_analysis_agent.run(question)
    content = run.content

    # 1) Data collection template
    tmpl = content.data_template.model_dump()
    columns = tmpl.get("columns", [])
    print("== Data Collection Template ==")
    for c in columns:
        name = c.get("name")
        ctype = c.get("type")
        allowed = ", ".join(to_list(c.get("allowed") or []))
        notes = c.get("notes") or ""
        print(f"- {name} [{ctype}]" + (f"  allowed: {allowed}" if allowed else "") + (f"  notes: {notes}" if notes else ""))

    # 2) Recommended statistical method
    method = content.method
    print("\n== Recommended Statistical Method ==")
    print(f"- {method.name}")
    print(f"  rationale: {method.justification}")
    if method.alternatives:
        print(f"  alternatives: {', '.join(method.alternatives)}")

    # 3) Analysis steps
    print("\n== Analysis Steps ==")
    for i, step in enumerate(content.analysis_steps, start=1):
        print(f"{i}. {step}")

    # Create Excel
    xlsx_path = ROOT / "data_template.xlsx"
    result = build_excel_from_template(columns, xlsx_path)
    print("\n[OK] Excel file created:", xlsx_path)
    print("Headers:", ", ".join(result["headers"]))
    if result["dropdowns"]:
        print("Dropdowns:")
        for col, values in result["dropdowns"].items():
            print(f"- {col}: {', '.join(values)}")
    else:
        print("No dropdowns added.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

