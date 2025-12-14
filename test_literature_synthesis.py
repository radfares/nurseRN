"""
Verification Test for Literature Synthesis Agent
Tests that the agent can synthesize 4+ articles into structured output
"""

from agents.medical_research_agent import get_medical_research_agent

# Get agent (returns LiteratureSynthesisAgent via backward compat alias)
synthesis_agent = get_medical_research_agent()

print("=" * 80)
print("LITERATURE SYNTHESIS AGENT - VERIFICATION TEST")
print("=" * 80)

# Test query: 4 sample articles about fall prevention
test_query = """
Synthesize these 4 fall prevention articles:

Article 1: "Hourly Rounding and Fall Rates" by Smith et al. 2020
- Sample: 150 patients
- Method: RCT
- Finding: 30% reduction in falls

Article 2: "Bed Alarm Effectiveness" by Johnson 2019
- Sample: 80 patients
- Method: Cohort study
- Finding: 22% reduction in falls

Article 3: "Fall Risk Assessment Tools" by Williams 2021
- Sample: 200 patients  
- Method: Meta-analysis
- Finding: Risk assessment alone insufficient

Article 4: "Multifactorial Intervention Study" by Brown 2018
- Sample: 120 patients
- Method: Case-control
- Finding: Combined interventions effective

Please provide:
1. Comparison table
2. Common themes
3. Research gaps
4. Evidence strength summary
"""

print("\n📝 Test Query:")
print(test_query)

print("\n🤖 Agent Response:")
print("-" * 80)

try:
    # Run agent - should output structured synthesis
    response = synthesis_agent.run_with_grounding_check(test_query)
    
    print(response.content if hasattr(response, 'content') else response)
    
    print("\n" + "=" * 80)
    print("✅ Verification Complete")
    print("=" * 80)
    
    print("\nCheck for required elements:")
    content_str = str(response.content if hasattr(response, 'content') else response)
    
    checks = {
        "Comparison Table": ("comparison" in content_str.lower() or "table" in content_str.lower()),
        "Themes Section": "theme" in content_str.lower(),
        "Gaps Section": "gap" in content_str.lower(),
        "Evidence Strength": "evidence" in content_str.lower() or "strong" in content_str.lower(),
        "Synthesis Statement": len(content_str) > 200  # Should have substantial content
    }
    
    for check_name, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {'PASS' if passed else 'FAIL'}")
    
    if all(checks.values()):
        print("\n🎉 ALL CHECKS PASSED - Agent working correctly!")
    else:
        print("\n⚠️ Some checks failed - review output format")

except Exception as e:
    print(f"\n❌ Error during synthesis: {e}")
    import traceback
    traceback.print_exc()
