# New Research Agents - Quick Guide

## 🆕 What's New

I've added **2 specialized research agents** to help you find peer-reviewed literature for your nursing project!
- All agents now share a standardized reasoning framework—see each agent’s "Reasoning Approach" block for how they break down questions.
- Want a lighter prompt? Set `REASONING_BLOCK=off` to disable the standardized reasoning blocks (defaults on).

---

## 🏥 Medical Research Agent (PubMed)

### What It Does
Searches **PubMed** - the world's largest database of biomedical and nursing research with over 35 million citations!

### Perfect For:
- ✅ Finding your **3 required research articles** (January requirement!)
- ✅ Peer-reviewed clinical studies
- ✅ Nursing research and systematic reviews
- ✅ Evidence-based practice guidelines
- ✅ Clinical trials and meta-analyses

### Example Questions:
```
"Find recent peer-reviewed studies on fall prevention in elderly hospitalized patients"

"Search for evidence-based interventions for catheter-associated urinary tract infections"

"Find 3 systematic reviews about pressure ulcer prevention published in the last 5 years"

"What are the latest studies on medication reconciliation effectiveness?"

"Find nursing research on patient safety culture in hospitals"
```

### When to Use:
- **January 2026** - Literature search phase
- Finding specific clinical studies
- Need peer-reviewed medical/nursing research
- Require evidence-based practice information

### Cost:
- **FREE** to search PubMed!
- Only costs for OpenAI GPT-4o processing (~$0.01-0.03 per search)

---

## 📚 Academic Research Agent (Arxiv)

### What It Does
Searches **Arxiv** - repository of academic papers in science, math, computer science, and related fields.

### Perfect For:
- ✅ Statistical analysis methods
- ✅ Data analysis techniques
- ✅ Research methodologies
- ✅ AI/ML applications in healthcare
- ✅ Theoretical frameworks
- ✅ Advanced quantitative methods

### Example Questions:
```
"Find papers on statistical methods for healthcare quality improvement"

"Search for research on machine learning for patient outcome prediction"

"Find studies about data collection methods in clinical research"

"What are the best practices for analyzing pre/post intervention data?"

"Find papers on epidemiological modeling of hospital infections"
```

### When to Use:
- **March 2026** - Planning data analysis
- Need advanced statistical methods
- Looking for research methodologies
- Want cutting-edge analytical techniques

### Cost:
- **FREE** to search Arxiv!
- Only costs for OpenAI GPT-4o processing (~$0.01-0.03 per search)

---

## 🎯 Which Agent Should You Use?

### Use Medical Research Agent (PubMed) when:
- 📋 Finding articles for your literature review
- 🏥 Need clinical/nursing research
- 📊 Want evidence-based practice guidelines
- ✅ **This is your PRIMARY agent for January!**

### Use Academic Research Agent (Arxiv) when:
- 📈 Need statistical analysis methods
- 🔬 Looking for research methodologies
- 💡 Want theoretical frameworks
- 📊 Need advanced data analysis techniques

### Use Original Research Agent (Exa + SerpAPI) when:
- 🌐 General web research
- 📰 Recent news and updates
- 📋 Healthcare standards (Joint Commission)
- 🔍 Broad topic exploration

### Use Timeline Assistant when:
- 📅 Check what's due
- ✅ Track milestones
- 📝 Plan next steps
- 📧 Need contact information

---

## 💡 Pro Tips for Literature Search

### For PubMed Agent:

**Be Specific:**
- ❌ "Fall prevention" (too broad)
- ✅ "Fall prevention interventions in elderly hospitalized patients"

**Include Key Terms:**
- Patient population (elderly, pediatric, adults)
- Setting (hospital, nursing home, community)
- Intervention type (education, protocol, technology)
- Outcome (reduction, improvement, effectiveness)

**Request Specific Info:**
```
"Find 3 recent peer-reviewed articles about [topic] and for each provide:
- Title and authors
- Publication year and journal
- Key findings
- Study design
- Sample size
- Clinical implications"
```

