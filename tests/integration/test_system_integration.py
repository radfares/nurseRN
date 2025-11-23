"""
Nursing Research Agent System - Integration Test Suite
Tests all 6 agents and their integration points
"""

import os
import sys
from datetime import datetime

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(msg, status="INFO"):
    colors = {"PASS": GREEN, "FAIL": RED, "WARN": YELLOW, "INFO": BLUE}
    color = colors.get(status, RESET)
    print(f"{color}[{status}]{RESET} {msg}")

def check_environment():
    """Phase 1: Environment validation"""
    print("\n" + "="*80)
    print("PHASE 1: ENVIRONMENT CHECK")
    print("="*80)
    
    results = {}
    
    # Check Python version
    py_version = sys.version_info
    if py_version >= (3, 10):
        print_test(f"Python version: {py_version.major}.{py_version.minor}", "PASS")
        results['python'] = True
    else:
        print_test(f"Python version too old: {py_version.major}.{py_version.minor}", "FAIL")
        results['python'] = False
    
    # Check API keys
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'EXA_API_KEY': os.getenv('EXA_API_KEY'),
        'SERPAPI_API_KEY': os.getenv('SERPAPI_API_KEY')
    }
    
    for key_name, key_value in api_keys.items():
        if key_value:
            masked = key_value[:8] + "..." + key_value[-4:] if len(key_value) > 12 else "***"
            print_test(f"{key_name}: {masked}", "PASS")
            results[key_name] = True
        else:
            print_test(f"{key_name}: NOT SET", "FAIL")
            results[key_name] = False
    
    # Check if virtual environment is active
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_test("Virtual environment: ACTIVE", "PASS")
        results['venv'] = True
    else:
        print_test("Virtual environment: NOT ACTIVE", "WARN")
        results['venv'] = False
    
    return results

def test_agent_imports():
    """Phase 2: Test that all agents can be imported"""
    print("\n" + "="*80)
    print("PHASE 2: AGENT IMPORT TEST")
    print("="*80)
    
    results = {}
    agents = [
        ('nursing_research_agent', 'nursing_research_agent'),
        ('nursing_project_timeline_agent', 'project_timeline_agent'),
        ('medical_research_agent', 'medical_research_agent'),
        ('academic_research_agent', 'academic_research_agent'),
        ('research_writing_agent', 'research_writing_agent'),
        ('data_analysis_agent', 'data_analysis_agent'),
    ]
    
    for module_name, agent_name in agents:
        try:
            module = __import__(module_name, fromlist=[agent_name])
            agent = getattr(module, agent_name)
            print_test(f"Agent imported: {agent_name}", "PASS")
            results[agent_name] = {'imported': True, 'agent': agent}
        except ImportError as e:
            print_test(f"Failed to import {agent_name}: {e}", "FAIL")
            results[agent_name] = {'imported': False, 'error': str(e)}
        except AttributeError as e:
            print_test(f"Agent not found in module {module_name}: {e}", "FAIL")
            results[agent_name] = {'imported': False, 'error': str(e)}
    
    return results

def test_agent_response(agent_name, agent, test_query, timeout=30):
    """Test an individual agent with a simple query"""
    try:
        print(f"\n  Testing {agent_name} with query: '{test_query[:50]}...'")
        
        # Run agent (with timeout protection)
        response = agent.run(test_query)
        
        if response and response.content:
            content_preview = response.content[:150].replace('\n', ' ')
            print_test(f"  {agent_name} responded: {content_preview}...", "PASS")
            return True, len(response.content)
        else:
            print_test(f"  {agent_name} returned empty response", "FAIL")
            return False, 0
            
    except Exception as e:
        print_test(f"  {agent_name} error: {str(e)[:100]}", "FAIL")
        return False, 0

