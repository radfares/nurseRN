# nurseRN/run_nursing_project.py at main · radfares/nurseRN · GitHub

**URL:** https://github.com/radfares/nurseRN/blob/main/run_nursing_project.py

---

Skip to content
Navigation Menu
Platform
Solutions
Resources
Open Source
Enterprise
Pricing
Sign in
Sign up
radfares
/
nurseRN
Public
Notifications
Fork 0
 Star 0
Code
Issues
Pull requests
Actions
Projects
Security
Insights
Files
 main
.agent
.claude
.cursor
.github
New_Grad_project
_archived_docs
_archived_misc
agents
cookbook
data
docs
libs
scripts
src
tests
.cursorrules
.editorconfig
.env.example
.gitignore
CODEOWNERS
CODE_OF_CONDUCT.md
CONTRIBUTING.md
LICENSE
NEW_AGENTS_GUIDE.md
NURSING_PROJECT_GUIDE.md
README.md
SETUP.md
agent_config.py
data_template.xlsx
diagnostic_tool_analysis.py
project_manager.py
pytest.ini
requirements.txt
run_nursing_project.py
setup_gates.py
setup_venv.sh
start_nursing_project.sh
truth_file.md
verify_workflow_e2e.py
Breadcrumbs
nurseRN
/run_nursing_project.py
Latest commit
radfares
fix(tests): Gate 2 validation - add assertions and fix test pollution
513c874
 · 
History
History
File metadata and controls
Code
Blame
Raw
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
570
571
572
573
574
575
576
577
578
579
580
581
582
583
584
585
586
587
588
589
590
591
592
593
594
595
596
597
598
599
600
601
602
603
604
605
606
607
608
609
610
611
612
613
614
615
616
617
618
619
620
621
622
623
624
625
626
627
628
629
630
631
632
633
634
635
636
637
638
639
640
641
642
643
"""
Nursing Research Project Assistant
Complete system for healthcare improvement project support with project management.


UPDATED: 2025-11-23 - Added project-centric database architecture
"""


from dotenv import load_dotenv
# Ensure .env values override any existing shell values so the app uses the keys you set in .env
load_dotenv(override=True)


# Ensure vendored agno library is importable
import sys
import time
from pathlib import Path
_project_root = Path(__file__).parent
_agno_path = _project_root / "libs" / "agno"
if _agno_path.exists() and str(_agno_path) not in sys.path:
    sys.path.insert(0, str(_agno_path))


from project_manager import (
    get_project_manager,
    cli_create_project,
    cli_list_projects,
    cli_switch_project,
    cli_archive_project
)


# Agent imports from agents/ module
from agents.base_agent import BaseAgent
from agents.nursing_research_agent import nursing_research_agent
from agents.nursing_project_timeline_agent import project_timeline_agent
from agents.medical_research_agent import get_medical_research_agent
from agents.academic_research_agent import academic_research_agent
from agents.research_writing_agent import research_writing_agent
from agents.data_analysis_agent import data_analysis_agent
from agents.citation_validation_agent import get_citation_validation_agent


# Orchestration imports
from src.orchestration.context_manager import ContextManager
from src.orchestration.orchestrator import WorkflowOrchestrator
from src.orchestration.query_router import QueryRouter, Intent
from src.workflows.research_workflow import ResearchWorkflow
from src.workflows.parallel_search import ParallelSearchWorkflow
from src.workflows.timeline_planner import TimelinePlannerWorkflow
from src.workflows.validated_research_workflow import ValidatedResearchWorkflow




def show_welcome():
    """Display welcome message."""
    print("\n" + "=" * 80)
    print("🏥 NURSING RESEARCH PROJECT ASSISTANT")
    print("=" * 80)
    print("\nProject-Centric Multi-Agent System")
    print("Timeline: November 2025 - June 2026")
    print("\nFeatures:")
    print("  ✓ Project management (create, switch, archive)")
    print("  ✓ 6 specialized AI agents")
    print("  ✓ Centralized project database")
    print("  ✓ PICOT development, literature search, data analysis")
    print("=" * 80)




def show_project_menu():
    """Display project management menu."""
    print("\n" + "="*80)
    print("PROJECT MANAGEMENT")
    print("="*80)


    pm = get_project_manager()
    active_project = pm.get_active_project()


    if active_project:
        print(f"\n★ ACTIVE PROJECT: {active_project}")
    else:
        print("\n⚠️  No active project selected")


    print("\nProject Commands:")
    print("  new <project_name>     - Create new project")
    print("  list                   - List all projects")
    print("  switch <project_name>  - Switch to project")
    print("  archive <project_name> - Archive project")
    print("  agents                 - Launch agents (requires active project)")
    print("  exit                   - Exit program")
    print("\n" + "="*80)




def project_management_loop():
    """Main project management loop."""
    while True:
        show_project_menu()


        command = input("\n📋 Command: ").strip().lower()


        if not command:
            continue


        # Parse command
        parts = command.split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else None


        if cmd in ['exit', 'quit', 'q']:
            print("\n👋 Goodbye!")
            break


        elif cmd == 'new':
            if not arg:
                print("❌ Usage: new <project_name>")
                continue
            cli_create_project(arg, add_milestones=True)


        elif cmd == 'list':
            cli_list_projects()


        elif cmd == 'switch':
            if not arg:
                print("❌ Usage: switch <project_name>")
                continue
            cli_switch_project(arg)


        elif cmd == 'archive':
            if not arg:
                print("❌ Usage: archive <project_name>")
                continue
            confirm = input(f"⚠️  Archive '{arg}'? This will move it to archives. (yes/no): ")
            if confirm.lower() == 'yes':
                cli_archive_project(arg)
            else:
                print("❌ Cancelled")


        elif cmd == 'agents':
            # Check for active project
            pm = get_project_manager()
            active_project = pm.get_active_project()


            if not active_project:
                print("\n❌ No active project. Create or switch to a project first.")
                print("   Commands: 'new <name>' or 'switch <name>'")
                continue


            # Launch agent selector
            print(f"\n✅ Using project: {active_project}")
            agent_selection_loop()


        else:
  ❌ A validated clinical decision tool


ALL OUTPUTS MUST BE REVIEWED BY:
  • Nurse Manager (workflow feasibility)
  • Clinical experts (Infection Control, Safety, Quality Dept)
  • Statistician (if using sample size calculations)
  • IRB/Ethics Committee (for research classification)


BY USING THIS TOOL YOU ACKNOWLEDGE:
  1. You are a licensed healthcare professional
  2. You will obtain appropriate institutional approvals
  3. You will validate all recommendations with experts
  4. You are solely responsible for project outcomes
  5. This tool provides planning guidance, not clinical recommendations


IMPORTANT:
  • All statistical calculations are estimates and require expert review
  • Budget estimates are rough approximations only
  • Literature search results must be independently verified