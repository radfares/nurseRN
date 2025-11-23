"""
Pytest configuration and fixtures for the nursing research agent tests
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add vendored agno library to Python path
agno_path = project_root / "libs" / "agno"
sys.path.insert(0, str(agno_path))
