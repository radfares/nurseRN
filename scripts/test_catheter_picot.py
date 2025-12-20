
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.nursing_research_agent import nursing_research_agent

def compare_picot_quality():
    print("Testing PICOT Quality for 'Foley Catheter Removal' (CAUTI)...")
    
    query = """
    Help me develop a PICOT question about early foley catheter removal to reduce UTIs.
    """
    
    try:
        print("\n" + "="*80)
        print("AGENT RESPONSE (New Standard):")
        print("="*80)
        # Access the inner agno Agent object
        response = nursing_research_agent.agent.run(query, stream=False)
        print(response.content)
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    compare_picot_quality()
