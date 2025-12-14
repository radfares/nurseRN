#!/usr/bin/env python3
"""
Nursing Research Assistant - Unified Interface

ONE COMMAND. ONE FLOW. ALL FEATURES.

Usage:
    python run_research.py
    python run_research.py "fall prevention in elderly patients"

This is the streamlined interface that runs the complete unified pipeline.
"""

from dotenv import load_dotenv
load_dotenv(override=True)

import sys
from pathlib import Path

# Ensure vendored agno library is importable
_project_root = Path(__file__).parent
_agno_path = _project_root / "libs" / "agno"
if _agno_path.exists() and str(_agno_path) not in sys.path:
    sys.path.insert(0, str(_agno_path))

from project_manager import get_project_manager, cli_create_project, cli_list_projects
from src.workflows.unified_research_pipeline import UnifiedResearchPipeline, run_unified_pipeline


def show_disclaimer() -> bool:
    """Display clinical disclaimer."""
    print("\n" + "="*70)
    print("CLINICAL DISCLAIMER".center(70))
    print("="*70)
    print("""
This is a QUALITY IMPROVEMENT PLANNING TOOL.

- NOT a substitute for clinical judgment
- NOT medical advice or clinical decision support
- ALL outputs must be reviewed by clinical experts
- You are responsible for institutional approvals

By continuing, you acknowledge these terms.
""")
    print("="*70)

    response = input("\nType 'yes' to continue: ").strip().lower()
    return response in ['yes', 'y']


def show_welcome(project_name: str):
    """Display welcome message."""
    print("\n" + "="*70)
    print("NURSING RESEARCH ASSISTANT".center(70))
    print("="*70)
    print(f"\nProject: {project_name}")
    print("\nThis tool runs a complete research pipeline:")
    print("  1. PICOT Question Generation")
    print("  2. Literature Search (PubMed)")
    print("  3. Citation Validation")
    print("  4. Evidence Synthesis")
    print("  5. Data Analysis Planning")
    print("  6. Timeline & Milestones")
    print("\nAll steps run automatically in sequence.")
    print("="*70)


def show_results(result):
    """Display pipeline results."""
    print("\n" + "="*70)
    print("RESEARCH RESULTS".center(70))
    print("="*70)

    # PICOT
    print("\n" + "-"*70)
    print("PICOT QUESTION")
    print("-"*70)
    picot = result.outputs.get("picot", "Not generated")
    print(picot[:800] if len(picot) > 800 else picot)

    # Articles
    print("\n" + "-"*70)
    print("ARTICLES FOUND")
    print("-"*70)
    pmids = result.outputs.get("pmids", [])
    valid = result.outputs.get("valid_pmids", pmids)
    retracted = result.outputs.get("retracted_pmids", [])
    print(f"Total: {len(pmids)} | Valid: {len(valid)} | Retracted: {len(retracted)}")
    print(f"PMIDs: {', '.join(pmids[:10])}")
    if len(pmids) > 10:
        print(f"  ... and {len(pmids) - 10} more")

    # Synthesis preview
    print("\n" + "-"*70)
    print("LITERATURE SYNTHESIS (Preview)")
    print("-"*70)
    synthesis = result.outputs.get("synthesis", "Not generated")
    print(synthesis[:600] + "..." if len(synthesis) > 600 else synthesis)

    # Analysis plan preview
    print("\n" + "-"*70)
    print("ANALYSIS PLAN (Preview)")
    print("-"*70)
    analysis = result.outputs.get("analysis_plan", "Not generated")
    print(str(analysis)[:400] + "..." if len(str(analysis)) > 400 else analysis)

    # Milestones
    print("\n" + "-"*70)
    print("PROJECT MILESTONES")
    print("-"*70)
    milestones = result.outputs.get("milestones", [])
    for i, m in enumerate(milestones[:5], 1):
        name = m.get("name", "Unknown") if isinstance(m, dict) else str(m)
        status = m.get("status", "pending") if isinstance(m, dict) else "pending"
        print(f"  {i}. {name} [{status}]")
    if len(milestones) > 5:
        print(f"  ... and {len(milestones) - 5} more")

    print("\n" + "="*70)
    print("Results saved to project database.")
    print("="*70)


def get_or_create_project() -> str:
    """Ensure a project exists and is active."""
    pm = get_project_manager()
    projects = pm.list_projects()
    active = pm.get_active_project()

    if active:
        return active

    if not projects:
        print("\nNo projects found. Creating default project...")
        cli_create_project("research_project", add_milestones=True)
        return "research_project"

    print("\nAvailable projects:")
    cli_list_projects()
    choice = input("\nEnter project name to use: ").strip()

    if choice in projects:
        pm.switch_project(choice)
        return choice
    else:
        print(f"Creating new project: {choice}")
        cli_create_project(choice, add_milestones=True)
        return choice


def run_interactive():
    """Run interactive mode."""
    # Get project
    project_name = get_or_create_project()
    show_welcome(project_name)

    while True:
        print("\n" + "-"*70)
        topic = input("\nEnter research topic (or 'exit' to quit): ").strip()

        if not topic:
            print("Please enter a topic.")
            continue

        if topic.lower() in ['exit', 'quit', 'q']:
            print("\nGoodbye!")
            break

        print(f"\nStarting research pipeline for: {topic}")
        print("This will take 1-3 minutes...\n")

        try:
            result = run_unified_pipeline(topic, project_name)

            if result.success:
                show_results(result)
            else:
                print(f"\nPipeline failed: {result.error}")
                print("Check logs for details.")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'exit' to quit or enter a new topic.")
            continue

        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()

        # Ask if they want to run again
        again = input("\nRun another topic? (yes/no): ").strip().lower()
        if again not in ['yes', 'y']:
            print("\nGoodbye!")
            break


def main():
    """Main entry point."""
    # Check for disclaimer skip (for testing)
    skip_disclaimer = "--skip-disclaimer" in sys.argv

    if not skip_disclaimer:
        if not show_disclaimer():
            print("Exiting.")
            sys.exit(1)

    # Check if topic provided as argument
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if args:
        # Direct execution with topic
        topic = " ".join(args)
        project_name = get_or_create_project()
        show_welcome(project_name)

        print(f"\nRunning pipeline for: {topic}\n")
        result = run_unified_pipeline(topic, project_name)

        if result.success:
            show_results(result)
        else:
            print(f"\nFailed: {result.error}")
            sys.exit(1)
    else:
        # Interactive mode
        run_interactive()


if __name__ == "__main__":
    main()