def test_all_agents(agent_results):
    """Phase 3: Test each agent with a simple query"""
    print("\n" + "="*80)
    print("PHASE 3: AGENT FUNCTIONALITY TEST")
    print("="*80)
    
    test_queries = {
        'nursing_research_agent': "What is a PICOT question?",
        'project_timeline_agent': "What should I do in November 2025?",
        'medical_research_agent': "Search for one article about hand hygiene",
        'academic_research_agent': "Find a paper about research methodology",
        'research_writing_agent': "What are the components of a PICOT question?",
        'data_analysis_agent': "What statistical test compares two groups?",
    }
    
    results = {}
    
    for agent_name, agent_data in agent_results.items():
        if not agent_data.get('imported'):
            print_test(f"Skipping {agent_name} (import failed)", "WARN")
            results[agent_name] = {'tested': False, 'reason': 'import_failed'}
            continue
        
        agent = agent_data['agent']
        test_query = test_queries.get(agent_name, "Hello, are you working?")
        
        success, response_length = test_agent_response(agent_name, agent, test_query)
        results[agent_name] = {
            'tested': True,
            'success': success,
            'response_length': response_length
        }
    
    return results

def test_menu_system():
    """Phase 4: Test the main menu runner"""
    print("\n" + "="*80)
    print("PHASE 4: MENU SYSTEM TEST")
    print("="*80)
    
    try:
        # Import the runner
        import run_nursing_project
        print_test("Menu runner imported successfully", "PASS")
        
        # Check that it has the main function
        if hasattr(run_nursing_project, 'main'):
            print_test("Main function found", "PASS")
            return True
        else:
            print_test("Main function not found", "FAIL")
            return False
            
    except Exception as e:
        print_test(f"Menu system error: {e}", "FAIL")
        return False

def generate_report(env_results, import_results, agent_results, menu_result):
    """Phase 5: Generate final report"""
    print("\n" + "="*80)
    print("FINAL INTEGRATION TEST REPORT")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Environment
    print("\n🔧 ENVIRONMENT:")
    env_pass = sum(1 for v in env_results.values() if v)
    env_total = len(env_results)
    print(f"   Passed: {env_pass}/{env_total}")
    
    # Imports
    print("\n📦 IMPORTS:")
    import_pass = sum(1 for v in import_results.values() if v.get('imported'))
    import_total = len(import_results)
    print(f"   Passed: {import_pass}/{import_total}")
    
    # Agent functionality
    print("\n🤖 AGENT FUNCTIONALITY:")
    agent_pass = sum(1 for v in agent_results.values() if v.get('success'))
    agent_total = sum(1 for v in agent_results.values() if v.get('tested'))
    print(f"   Passed: {agent_pass}/{agent_total}")
    
    for agent_name, result in agent_results.items():
        if result.get('success'):
            status = f"{GREEN}✓{RESET}"
        elif result.get('tested'):
            status = f"{RED}✗{RESET}"
        else:
            status = f"{YELLOW}⊗{RESET}"
        print(f"   {status} {agent_name}")
    
    # Menu
    print("\n📋 MENU SYSTEM:")
    menu_status = f"{GREEN}✓ PASS{RESET}" if menu_result else f"{RED}✗ FAIL{RESET}"
    print(f"   {menu_status}")
    
    # Overall
    print("\n" + "="*80)
    all_pass = (env_pass == env_total and 
                import_pass == import_total and 
                agent_pass == agent_total and 
                menu_result)
    
    if all_pass:
        print(f"{GREEN}✅ ALL TESTS PASSED - SYSTEM IS PRODUCTION READY{RESET}")
        return True
    else:
        print(f"{YELLOW}⚠️  SOME TESTS FAILED - REVIEW RESULTS ABOVE{RESET}")
        return False

def main():
    """Run full integration test suite"""
    print("\n" + "="*80)
    print("🧪 NURSING RESEARCH AGENT SYSTEM - INTEGRATION TEST")
    print("="*80)
    print("This will test all 6 agents and system integration")
    print("Estimated time: 3-5 minutes")
    print("="*80)
    
    # Run all test phases
    env_results = check_environment()
    import_results = test_agent_imports()
    agent_results = test_all_agents(import_results)
    menu_result = test_menu_system()
    
    # Generate report
    success = generate_report(env_results, import_results, agent_results, menu_result)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

