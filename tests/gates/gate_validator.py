"""
Gated validation system for AI agent workflows
Prevents agents from proceeding without legitimate test passes
"""

import subprocess
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class Gate:
    """Represents a validation gate that must be passed"""

    def __init__(self, name: str, test_command: str, description: str):
        self.name = name
        self.test_command = test_command
        self.description = description
        self.passed = False
        self.timestamp = None

    def validate(self) -> Dict:
        """Run tests and validate results"""
        # Hash test files BEFORE running
        test_hash_before = self._hash_test_files()

        # Run actual pytest command
        result = subprocess.run(
            self.test_command.split(),
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )

        # Hash test files AFTER running
        test_hash_after = self._hash_test_files()

        # Verify tests weren't modified
        hash_match = test_hash_before == test_hash_after

        return {
            "gate": self.name,
            "passed": result.returncode == 0 and hash_match,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "test_hash_before": test_hash_before,
            "test_hash_after": test_hash_after,
            "hash_verified": hash_match,
            "timestamp": datetime.now().isoformat()
        }

    def _hash_test_files(self) -> str:
        """Calculate hash of all test files to detect tampering"""
        test_files = sorted(Path("tests").rglob("test_*.py"))
        combined_hash = hashlib.sha256()

        for file in test_files:
            if file.exists():
                combined_hash.update(file.read_bytes())

        return combined_hash.hexdigest()

class GateKeeper:
    """Manages gate progression and validation"""

    def __init__(self):
        self.gates: List[Gate] = []
        self.current_gate = 0
        self.log: List[Dict] = []
        self.log_file = Path("tests/gates/gate_log.json")

    def add_gate(self, gate: Gate):
        """Add a gate to the sequence"""
        self.gates.append(gate)

    def validate_current_gate(self) -> Dict:
        """Validate the current gate"""
        if self.current_gate >= len(self.gates):
            return {
                "status": "COMPLETE",
                "message": "All gates passed!"
            }

        gate = self.gates[self.current_gate]
        print(f"\n{'='*60}")
        print(f"VALIDATING: {gate.name}")
        print(f"Description: {gate.description}")
        print(f"Command: {gate.test_command}")
        print(f"{'='*60}\n")

        result = gate.validate()
        self.log.append(result)
        self._save_log()

        if result["passed"]:
            print(f"✅ GATE {self.current_gate + 1} PASSED")
            self.current_gate += 1
            return {"status": "PASSED", "result": result}
        else:
            print(f"❌ GATE {self.current_gate + 1} FAILED")
            return {"status": "FAILED", "result": result}

    def _save_log(self):
        """Save immutable log of gate validations"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "current_gate": self.current_gate,
            "total_gates": len(self.gates),
            "gates_passed": self.current_gate,
            "log": self.log
        }

        with open(self.log_file, "w") as f:
            json.dump(log_data, f, indent=2)

        print(f"📝 Log saved to: {self.log_file}")
