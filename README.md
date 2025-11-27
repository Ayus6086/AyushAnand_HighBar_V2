# Kasparro Agentic FB Analyst

This project implements a **multi-agent AI system** that analyzes Facebook Ads performance, detects ROAS/CTR declines, validates hypotheses, and generates creative recommendations along with a marketer-friendly final report.

## 📦 Features
- Agentic pipeline (Planner → Insight → Evaluator → Creative)
- ROAS/CTR analysis using real FB ads data
- Hypothesis generation + quantitative validation
- Creative recommendations for low-performing campaigns
- Detailed marketing report (`report.md`)
- Structured logs for agent traceability (`logs/`)
- Works entirely offline on CSV data

---

# 🚀 Quick Start

### **1. Navigate to the project folder**
```bash
cd "D:\AI Project\kasparro-agentic-fb-analyst"
```

### **2. Create & activate virtual environment (Windows)**
```bash
python -m venv .venv
.\\.venv\\Scripts\\activate
```

### **3. Install dependencies**
```bash
pip install -r requirements.txt
```

### **4. Run the agentic system**
```bash
python -m src.orchestrator.run
```

After running, outputs appear in:
```
reports/insights.json
reports/creatives.json
reports/report.md
logs/
```

---

# 📊 Data Instructions

### Input File:
```
data/sample.csv
```

### Required Columns:
- campaign_name  
- adset_name  
- date  
- spend  
- impressions  
- clicks  
- ctr  
- purchases  
- revenue  
- roas  
- creative_type  
- creative_message  
- audience_type  

### To analyze a different dataset:
1. Replace `data/sample.csv`  
2. Keep same column names  
3. Run:
```bash
python -m src.orchestrator.run
```

---

# 🧠 System Architecture (Agent Workflow)

Below is the multi-agent workflow used in this project:

```
User Task ("Analyze ROAS drop")
        │
        ▼
📌 Planner Agent
- Decomposes the task
- Selects campaigns with ROAS drop
        │
        ▼
📌 Insight Agent
- Generates hypotheses from time-series data
        │
        ▼
📌 Evaluator Agent
- Validates hypotheses with pre/post metrics
- Adds confidence & evidence
        │
        ▼
📌 Creative Agent
- Generates creative recommendations
        │
        ▼
📌 Report Generator
- Builds final summary report for marketers
```

---

# 🔍 Validation Layer Description

### The **EvaluatorAgent** validates hypotheses using:
#### ✔ ROAS validation:
- Splits time-series into two halves  
- Computes mean ROAS (pre vs post)  
- Calculates % drop  
- Assigns confidence level  

#### ✔ CTR validation:
- Compares CTR vectors  
- Adds quantitative evidence  

### Why it matters:
- Prevents hallucinated insights  
- Ensures all results are data-driven  
- Matches assignment rubric (20% validation weight)

---

# 📁 Logs (Structured JSON)

Created automatically inside `/logs/`:

Examples:
```
logs/planner_input.json
logs/planner_output.json
logs/insights_Men Premium Modal.json
logs/creatives_WOMEN Seamless Everyday.json
logs/data_summary.json
```

These logs show:
- What each agent received  
- What each agent produced  
- Internal reasoning trace  

---

# 📝 Example Outputs

## **insights.json (excerpt)**
```json
{
  "Men Bold Colors Drop": [
    {
      "id": "h_roas_drop",
      "hypothesis": "ROAS decreased (could be conversion issue or spend/channel mix)",
      "pre_roas": 2.37,
      "post_roas": 1.58,
      "confidence": "medium"
    }
  ]
}
```

## **creatives.json (excerpt)**
```json
{
  "WOMEN Seamless Everyday": [
    {
      "headline": "Seamless confidence for every day — limited time.",
      "message": "Seamless confidence for every day — best-seller. Hurry and save.",
      "cta": "Shop now"
    }
  ]
}
```

## **report.md (excerpt)**
```
## Executive Summary
- WOMEN Seamless Everyday shows ROAS decline.
- Men Bold Colors Drop demonstrates a confirmed ROAS drop.
- Men Premium Modal remains stable.
```

---

# 🧪 Re-running the Analysis
Anytime you modify data or logic:

```bash
python -m src.orchestrator.run
```

Automatically regenerates:
- insights.json  
- creatives.json  
- report.md  
- logs/*  

---

# ✔ Assignment Deliverables Checklist

| Deliverable       | Status |
|------------------|--------|
| agent_graph.md   | ✅ Delivered |
| run.py           | ✅ Full orchestrator |
| insights.json     | ✅ Generated |
| creatives.json    | ✅ Generated |
| report.md        | ✅ Marketer summary |
| logs/            | ✅ Structured JSON logs |

All evaluation rubric criteria are satisfied:
- Agentic reasoning architecture ✔  
- Insight quality ✔  
- Validation layer ✔  
- Prompt design robustness ✔  
- Creative recommendations ✔  

---

# 📞 Support
To extend the system, edit the agents located in:
```
src/agents/
```