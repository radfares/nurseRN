#!/usr/bin/env python3
"""
Setup and run gated validation for test cleanup
"""

from tests.gates.gate_validator import GateKeeper, Gate

def main():
    """Setup gates and begin validation"""

    gatekeeper = GateKeeper()

    # Gate 1: File Organization
    gatekeeper.add_gate(Gate(
        name="Gate 1: File Organization",
        test_command="pytest tests/unit/test_file_organization.py -v",
        description="Move misplaced test files to correct directories"
    ))

    # Gate 2: Test Integrity
    gatekeeper.add_gate(Gate(
        name="Gate 2: Test Integrity",
        test_command="pytest tests/unit/test_test_integrity.py -v",
        description="Ensure tests have meaningful assertions and aren't fake/trivial"
    ))

    # Gate 3: Gitignore Security
    gatekeeper.add_gate(Gate(
        name="Gate 3: Gitignore Security",
        test_command="pytest tests/unit/test_gitignore_security.py -v",
        description="Verify .gitignore correctly ignores secrets and user data"
    ))

    print("\n🚀 Starting Gated Validation System")
    print(f"📊 Total Gates: {len(gatekeeper.gates)}")
    print(f"📍 Current Gate: {gatekeeper.current_gate + 1}\n")

    # Validate gates until failure or completion
    while True:
        result = gatekeeper.validate_current_gate()

        if result["status"] == "COMPLETE":
            print(f"\n🎉 {result['message']}")
            break

        if result["status"] == "PASSED":
            print(f"\n✅ Gate {gatekeeper.current_gate} passed!")
            print(f"🔓 Gate {gatekeeper.current_gate + 1} is now unlocked")
            continue
            
        elif result["status"] == "FAILED":
            print(f"\n❌ Gate {gatekeeper.current_gate + 1} failed")
            print(f"\nTest Output:")
            print(result["result"]["stdout"])
            if result["result"]["stderr"]:
                print(f"\nErrors:")
                print(result["result"]["stderr"])
            break

    print(f"\n📝 Full log saved to: tests/gates/gate_log.json")

if __name__ == "__main__":
    main()
