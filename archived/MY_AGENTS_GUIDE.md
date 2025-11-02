# Your Research Agent System - Complete Guide

## 🎯 What You Have Now

You have **3 research agents**, each with different strengths:

### 1. Research Agent (Exa)
**File**: `my_research_agent.py`
- **Best for**: Recent articles, today's news, keyword search
- **Tool**: Exa (searches only recent content)
- **Cost**: ~$0.02-0.05 per query
- **When to use**: "What's new today?", "Latest developments in..."

### 2. Google Search Agent (SerpAPI)
**File**: `my_serp_agent.py`
- **Best for**: General search, definitions, Google knowledge panels
- **Tool**: SerpAPI (full Google search results)
- **Cost**: ~$0.02-0.05 per query
- **When to use**: "What is...", "How does... work?", general research

### 3. Multi-Search Agent (Exa + SerpAPI)
**File**: `my_multi_search_agent.py`
- **Best for**: Comprehensive research, cross-referenced results
- **Tools**: Both Exa AND SerpAPI
- **Cost**: ~$0.03-0.08 per query (uses both when needed)
- **When to use**: Important research needing multiple sources

## 🚀 How to Run

### Quick Start - Choose Your Agent
```bash
cd /Users/hdz_agents/Projects/agno
source .venv/bin/activate
export OPENAI_API_KEY='your-key-here'
python run_all_agents.py
```

This will let you choose which agent to use interactively!

### Run Specific Agent

#### Exa Research Agent:
```bash
python run_research_interactive.py
```

#### Use in Your Code:
```python
# Option 1: Research Agent (Exa)
from my_research_agent import research_agent
response = research_agent.run("What's new in AI today?")

# Option 2: Google Search Agent (SerpAPI)
from my_serp_agent import serp_agent
response = serp_agent.run("What is quantum computing?")

# Option 3: Multi-Search Agent (Both)
from my_multi_search_agent import multi_search_agent
response = multi_search_agent.run("Comprehensive analysis of Tesla")
```

## 💰 Cost Comparison

| Agent | Tools Used | Cost per Query | Best For |
|-------|-----------|----------------|----------|
| Research Agent | Exa | ~$0.02-0.05 | Recent news |
| Google Agent | SerpAPI | ~$0.02-0.05 | General search |
| Multi-Search | Both | ~$0.03-0.08 | Deep research |

