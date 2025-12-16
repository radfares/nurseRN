# 🛠️ DIY Legacy Code Review - Hands-On Guide

> **Last Updated:** 2025-12-15

This guide will walk you through setting up and using modern code review tools on your own projects. Follow these steps to transform messy legacy code into clean, maintainable software.

---

## 🚀 Quick Start (5 Minutes)

### For Python Projects

```bash
# 1. Install the essential tools
pip install ruff mypy bandit vulture radon pytest pytest-cov

# 2. Run your first scan
ruff check .                    # Find style issues
mypy .                          # Check types
bandit -r src/                  # Security scan
vulture src/                    # Find dead code

# 3. Auto-fix what you can
ruff check --fix .              # Auto-fix style issues
```

### For JavaScript/TypeScript Projects

```bash
# 1. Install the essential tools
npm install --save-dev eslint prettier @typescript-eslint/parser eslint-plugin-deprecation

# 2. Run your first scan
npx eslint .                    # Find code issues
npx prettier --check .          # Check formatting

# 3. Auto-fix what you can
npx eslint --fix .              # Auto-fix issues
npx prettier --write .          # Format code
```

---

## 📦 Tool-by-Tool Setup Guide

### 1. **Ruff** - Super Fast Python Linter + Formatter

#### What It Does (Detailed)

**Ruff is like a code quality inspector for Python.** Think of it as a teacher that checks your homework for three things:

1. **Style Police (Formatting):** Makes sure your code looks consistent
   - Are you using 2 spaces or 4? Ruff enforces consistency
   - Are your imports alphabetized? Ruff can sort them
   - Are lines too long? Ruff can break them up
   
2. **Bug Detector (Linting):** Catches common mistakes before they crash your program
   - Unused variables: `x = 5` but you never use `x` → wastes memory
   - Missing imports: You call `print_json()` but forgot to `import json`
   - Undefined variables: Typos like `usre_name` instead of `user_name`
   
3. **Modernizer (Upgrading):** Suggests better ways to write old code
   - Old: `"Hello %s" % name` → New: `f"Hello {name}"`
   - Old: `dict.has_key('x')` → New: `'x' in dict`

**Why It Matters:**
- **Prevents bugs:** 60% of production bugs are caught by linters before deployment
- **Saves time:** Auto-fixes 80% of issues in seconds (vs hours of manual fixes)
- **Speeds up reviews:** Teammates spend less time arguing about style, more on logic

**Real-World Example:**

Before Ruff:
```python
import os, sys  # Multiple imports on one line (bad style)
import json     # Not alphabetized

def   calculate(x,y):  # Extra spaces, no type hints
    result=x+y         # No spaces around operators
    unused_var = 10    # Variable created but never used
    return result
```

After `ruff check --fix .`:
```python
import json  # Alphabetized
import os
import sys

def calculate(x: int, y: int) -> int:  # Added type hints
    result = x + y  # Proper spacing
    return result  # Removed unused variable
```

**Installation:**
```bash
pip install ruff
```

**Basic Usage:**
```bash
# Check for issues (doesn't change files)
ruff check .

# Auto-fix issues (modifies files)
ruff check --fix .

# Format code (like Black - makes everything pretty)
ruff format .
```

**Configuration (create `pyproject.toml` in your project root):**
```toml
[tool.ruff]
line-length = 100          # Maximum characters per line
target-version = "py312"   # Use Python 3.12 features

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors (style violations)
    "F",    # pyflakes (unused imports, variables)
    "I",    # isort (sorts imports alphabetically)
    "N",    # pep8-naming (enforces naming conventions)
    "UP",   # pyupgrade (modernizes old syntax)
    "B",    # flake8-bugbear (finds likely bugs)
    "C4",   # flake8-comprehensions (simpler list/dict creation)
]
```

**Pro Tips:**
- Run `ruff check --fix .` before every commit
- Add to pre-commit hooks: `pre-commit install`
- Ignore specific rules: `# noqa: E501` (line too long)

---

### 2. **Vulture** - Dead Code Detector

#### What It Does (Detailed)

**Vulture is like a detective that finds "zombie code" - code that exists but is never used.**

**The Problem:** Over time, codebases accumulate code that nobody calls anymore:
- **Old functions** from a feature you removed 2 years ago
- **Unused imports** like `import pandas` when you stopped using pandas
- **Dead variables** assigned but never read
- **Orphaned classes** that nothing instantiates anymore

