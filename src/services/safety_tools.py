import requests
import json
from typing import Dict, List, Optional
from agno.tools import Toolkit

class SafetyTools(Toolkit):
    def __init__(self, enable_device_recalls: bool = True, enable_drug_events: bool = True):
        super().__init__(name="safety_tools")
        self.enable_device_recalls = enable_device_recalls
        self.enable_drug_events = enable_drug_events

        # Register tools
        self.register(self.get_device_recalls)
        self.register(self.get_drug_adverse_events)

    def verify_access(self) -> bool:
        """
        Run this FIRST. Tests connectivity to OpenFDA.
        Returns True if API is reachable, False if blocked.
        """
        test_url = "https://api.fda.gov/device/enforcement.json?limit=1"
        try:
            print(f"🔍 Testing OpenFDA connection...")
            # 5 second timeout to prevent hanging
            response = requests.get(test_url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if "meta" in data:
                    print("✅ OpenFDA Connection Established (Valid JSON received).")
                    return True

            print(f"❌ OpenFDA Error: Status {response.status_code}")
            return False

        except Exception as e:
            print(f"❌ OpenFDA Unreachable: {str(e)}")
            return False

    def get_device_recalls(self, keyword: str, limit: int = 3) -> str:
        """
        Searches for Class I (Serious) device recalls.
        Use this for catheters, pumps, IVs, etc.

        Args:
            keyword: The device name (e.g., "catheter", "pump")
            limit: Max results to return
        """
        if not self.enable_device_recalls:
            return "Device recall search is disabled."

        base_url = "https://api.fda.gov/device/enforcement.json"

        # Query for Class I (most dangerous) recalls matching the keyword
        # Syntax: field:value+AND+field:value
        # We assume keyword is a single word for safety; if multi-word, wrap in quotes in caller
        query = f'classification:"Class I"+AND+product_description:"{keyword}"'

        try:
            full_url = f"{base_url}?search={query}&limit={limit}"
            response = requests.get(full_url, timeout=10)
            data = response.json()

            # Handle "No results found" which returns a 404-like error structure in OpenFDA
            if "error" in data:
                return f"No Class I recalls found for '{keyword}'."

            results = data.get("results", [])
            if not results:
                return f"No Class I recalls found for '{keyword}'."

            output = [f"⚠️ FOUND {len(results)} CLASS I RECALLS FOR '{keyword}':"]

            for item in results:
                recall_info = (
                    f"- Product: {item.get('product_description', 'N/A')}\n"
                    f"  Reason: {item.get('reason_for_recall', 'N/A')}\n"
                    f"  Recall Date: {item.get('recall_initiation_date', 'N/A')}\n"
                    f"  Status: {item.get('status', 'N/A')}\n"
                )
                output.append(recall_info)

            return "\n".join(output)

        except Exception as e:
            return f"Error fetching device recalls: {str(e)}"

    def get_drug_adverse_events(self, drug_name: str, limit: int = 3) -> str:
        """
        Searches for reported adverse events for a medication.

        Args:
            drug_name: The generic name (e.g., "heparin", "furosemide")
        """
        if not self.enable_drug_events:
            return "Drug event search is disabled."

        base_url = "https://api.fda.gov/drug/event.json"
        # Search patient.drug.medicinalproduct
        query = f'patient.drug.medicinalproduct:"{drug_name}"'

        try:
            response = requests.get(f"{base_url}?search={query}&limit={limit}", timeout=10)
            data = response.json()

            if "error" in data:
                return f"No adverse events found for '{drug_name}' in this query."

            results = data.get("results", [])
            if not results:
                return f"No adverse events found for '{drug_name}'."

            output = [f"📋 ADVERSE EVENTS SAMPLE FOR '{drug_name}':"]

            for item in results:
                patient = item.get("patient", {})
                # Extract reactions list
                reactions = [r.get("reactionmeddrapt", "Unknown") for r in patient.get("reaction", [])]
                # Extract serious flag
                serious = "Yes" if patient.get("reaction", [{}])[0].get("serious") == "1" else "No"

                output.append(f"- Serious: {serious} | Reactions: {', '.join(reactions)}")

            return "\n".join(output)

        except Exception as e:
            return f"Error fetching drug events: {str(e)}"

# --- SELF-TEST BLOCK ---
if __name__ == "__main__":
    print("--- STARTING SAFETY TOOLS SELF-TEST ---")
    tools = SafetyTools()

    if tools.verify_access():
        print("\n🧪 TEST 1: Searching for 'Catheter' Recalls (Class I)...")
        print(tools.get_device_recalls("catheter", limit=1))

        print("\n🧪 TEST 2: Searching for 'Heparin' Adverse Events...")
        print(tools.get_drug_adverse_events("heparin", limit=1))

        print("\n✅ SELF-TEST COMPLETE.")
    else:
        print("\n🛑 ABORT: API Accessibility Check Failed.")
