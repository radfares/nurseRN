
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.nursing_research_agent import nursing_research_agent

def test_picot_quality():
    print("Testing PICOT Quality for 'Nurse Burnout'...")
    
    query = """
    Help me develop a PICOT question about using peer support groups to reduce nurse burnout.
    """
    
    try:
        # Run agent directly and capture output
        print("\n" + "="*80)
        print("AGENT RESPONSE (Direct Run):")
        print("="*80)
        # Access the inner agno Agent object
        response = nursing_research_agent.agent.run(query, stream=False)
        print(response.content)
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_picot_quality()
