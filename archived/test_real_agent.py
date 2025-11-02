from data_analysis_agent import data_analysis_agent

print("=" * 80)
print("REAL API TEST - Data Analysis Agent")
print("=" * 80)
print("\nQuery: Catheter infection baseline 15%, target 8%. Sample size?\n")
print("-" * 80)

response = data_analysis_agent.run('Catheter infection rate: baseline 15%, target 8%. Need sample size for α=0.05, power=0.80')

print("\nFULL RESPONSE:")
print(response.content)
print("\n" + "=" * 80)
print("✅ TEST COMPLETE - Agent is working!")