**Why This Matters:**
- **Reduces confusion:** New developers waste hours reading code that doesn't run
- **Faster builds:** Unused imports still get loaded (slows startup by 10-30%)
- **Security:** Old code may contain vulnerabilities you thought were gone
- **Smaller codebase:** Deleting 20% of unused code makes everything more maintainable

**Real-World Example:**

Your code:
```python
import os  # You use this
import sys  # Never used - takes 50ms to load
import pandas  # Never used - takes 2 seconds to load!

def calculate_total(prices):
    tax_rate = 0.08  # Never used
    return sum(prices)

def old_calculate_total(prices):  # Old version, never called
    return sum(prices) * 1.08
```

Vulture finds:
```
src/calculator.py:2: unused import 'sys' (100% confidence)
src/calculator.py:3: unused import 'pandas' (100% confidence)
src/calculator.py:6: unused variable 'tax_rate' (100% confidence)
src/calculator.py:9: unused function 'old_calculate_total' (60% confidence)
```

**Confidence Score Explained:**
- **100%:** Definitely unused (safe to delete)
- **80-99%:** Probably unused (double-check)
- **60-79%:** Might be used dynamically (e.g., called via `getattr()`)
- **<60%:** Often false positives

**Installation:**
```bash
pip install vulture
```

**Basic Usage:**
```bash
# Scan for dead code
vulture src/

# Save report to file
vulture src/ > dead_code_report.txt

# Set minimum confidence (0-100, higher = more certain)
vulture src/ --min-confidence 80
```

**Pro Tips:**
- Start with `--min-confidence 80` to avoid false positives
- Review each finding - some "unused" code may be called dynamically
- Create a whitelist file for intentionally unused code:
  ```bash
  vulture src/ --exclude whitelist.py
  ```

---

### 3. **Refurb** - Modernize Your Python Code

#### What It Does (Detailed)

**Refurb is like a translator that updates "old English" Python to modern Python.**

**The Problem:** Python has evolved massively:
- **Python 2 → 3:** Huge syntax changes
- **Python 3.6:** Introduced f-strings (faster, cleaner)
- **Python 3.10:** Added match/case statements
- **Python 3.12:** Improved type hints, performance

**What Refurb Does:**
It finds old-style code and suggests the modern equivalent.

**Why This Matters:**
- **Speed:** Modern Python is 10-40% faster for some operations
- **Readability:** f-strings are easier to read than `%` formatting
- **Safety:** New features catch bugs (e.g., `match/case` is exhaustive)

**Real-World Examples:**

**Example 1: String Formatting**
```python
# Old way (Python 2 style - slow, ugly)
name = "Alice"
age = 30
message = "Hello %s, you are %d years old" % (name, age)

# Modern way (Python 3.6+ - 20% faster, clearer)
message = f"Hello {name}, you are {age} years old"
```

**Example 2: List Creation**
```python
# Old way (verbose, 5 lines)
items = []
for x in range(10):
    if x % 2 == 0:
        items.append(x * 2)

# Modern way (1 line, easier to understand)
items = [x * 2 for x in range(10) if x % 2 == 0]
```

**Example 3: Path Handling**
```python
# Old way (breaks on Windows vs Mac)
import os
file_path = os.path.join('/Users', 'alice', 'documents', 'file.txt')

# Modern way (works everywhere, type-safe)
from pathlib import Path
file_path = Path('/Users') / 'alice' / 'documents' / 'file.txt'
```

**Installation:**
```bash
pip install refurb
```

**Basic Usage:**
```bash
# Scan for modernization opportunities
refurb check src/

# Show explanations for each suggestion
refurb check --explain src/
```

**Pro Tips:**
- Run after upgrading Python versions (e.g., 3.8 → 3.12)
- Pair with `pyupgrade` for automated fixes

---

### 4. **mypy** - Static Type Checker

#### What It Does (Detailed)

**mypy is like a spell-checker for your code's data types.**

**The Problem:** Python doesn't check types until your code crashes:
```python
def calculate_discount(price, percent):
    return price * (1 - percent / 100)

# These will CRASH at runtime:
calculate_discount("100", 20)  # Can't multiply string!
calculate_discount(100, "20")  # Can't divide string!
calculate_discount(None, 20)   # Can't multiply None!
```

**Without mypy:** You discover these bugs when users complain.