### For Arxiv Agent:

**Focus on Methods:**
- "Statistical methods for..."
- "Data analysis techniques for..."
- "Machine learning approaches to..."

**Combine with Your Topic:**
- "Statistical methods for analyzing fall prevention programs"
- "Data visualization techniques for healthcare quality metrics"

---

## 📅 When to Use Each Agent (Timeline)

### November 2025 (Topic Selection):
- Use: **Timeline Assistant** + **Research Agent (Exa)**
- For: Planning, brainstorming, standards

### December 2025 (PICOT Development):
- Use: **Research Agent (Exa)** + **Timeline Assistant**
- For: PICOT development, standards research

### January 2026 (Literature Search):
- Use: **Medical Research Agent (PubMed)** ⭐ PRIMARY
- Also: **Academic Research Agent (Arxiv)** if needed
- For: Finding your 3 required articles!

### February-March 2026 (Intervention Planning):
- Use: **Medical Research Agent** + **Academic Research Agent**
- For: Evidence-based interventions, data collection methods

### April 2026 (Poster Preparation):
- Use: All agents as needed
- For: Final literature review, conclusions

---

## 🚀 How to Access New Agents

### Run the system:
```bash
./start_nursing_project.sh
```

### Choose your agent:
```
Choose assistant (1/2/3/4):
1. Research Agent (Exa + SerpAPI) - General research
2. Timeline Assistant - Project planning
3. Medical Research Agent (PubMed) - Medical literature 🆕
4. Academic Research Agent (Arxiv) - Academic papers 🆕
```

---

## 💰 Cost Information

### Both New Agents:
- **Database Access**: FREE (PubMed and Arxiv are free)
- **OpenAI Processing**: ~$0.01-0.03 per query
- **Total Cost**: Same as your other agents!

### Estimated Usage:
- January literature search: $1-3 total
  - ~50-100 searches to find perfect articles
  - Review abstracts, refine searches
  - Final selection of 3 articles

---

## 📋 Example Workflow for January

### Week 1: Broad Search
```
Agent: Medical Research Agent (PubMed)

Query: "Find recent systematic reviews and meta-analyses 
about fall prevention in hospitalized elderly patients 
published in the last 5 years"
```

### Week 2: Refine Search
```
Agent: Medical Research Agent (PubMed)

Query: "Find specific intervention studies about fall 
prevention that include pre-post data analysis and 
were conducted in medical-surgical units"
```

### Week 3: Methodology Research
```
Agent: Academic Research Agent (Arxiv)

Query: "Find papers on statistical methods for 
analyzing fall prevention program effectiveness"
```

### Week 4: Final Selection
```
Agent: Medical Research Agent (PubMed)

Query: "Find the full text availability and detailed 
methodology for these PMIDs: [IDs from previous searches]"
```

---

## ⚠️ Important Notes

### PubMed Agent:
- Searches medical/nursing literature
- Returns PMIDs (PubMed IDs) - use these to find full articles
- May need institutional access for full text (check with librarian!)
- Focus on abstracts for your initial analysis

### Arxiv Agent:
- All papers are open access (free full text!)
- More theoretical/methodological
- Great for statistical and analytical methods
- May be more technical than clinical studies

### Getting Full Articles:
1. Use PMID from PubMed results
2. Contact Laura Arrick (librarian) - Larrick1@hfhs.org
3. Check hospital library access
4. Use Google Scholar as backup

---

## 🎓 You're Ready!

You now have **4 specialized agents** for your project:
1. ✅ Research Agent - General & standards
2. ✅ Timeline Assistant - Project management
3. ✅ Medical Research Agent - Clinical literature 🆕
4. ✅ Academic Research Agent - Academic papers 🆕

**Perfect for your January literature search phase!**

Run `./start_nursing_project.sh` to start using them! 🏥
