content = '''OPENAI_API_KEY=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
EXA_API_KEY=f786797a-3063-4869-ab3f-bb95b282f8ab
SERP_API_KEY=cf91e3f9c1ba39340e3b4dc3a905215d78790c2f9004520209b35878921f8a7b

# Nursing Research Agents - Environment Configuration
# Copy this file to .env and fill in your actual API keys
#
# IMPORTANT: Never commit .env to version control!
# The .gitignore file already excludes .env

# =============================================================================
# REQUIRED API KEYS
# =============================================================================

# OpenAI API Key (Required for all agents)
# Get your key from: https://platform.openai.com/api-keys
# Used by: All 6 agents (GPT-4o model)

# Exa API Key (Required for Agent 1 only)
# Get your key from: https://exa.ai
# Used by: Agent 1 (Nursing Research Agent) for recent healthcare articles

# SerpAPI Key (Required for Agent 1 only)
# Get your key from: https://serpapi.com
# Used by: Agent 1 (Nursing Research Agent) for healthcare standards/guidelines

# =============================================================================
# OPTIONAL CONFIGURATION
# =============================================================================

# Logging Configuration
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
# Default: INFO
# AGENT_LOG_LEVEL=INFO

# Database Directory
# Default: /tmp/nursing_research_agents_db/
# Uncomment to override:
# AGENT_DB_DIR=/path/to/custom/db/directory

# =============================================================================
# SETUP INSTRUCTIONS
# =============================================================================
#
# 1. Copy this file:
#    cp .env.example .env
#
# 2. Edit .env and add your actual API keys
#
# 3. Verify .env is in .gitignore (it should be by default)
#
# 4. Test your setup:
#    python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
#
# =============================================================================
# AGENT-SPECIFIC REQUIREMENTS
# =============================================================================
#
# Agent 1 (Nursing Research): OPENAI_API_KEY, EXA_API_KEY, SERP_API_KEY
# Agent 2 (Medical Research): OPENAI_API_KEY only (PubMed is free)
# Agent 3 (Academic Research): OPENAI_API_KEY only (ArXiv is free)
# Agent 4 (Research Writing): OPENAI_API_KEY only
# Agent 5 (Project Timeline): OPENAI_API_KEY only
# Agent 6 (Data Analysis): OPENAI_API_KEY only
#
# =============================================================================
# SECURITY NOTES
# =============================================================================
#
# - NEVER commit your .env file to version control
# - NEVER share your API keys publicly
# - Rotate your API keys if they are ever exposed
# - Use separate API keys for development and production
# - Monitor your API usage and costs regularly
#
# OpenAI Pricing: https://openai.com/pricing
# Exa Pricing: https://exa.ai/pricing
# SerpAPI Pricing: https://serpapi.com/pricing
#
# =============================================================================
'''
with open('.env', 'w') as f:
    f.write(content)