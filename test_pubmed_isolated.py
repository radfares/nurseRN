#!/usr/bin/env python3
"""
Isolated PubMed Test - Phase 4
Tests PubMed API directly without agents or orchestrators.

This proves PubMed works when given a valid query string.
"""
import sys
sys.path.insert(0, '/Users/hdz/nurseRN')

from src.services.api_tools import create_pubmed_tools_safe

def test_pubmed_isolation():
    """Test PubMed search in complete isolation."""
    
    print("=" * 80)
    print("PHASE 4: ISOLATED PUBMED TEST")
    print("=" * 80)
    print()
    
    # Create PubMed tools
    print("1. Creating PubMed tools...")
    pubmed = create_pubmed_tools_safe()
    
    if pubmed is None:
        print("❌ FAILED: Could not create PubMed tools")
        return False
    
    print("✅ PubMed tools created successfully")
    print(f"   Type: {type(pubmed)}")
    print(f"   Available methods: {[m for m in dir(pubmed) if not m.startswith('_')]}")
    print()
    
    # Test search
    query = "catheter associated urinary tract infection prevention bundle"
    print(f"2. Testing search with query: '{query}'")
    print(f"   Max results: 5")
    print()
    
    try:
        # Check if search_pubmed method exists
        if not hasattr(pubmed, 'search_pubmed'):
            print("❌ FAILED: PubMed tool does not have 'search_pubmed' method")
            print(f"   Available methods: {dir(pubmed)}")
            return False
        
        # Execute search
        print("3. Executing search...")
        print("-" * 80)
        result = pubmed.search_pubmed(query, max_results=5)
        print("-" * 80)
        print()
        
        # Display results
        print("4. Results:")
        print(f"   Type: {type(result)}")
        print(f"   Length: {len(str(result))} characters")
        print()
        
        if result:
            # Try to parse if it's a string
            if isinstance(result, str):
                print("   Raw result (first 1000 chars):")
                print("   " + "-" * 76)
                print("   " + str(result)[:1000])
                if len(str(result)) > 1000:
                    print("   ... (truncated)")
                print("   " + "-" * 76)
            else:
                print(f"   Result: {result}")
            
            print()
            print("=" * 80)
            print("✅ SUCCESS: PubMed search completed")
            print("=" * 80)
            return True
        else:
            print("⚠️  WARNING: Search returned empty/None result")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Exception during search")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pubmed_isolation()
    sys.exit(0 if success else 1)
