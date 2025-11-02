"""
Runner script for Data Analysis Agent tests.
Handles API key checking and provides user-friendly output.
"""

import os
import sys

def check_api_keys():
    """Check if required API keys are available."""
    print("Checking API keys...")
    
    mistral_key = os.getenv("MISTRAL_API_KEY")
    
    if not mistral_key:
        print("\n" + "=" * 80)
        print("⚠️  MISTRAL API KEY REQUIRED")
        print("=" * 80)
        print("\nThe Data Analysis Agent requires a Mistral API key to run.")
        print("\nYou have two options:")
        print("\n1. Set environment variable:")
        print("   export MISTRAL_API_KEY='your-mistral-api-key'")
        print("\n2. Create .env file with:")
        print("   MISTRAL_API_KEY=your-mistral-api-key")
        print("\n" + "=" * 80)
        
        # Offer to enter key interactively
        print("\nWould you like to enter your Mistral API key now? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice == 'y':
            print("\nEnter your Mistral API key: ", end="")
            key = input().strip()
            if key:
                os.environ["MISTRAL_API_KEY"] = key
                print("✓ API key set for this session")
                return True
            else:
                print("✗ No key entered")
                return False
        else:
            print("\n❌ Cannot run tests without Mistral API key")
            return False
    else:
        print("✓ MISTRAL_API_KEY found")
        return True

def main():
    """Main test runner."""
    print("\n" + "=" * 80)
    print("DATA ANALYSIS AGENT - TEST RUNNER")
    print("=" * 80)
    
    # Check API keys
    if not check_api_keys():
        sys.exit(1)
    
    print("\nStarting tests...\n")
    
    # Import and run tests
    try:
        from test_data_analysis_agent import run_all_tests
        results = run_all_tests()
        
        if results:
            print("\n✅ Test run completed successfully!")
            print("\nNext step: Review test_results.json and create test report")
        else:
            print("\n❌ Test run failed - check error messages above")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

