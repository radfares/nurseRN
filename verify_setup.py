#!/usr/bin/env python3
"""
Setup Verification Script
Verifies that all dependencies and paths are correctly configured.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_agno_library():
    """Check if agno library can be imported."""
    try:
        # Add libs/agno to path
        project_root = Path(__file__).parent
        agno_path = project_root / "libs" / "agno"
        if agno_path.exists():
            sys.path.insert(0, str(agno_path))

        from agno.agent import Agent
        print("✅ Agno library imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import agno: {e}")
        print("   Make sure libs/agno exists and PYTHONPATH is set")
        return False

def check_core_dependencies():
    """Check core dependencies."""
    dependencies = [
        ("dotenv", "python-dotenv"),
        ("httpx", "httpx"),
        ("requests", "requests"),
        ("pydantic", "pydantic"),
        ("openai", "openai"),
        ("rich", "rich"),
        ("sqlalchemy", "sqlalchemy"),
    ]

    all_ok = True
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - Run: pip install {package_name}")
            all_ok = False

    return all_ok

def check_env_file():
    """Check if .env file exists."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print("✅ .env file found")

        # Check for required keys
        from dotenv import load_dotenv
        load_dotenv()

        openai_key = os.getenv("OPENAI_API_KEY")
        def _mask(k: str) -> str:
            if not k:
                return ""
            if len(k) <= 8:
                return "*" * len(k)
            return f"{k[:6]}…{k[-4:]}"

        def _looks_placeholder(k: str) -> bool:
            if not k:
                return False
            kl = k.lower()
            placeholders = [
                "your-openai", "your_api_key", "your-openai-api-key-here",
                "your-ope", "<your-openai", "your-key", "paste-key",
            ]
            return any(p in kl for p in placeholders)

        if openai_key:
            if _looks_placeholder(openai_key):
                print(f"❌ OPENAI_API_KEY appears to be a placeholder: {_mask(openai_key)}")
                print("   Update .env with a real key from https://platform.openai.com/api-keys")
            else:
                prefix = "valid-looking"
                if not (openai_key.startswith("sk-") or openai_key.startswith("sk-proj-")):
                    prefix = "non-standard"
                print(f"✅ OPENAI_API_KEY is set ({prefix}): {_mask(openai_key)}")
        else:
            print("⚠️  OPENAI_API_KEY not set (REQUIRED)")

        # Optional keys
        optional_keys = [
            ("EXA_API_KEY", "Exa search"),
            ("SERPAPI_API_KEY", "SerpAPI search"),
            ("SERP_API_KEY", "SerpAPI search (legacy)"),
            ("PUBMED_EMAIL", "PubMed search"),
        ]

        for key, description in optional_keys:
            if os.getenv(key):
                print(f"✅ {key} is set ({description})")
            else:
                print(f"⚠️  {key} not set (optional - {description})")

        return True
    else:
        print("⚠️  .env file not found")
        print("   Create .env file with your API keys")
        print("   Required: OPENAI_API_KEY")
        print("   Optional: EXA_API_KEY, SERP_API_KEY, PUBMED_EMAIL")
        return False

def check_project_structure():
    """Check project directory structure."""
    project_root = Path(__file__).parent

    required_dirs = [
        "libs/agno",
        "data",
        "src/services",
    ]

    all_ok = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - Missing")
            all_ok = False

    return all_ok

def main():
    """Run all checks."""
    print("=" * 60)
    print("Nursing Research Project - Setup Verification")
    print("=" * 60)
    print()

    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Core Dependencies", check_core_dependencies),
        ("Agno Library", check_agno_library),
        ("Environment File", check_env_file),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 60)
        result = check_func()
        results.append((name, result))

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
        if not result:
            all_passed = False

    print()
    if all_passed:
        print("🎉 All checks passed! You're ready to start.")
        print("\nTo start the project:")
        print("  ./start_nursing_project.sh")
        print("  or")
        print("  python3 run_nursing_project.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