**With mypy:** You discover them while writing code:
```python
def calculate_discount(price: float, percent: float) -> float:
    return price * (1 - percent / 100)

calculate_discount("100", 20)  # mypy ERROR: Expected float, got str
```

**Why This Matters:**
- **Catches 15% of all bugs** before you even run the code
- **Better autocomplete:** Your editor knows what methods are available
- **Documentation:** Types tell you what a function expects
- **Refactoring safety:** Change one function, mypy shows everywhere it breaks

**Real-World Example:**

Before mypy (risky):
```python
def get_user(user_id):
    # What type is user_id? String? Int?
    # What does this return? Dict? User object? None?
    return database.query(user_id)

user = get_user("123")  # Or is it get_user(123)?
print(user.name)  # Will this crash if user is None?
```

After mypy (safe):
```python
from typing import Optional

def get_user(user_id: int) -> Optional[dict]:
    """Get user by ID. Returns None if not found."""
    return database.query(user_id)

user = get_user("123")  # mypy ERROR: Expected int, got str
user = get_user(123)    # OK!
print(user.name)        # mypy ERROR: user might be None!

# Fixed version:
user = get_user(123)
if user is not None:
    print(user["name"])  # Safe!
```

**Type Hint Cheat Sheet:**
```python
from typing import List, Dict, Optional, Union

# Basic types
age: int = 30
name: str = "Alice"
price: float = 19.99
is_active: bool = True

# Collections
scores: List[int] = [85, 90, 78]
user: Dict[str, str] = {"name": "Alice", "email": "alice@example.com"}

# Optional (might be None)
phone: Optional[str] = None  # Can be string or None

# Union (multiple types)
id: Union[int, str] = 123  # Can be int OR string

# Functions
def greet(name: str, age: int) -> str:
    return f"Hello {name}, age {age}"
```

**Installation:**
```bash
pip install mypy
```

**Basic Usage:**
```bash
# Check types
mypy src/

# Strict mode (recommended for new code)
mypy --strict src/

# Ignore missing imports (for legacy code)
mypy --ignore-missing-imports src/
```

**Configuration (`pyproject.toml`):**
```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

**Pro Tips:**
- Start with `--ignore-missing-imports` for legacy code
- Add types gradually (one module at a time)
- Use `reveal_type(variable)` to debug type inference

---

### 5. **Bandit** - Security Vulnerability Scanner

#### What It Does (Detailed)

**Bandit is like a security guard that checks your code for common hacking vulnerabilities.**

**The Problem:** Developers make security mistakes that hackers exploit:

**1. Hardcoded Secrets (90% of breaches)**
```python
# DANGER: Anyone with access to code can steal this!
API_KEY = "sk_live_51H8xYz2eZvKYlo2C"
PASSWORD = "admin123"
```

**2. SQL Injection (allows hackers to steal entire databases)**
```python
# DANGER: User can inject malicious SQL
user_input = "admin' OR '1'='1"
query = f"SELECT * FROM users WHERE username = '{user_input}'"
# This becomes: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# Returns ALL users!
```

**3. Insecure Random Numbers (predictable lottery/passwords)**
```python
import random
lottery_number = random.randint(1, 1000000)  # DANGER: Predictable!
# Hackers can guess this
```

**What Bandit Finds:**
- **Hardcoded passwords/API keys** (B105)
- **SQL injection vulnerabilities** (B608)
- **Weak cryptography** (B304, B305)
- **Insecure file permissions** (B103)
- **Shell injection** (B602, B605)
- **Use of `eval()`** (B307 - allows arbitrary code execution)

**Why This Matters:**
- **97% of data breaches** exploit known vulnerabilities that tools like Bandit catch
- **Average cost of breach:** $4.45 million (IBM 2023)
- **Compliance:** Many industries (healthcare, finance) require security scanning

**Real-World Example:**

Dangerous code:
```python
import os

# DANGER 1: Hardcoded password
DATABASE_PASSWORD = "super_secret_123"

