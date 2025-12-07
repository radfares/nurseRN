"""
Gate 3: .gitignore Security Validation
Focused on security-critical patterns only
"""
import subprocess
from pathlib import Path
import pytest

class TestGate3GitignoreSecurity:
    """Security validation for .gitignore"""
    
    @pytest.fixture
    def project_root(self):
        return Path(__file__).parent.parent.parent
    
    def test_env_patterns_present(self, project_root):
        """Verify .env patterns exist in .gitignore"""
        gitignore = (project_root / ".gitignore").read_text()
        assert ".env" in gitignore, "Missing .env pattern"
        assert ".env.local" in gitignore, "Missing .env.local pattern"
    
    def test_no_secrets_tracked(self, project_root):
        """CRITICAL: No secret files should be tracked"""
        result = subprocess.run(
            ["git", "ls-files", ".env*"],
            capture_output=True,
            cwd=project_root
        )
        tracked_files = result.stdout.decode().strip().split('\n')
        
        # Filter out safe example files
        unsafe_tracked = [f for f in tracked_files if f and f != ".env.example"]
        
        assert len(unsafe_tracked) == 0, f"SECRET FILE TRACKED: {unsafe_tracked}"
    
    def test_user_data_ignored(self, project_root):
        """Verify user data patterns exist"""
        gitignore = (project_root / ".gitignore").read_text()
        assert "data/projects/" in gitignore
        assert "*.db" in gitignore