**Money-Saving Tips:**
1. Use specific agent for specific task (don't always use multi-search)
2. Ask focused questions
3. Consider switching to GPT-4o-mini (15x cheaper) for simple queries

## 📊 Which Agent Should You Use?

### Use Research Agent (Exa) when:
- ✅ You need TODAY's news
- ✅ Looking for recent articles
- ✅ Want keyword-based search
- ✅ Need sources published today

**Example queries:**
- "What happened with OpenAI today?"
- "Latest AI research papers"
- "Breaking news about Tesla"

### Use Google Agent (SerpAPI) when:
- ✅ You need definitions
- ✅ Want Google's featured snippets
- ✅ Need knowledge panel info
- ✅ Looking for established facts

**Example queries:**
- "What is machine learning?"
- "How does photosynthesis work?"
- "Who is the CEO of Apple?"
- "History of the internet"

### Use Multi-Search Agent when:
- ✅ You need comprehensive research
- ✅ Want multiple perspectives
- ✅ Need both recent AND historical info
- ✅ Research is important/critical

**Example queries:**
- "Comprehensive analysis of climate change"
- "Compare different AI models"
- "Full research on quantum computing developments"

## 🔧 Configuration & Customization

### Change to Cheaper Model (GPT-4o-mini)

Edit any agent file and change:
```python
# From:
model=OpenAIChat(id="gpt-4o")

# To:
model=OpenAIChat(id="gpt-4o-mini")  # 15x cheaper!
```

**Cost savings**: $0.15 per 1M tokens → $0.01 per 1M tokens

### Adjust Search Settings

**In my_research_agent.py (Exa):**
```python
ExaTools(
    api_key="your-key",
    start_published_date="2024-01-01",  # Change date range
    type="keyword",  # or "neural" for AI-powered search
    num_results=10,  # Limit results
)
```

**In my_serp_agent.py (SerpAPI):**
```python
SerpApiTools(
    api_key="your-key",
    # SerpAPI has auto-configuration, just works!
)
```

### Customize Instructions

Edit the `instructions` section in any agent file to change behavior:
```python
instructions=dedent("""\
    Your custom instructions here...
    - Step 1: Do this
    - Step 2: Do that
    """)
```

## 🎓 Advanced Usage - Adding More Agents

### Financial Research Agent (Free!)
```python
from agno.tools.yfinance import YFinanceTools

finance_agent = Agent(
    name="Finance Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools()],  # Free!
    instructions="Analyze stocks and financial data",
    db=SqliteDb(db_file="tmp/finance_agent.db"),
)
```

### Academic Research Agent (Free!)
```python
from agno.tools.arxiv import ArxivTools

academic_agent = Agent(
    name="Academic Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[ArxivTools()],  # Free!
    instructions="Find and summarize research papers",
    db=SqliteDb(db_file="tmp/academic_agent.db"),
)
```

### Create an Agent Team
```python
from agno.team.team import Team

research_team = Team(
    members=[research_agent, serp_agent, finance_agent],
    model=OpenAIChat(id="gpt-4o"),
    instructions="Work together to provide comprehensive research",
)

# Team automatically coordinates who does what
research_team.print_response("Analyze Tesla's market position", stream=True)
```

## 📁 Database & Memory

Each agent stores its conversations:
- `tmp/research_agent.db` - Exa agent conversations
- `tmp/serp_agent.db` - SerpAPI agent conversations  
- `tmp/multi_search_agent.db` - Multi-search agent conversations

**Benefits:**
- Remembers context across sessions
- Can reference previous conversations
- Builds long-term memory

**To start fresh:** Delete the database file

## ⚠️ Important Notes

### API Keys
Your keys are currently hardcoded in the agent files:
- **Exa**: `f786797a-3063-4869-ab3f-bb95b282f8ab`
- **SerpAPI**: `cf91e3f9c1ba39340e3b4dc3a905215d78790c2f9004520209b35878921f8a7b`
- **OpenAI**: Set via environment variable

### Rate Limits
- **OpenAI**: 10,000 requests/min (tier 1)
- **Exa**: Check your plan
- **SerpAPI**: Check your plan

### Cost Monitoring
Monitor usage at:
- OpenAI: https://platform.openai.com/usage
- Exa: https://exa.ai/dashboard
- SerpAPI: https://serpapi.com/dashboard

## 🆘 Troubleshooting

### "Module not found: agno"
```bash
source .venv/bin/activate
```

### "Invalid API key"
Check environment variable:
```bash
echo $OPENAI_API_KEY
```

### Agent not responding
1. Check internet connection
2. Verify API keys are valid
3. Check rate limits on dashboards
4. Try simpler query first

### Too expensive
1. Switch to GPT-4o-mini (edit model in agent file)
2. Use specific agents (not multi-search)
3. Ask focused questions
4. Limit follow-up questions

## 🎯 Quick Start Commands

### Interactive mode (choose agent):
```bash
python run_all_agents.py
```

### Exa research only:
```bash
python run_research_interactive.py
```

### In your own script:
```python
from my_research_agent import research_agent
response = research_agent.run("Your question")
print(response.content)
```

## 📚 Example Questions to Try

### For Research Agent (Exa):
- "What are today's top AI news?"
- "Latest developments in quantum computing"
- "Recent SpaceX launches"

### For Google Agent (SerpAPI):
- "What is the Fermi Paradox?"
- "How does blockchain work?"
- "History of artificial intelligence"

### For Multi-Search Agent:
- "Comprehensive analysis of GPT-4"
- "Compare different renewable energy sources"
- "Full research on CRISPR technology"

## 🎉 You're All Set!

You have 3 powerful research agents ready to use. Each one uses different search tools optimized for different tasks.

**Start researching:**
```bash
python run_all_agents.py
```

Choose your agent and start asking questions!

