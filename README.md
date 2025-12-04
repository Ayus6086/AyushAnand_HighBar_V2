# Kasparro Agentic FB Analyst

This project implements a **production-ready multi-agent AI system** that analyzes Facebook Ads performance, detects ROAS/CTR declines, validates hypotheses using real data, and generates creative recommendations — along with a marketer-friendly final report.

Designed to replicate real-world marketing analysis workflows using an **offline dataset**, with **logging, validation, schema checks, and tests** included.

## 📦 Features

- Full **agentic pipeline** (Planner → Insight → Evaluator → Creative)  
- Automated **ROAS/CTR trend analysis** on Facebook ads data  
- **Hypothesis generation + quantitative validation**  
- Auto-generated **creative recommendations** for weak campaigns  
- Final ready-to-share **marketing report (report.md)**  
- **Structured logs** for agent traceability (`logs/`)  
- **Schema drift detection + missing-data handling**  
- Works entirely **offline** on any CSV dataset with required columns 

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
The system automatically handles:
- Missing values
- Zero/negative anomalies
- Schema drift
- Type mismatches
---

# 🧠 System Architecture (Multi-Agent Workflow)

Below is the multi-agent workflow used in this project:

```
User Task ("Analyze ROAS drop")
        │
        ▼
📌 Planner Agent
- Identifies which campaigns have performance changes
- Selects focus campaigns
        │
        ▼
📌 Insight Agent
- Generates hypotheses from time-series data
- Analyzes ROAS/CTR time-series
        │
        ▼
📌 Evaluator Agent (V2 Upgrade)
- Adds quantitative validation:
      - Pre vs Post ROAS
      - Absolute Delta
      - Percentage Delta
      - Impact score (low/medium/high)
      - Confidence value (0–1)
        │
        ▼
📌 Creative Agent
- Creatives now reference the actual issue, not random ideas.
        │
        ▼
📌 Report Generator
- Builds final marketing report (report.md)
```

---

# 🔍 Validation Layer (V2 Requirement)

### The evaluator verifies:
✔ ROAS pre vs post
✔ CTR pre vs post
✔ Spend & impressions changes
✔ Delta % severity
✔ Confidence based on sample size + metric shift  

#### Error Handling & Schema Governance (V2 Upgrade)
Added:
- Required-column checks  
- Unexpected-column logs
- Retry logic on data load & metric calculations
- Inf/NaN cleaning
- Structured error logs:
  - logs/schema_error.json
  - logs/run_error.json
  - logs/data_load_error_attempt_*.json
Pipeline never silently fails.

### 📈 Observability
Automatically saved:
- logs/planner_input.json 
- logs/planner_output.json  
- logs/insights_<campaign>.json
- logs/creatives_<campaign>.json
- logs/metrics.json (execution timings, retries, error counts)
Metrics logged:
- Per-agent execution time
- Number of retries
- Total campaigns processed
- Error counts
This makes the system debuggable and production-friendly.

---
# 📝 Example Outputs

## **insights.json (excerpt)**
```json
{
  "WOMEN Seamless Everyday": [
    {
      "id": "h_roas_drop",
      "evidence": { "pre": 11.30, "post": 8.57, "delta_pct": -24.15 },
      "impact": "medium",
      "confidence": 0.60
    }
  ]
}
```

## **creatives.json (excerpt)**
```json
{
  "Men Bold Colors Drop": [
    {
      "headline": "Only today: extra savings",
      "linked_issue": "ROAS decreased significantly vs baseline"
    }
  ]
}
```

## **report.md (excerpt)**
```
## A clean marketing summary including:
- Executive summary
- Executive summary
- Creative prescriptions
- Next steps
- Files produced
```

---

# 🧪 Running Tests (V2 Requirement)

```bash
pytest tests
```
Covers:
- Schema validation
- Data calculations
- Evaluator logic

---

# 🛠 Developer Notes
Key Design Choices
- Schema validation balances strictness + flexibility
- Insights never rely on generic rules — all must be data-driven
- Creative links always reference the validated reason
- Modularity: each agent can be extended or replaced
- Deterministic processing ensures reproducibility

---