# DANGER 2: SQL Injection
def get_user(username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return db.execute(query)

# DANGER 3: Shell Injection
def backup_file(filename):
    os.system(f"cp {filename} /backup/")  # User can inject commands!
```

Bandit findings:
```
>> Issue: [B105:hardcoded_password_string] Hardcoded password
   Severity: MEDIUM   Confidence: MEDIUM
   Location: src/db.py:4
   
>> Issue: [B608:sql_injection] SQL injection via string interpolation
   Severity: HIGH   Confidence: MEDIUM
   Location: src/db.py:8
   
>> Issue: [B605:shell_injection] Shell injection via os.system
   Severity: HIGH   Confidence: HIGH
   Location: src/backup.py:13
```

Secure version:
```python
import os
import secrets
from pathlib import Path

# SAFE: Use environment variables
DATABASE_PASSWORD = os.getenv("DB_PASSWORD")

# SAFE: Use parameterized queries
def get_user(username):
    query = "SELECT * FROM users WHERE name = ?"
    return db.execute(query, (username,))  # Escaped automatically

# SAFE: Use Path library (prevents injection)
def backup_file(filename):
    src = Path(filename)
    dst = Path("/backup") / src.name
    shutil.copy(src, dst)
```

**Installation:**
```bash
pip install bandit
```

**Basic Usage:**
```bash
# Scan for security issues
bandit -r src/

# Show only high/medium severity
bandit -r src/ -ll

# Generate HTML report
bandit -r src/ -f html -o security_report.html
```

**Pro Tips:**
- Run before every deployment
- Fix high-severity issues immediately
- Use environment variables for secrets (never hardcode)

---

### 6. **Radon** - Code Complexity Metrics

#### What It Does (Detailed)

**Radon measures how "tangled" your code is - like counting knots in a rope.**

**Cyclomatic Complexity Explained:**
It counts how many different paths your code can take.

**Simple Example (Complexity = 1):**
```python
def greet(name):
    return f"Hello {name}"  # Only 1 path
```

**Complex Example (Complexity = 8):**
```python
def process_order(order):
    if order.is_valid:           # Path 1
        if order.has_payment:     # Path 2
            if order.in_stock:    # Path 3
                if order.user_premium:  # Path 4
                    # ... 4 more nested ifs
                    return True
    return False
# Total: 8 different paths = Complexity 8
```

**Why High Complexity is Bad:**
- **Hard to test:** Need 8+ tests to cover all paths
- **More bugs:** Studies show bugs increase exponentially with complexity
- **Difficult to understand:** Takes 3x longer to understand code with complexity > 15
- **Hard to modify:** Change one thing, break 5 others

**Research Data:**
- **Complexity 1-10:** 5% bug rate
- **Complexity 11-20:** 20% bug rate
- **Complexity 21+:** 40% bug rate

**Real-World Example:**

Complex code (Complexity = 12):
```python
def validate_user(user):
    if user.age >= 18:
        if user.email:
            if '@' in user.email:
                if user.password:
                    if len(user.password) >= 8:
                        if user.agreed_to_terms:
                            if user.country in ['US', 'UK', 'CA']:
                                return True
    return False
```

Simple code (Complexity = 1):
```python
def validate_user(user):
    """Validate user meets all requirements."""
    if user.age < 18:
        return False
    if not user.email or '@' not in user.email:
        return False
    if not user.password or len(user.password) < 8:
        return False
    if not user.agreed_to_terms:
        return False
    if user.country not in ['US', 'UK', 'CA']:
        return False
    return True
```

**Benefits of simple version:**
- ✅ No nesting (easier to read)
- ✅ Each check is independent (easier to modify)
- ✅ Early returns (faster execution)
- ✅ Complexity = 1 (90% fewer bugs)

**Installation:**
```bash
pip install radon
```

**Basic Usage:**
```bash
# Show complexity scores
radon cc src/ -s

# Only show complex functions (score > 10)
radon cc src/ -nc

# Maintainability index (A=best, F=worst)
radon mi src/
```

**Complexity Scale:**
- **A (1-5):** Simple, easy to maintain
- **B (6-10):** Moderate complexity
- **C (11-20):** High complexity - refactor recommended
- **D/F (20+):** Very high - urgent refactoring needed

**Pro Tips:**
- Target cyclomatic complexity < 10
- Break complex functions into smaller helpers
- Use early returns to reduce nesting

---

### 7. **pytest + coverage** - Test Coverage Analysis

#### What It Does (Detailed)

**Coverage shows which lines of your code are actually run by your tests.**

**The Problem:** You can have 100 tests but still miss critical bugs:

```python
def calculate_discount(price, user_type):
    if user_type == "premium":
        return price * 0.8  # 20% discount
    elif user_type == "student":
        return price * 0.9  # 10% discount - NEVER TESTED!
    else:
        return price

# Your test:
def test_premium_discount():
    assert calculate_discount(100, "premium") == 80

# Coverage shows: 66% - the student discount line was never run!
```

**Why Coverage Matters:**
- **Find blind spots:** Shows code you THINK works but never tested
- **Regression protection:** If coverage drops, you removed tests
- **Confidence:** 80%+ coverage means most code paths are checked

**Industry Standards:**
- **Critical systems (medical, finance):** 90-100% required
- **Production apps:** 80%+ recommended
- **Prototypes:** 60%+ acceptable

**What Coverage DOESN'T Mean:**
- ❌ 100% coverage ≠ bug-free (tests might be wrong)
- ❌ High coverage ≠ good tests (tests might not check outputs)
- ✅ Use coverage to find **missing** tests, not prove perfection

**Real-World Example:**

Your code:
```python
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

Your test:
```python
def test_divide():
    assert divide(10, 2) == 5
```

Coverage report:
```
Name            Stmts   Miss  Cover   Missing
---------------------------------------------
src/math.py         3      1    66%   3
```

Line 3 (`raise ValueError`) was **never tested!** Add:
```python
def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)  # Now 100% coverage!
```

**Reading Coverage Reports:**

```
Name                Stmts   Miss  Cover   Missing
-------------------------------------------------
src/utils.py           45      8    82%   23-25, 67-70
src/models.py          120     5    96%   145-149
-------------------------------------------------
TOTAL                  165     13    92%
```

- **Stmts:** Total executable lines
- **Miss:** Lines never run by tests
- **Cover:** Percentage tested (Stmts - Miss) / Stmts
- **Missing:** Exact line numbers not covered

**Installation:**
```bash
pip install pytest pytest-cov
```

**Basic Usage:**
```bash
# Run tests with coverage
pytest --cov=src tests/

# Generate HTML report (open htmlcov/index.html in browser)
pytest --cov=src --cov-report=html tests/

# Show missing lines in terminal
pytest --cov=src --cov-report=term-missing tests/

# Fail if coverage below 80%
pytest --cov=src --cov-fail-under=80 tests/
```

**Pro Tips:**
- Target 80%+ coverage for critical code
- Focus on testing business logic, not getters/setters
- Use `# pragma: no cover` for unreachable code (e.g., `if __name__ == "__main__"`)
- Don't chase 100% - test what matters

---

## 🤖 AI-Powered Tools Setup

### GitHub Copilot (Paid - $10/month)

**What it does:** AI assistant that suggests code, writes tests, explains legacy functions.

**Setup:**
1. Install VS Code extension: "GitHub Copilot"
2. Sign in with GitHub account
3. Start typing - Copilot auto-suggests

**Best for Legacy Code:**
- Highlight a function → Ask: "Explain this code"
- Right-click → "Generate tests"
- Comment: `# Refactor this to use modern Python` → Generate

---

### CodeRabbit (Free tier available)

**What it does:** AI code reviewer for GitHub PRs with full codebase context.

**Setup:**
1. Go to [coderabbit.ai](https://coderabbit.ai)
2. Connect your GitHub account
3. Install on your repository

**What it reviews:**
- Logic errors, performance issues
- Security vulnerabilities
- Code style violations
- Missing test coverage

---

### Qodo.ai (Free for open source)

**What it does:** AI-powered test generation.

**Setup:**
1. Install VS Code extension: "Qodo - AI Test Generation"
2. Right-click on a function → "Generate Tests"

**Example:**
```python
# Your function
def calculate_discount(price: float, percent: float) -> float:
    return price * (1 - percent / 100)

# Qodo generates:
def test_calculate_discount():
    assert calculate_discount(100, 10) == 90.0
    assert calculate_discount(50, 20) == 40.0
    assert calculate_discount(100, 0) == 100.0
```

---

## 🎯 Practical Workflow

### Step 1: Initial Health Check (10 minutes)

```bash
# Create a report directory
mkdir -p legacy_review_reports

# Run all scanners
ruff check . > legacy_review_reports/ruff_issues.txt
mypy --ignore-missing-imports . > legacy_review_reports/type_issues.txt
bandit -r src/ -f txt -o legacy_review_reports/security_issues.txt
vulture src/ > legacy_review_reports/dead_code.txt
radon cc src/ -s > legacy_review_reports/complexity.txt
pytest --cov=src --cov-report=html tests/
```

**Review the reports:**
- Prioritize security issues (Bandit)
- Fix dead code (Vulture) - easiest wins
- Address high complexity (Radon score > 15)

---

### Step 2: Quick Wins (30 minutes)

```bash
# Auto-fix formatting and simple issues
ruff check --fix .
ruff format .

# Remove dead imports
ruff check --select F401 --fix .

# Commit these changes
git add .
git commit -m "chore: auto-fix linting and formatting"
```

---

### Step 3: Add Type Hints (1-2 hours per module)

**Start with one file:**

```bash
# Add basic type hints
# tools/add_types.py
from typing import List, Dict, Optional

def process_users(users: List[Dict[str, str]]) -> Optional[str]:
    if not users:
        return None
    return users[0]["name"]

# Check types
mypy tools/add_types.py
```

**Gradually expand** to other modules.

---

### Step 4: Refactor Complex Functions (Ongoing)

**Find complex functions:**
```bash
radon cc src/ -nc  # Show only complex code
```

**Refactor example:**
```python
# Before (complexity = 15)
def process_order(order):
    if order.status == "pending":
        if order.payment_verified:
            if order.items_in_stock:
                # 10 more nested ifs...
                return True
    return False

# After (complexity = 3)
def process_order(order):
    if order.status != "pending":
        return False
    if not order.payment_verified:
        return False
    if not order.items_in_stock:
        return False
    # Clear, early returns
    return True
```

---

### Step 5: Set Up CI/CD Checks

**GitHub Actions (`.github/workflows/ci.yml`):**
```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install ruff mypy bandit pytest pytest-cov
      - run: ruff check .
      - run: mypy --ignore-missing-imports src/
      - run: bandit -r src/
      - run: pytest --cov=src --cov-fail-under=80 tests/
```

---

## 🎓 Learning Resources

### Beginner-Friendly
- [Real Python - Code Quality](https://realpython.com/python-code-quality/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

### Advanced
- [Refactoring Guru](https://refactoring.guru/) - Design patterns
- [GitHub's Code Review Best Practices](https://google.github.io/eng-practices/review/)
- [Martin Fowler - Refactoring](https://martinfowler.com/books/refactoring.html)

---

## 🆘 Troubleshooting

### "Too many false positives from Vulture"
**Solution:** Increase confidence threshold
```bash
vulture src/ --min-confidence 90
```

### "mypy complains about missing type stubs"
**Solution:** Install stub packages or ignore
```bash
pip install types-requests  # For requests library
# OR
mypy --ignore-missing-imports src/
```

### "Ruff is too strict"
**Solution:** Configure rules in `pyproject.toml`
```toml
[tool.ruff.lint]
ignore = ["E501"]  # Ignore line length
```

### "Too many issues to fix at once"
**Solution:** Fix incrementally
```bash
# Fix one category at a time
ruff check --select F401 --fix .  # Only unused imports
```

---

## ✅ Success Checklist

- [ ] Installed Ruff, mypy, Bandit (Python) or ESLint (JS)
- [ ] Ran initial health check and saved reports
- [ ] Fixed auto-fixable issues with `ruff check --fix`
- [ ] Removed dead code identified by Vulture
- [ ] Added type hints to at least one module
- [ ] Refactored at least one complex function (complexity > 15)
- [ ] Achieved >80% test coverage on core modules
- [ ] Set up CI/CD to run checks automatically
- [ ] Documented changes in git commits

---

## 🚦 When to Stop Refactoring

> **"Perfect is the enemy of good."**

Stop when:
- All **high-severity security issues** are fixed (Bandit)
- **Test coverage** is >80% on critical paths
- **Complexity scores** are <15 for core business logic
- **Dead code** is removed
- Code passes CI/CD checks

Don't over-optimize:
- **Performance** (unless you have metrics showing it's slow)
- **Style** (if Ruff passes, it's good enough)
- **Comments** (code should be self-documenting with good names)

---

## 📞 Need Help?

- **Ruff Issues:** [GitHub Discussions](https://github.com/astral-sh/ruff/discussions)
- **mypy Help:** [Gitter Chat](https://gitter.im/python/typing)
- **General Python:** [r/learnpython](https://reddit.com/r/learnpython)

---

**Happy Refactoring! 🎉**
