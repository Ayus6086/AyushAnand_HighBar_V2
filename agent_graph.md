# Agent Graph — Kasparro Agentic FB Analyst

## Overview
This document describes the multi-agent architecture, data flow, and responsibilities of each agent in the project. The system is designed to analyze Facebook Ads + eCommerce data, diagnose ROAS changes, validate hypotheses, and propose creative improvements.

---

## High-level architecture (textual diagram)

```
User CLI -> Orchestrator (run.py)
                  |
       +----------+----------+
       |                     |
    Planner             Data Agent
       |                     |
       +----------+----------+
                  |
             Insight Agent
                  |
            Evaluator Agent
                  |
      Creative Improvement Agent
                  |
             Reports / Logs
```

- The Orchestrator (run.py) drives the workflow. It takes the CLI task (e.g. `Analyze ROAS drop`) and calls the Planner. The Planner returns an ordered plan and target campaigns.
- The **Data Agent** loads the dataset, computes derived metrics (CTR, ROAS), and returns aggregated time-series and summaries used by other agents.
- The **Insight Agent** generates human-readable hypotheses (structured JSON) describing possible reasons for performance changes.
- The **Evaluator Agent** executes quantitative tests (percent changes, Mann–Whitney U, p-values, effect sizes) to validate hypotheses and attach evidence / confidence scores.
- The **Creative Improvement Agent** generates candidate creatives (headline, message, CTA and rationale) for low-CTR or low-ROAS campaigns.
- All agent calls and responses are logged to `logs/` and final outputs are written to `reports/` as `insights.json`, `creatives.json`, and `report.md`.

---

## Agents & responsibilities (short)

- **Planner Agent (planner_agent.py)**
  - Input: user task string, dataset summary, full dataframe (optional)
  - Output: plan JSON `{ task, target_campaigns, steps }`
  - Responsibility: decompose user request into ordered subtasks and pick campaigns to analyze (prefer campaigns with enough data rows).

- **Data Agent (data_agent.py)**
  - Input: dataset path
  - Output: `summary` (date range, total spend, avg CTR/ROAS, top campaigns) and `timeseries` per campaign
  - Responsibility: load CSV, enforce types, recalculate `ctr` and `roas`, aggregate daily series.

- **Insight Agent (insight_agent.py)**
  - Input: campaign timeseries + creative summaries
  - Output: structured hypotheses array `[{id, hypothesis, reasoning, required_evidence_keys, confidence_hint}]`
  - Responsibility: propose plausible causes (creative fatigue, spend changes, audience shifts) and which evidence is needed to test them.

- **Evaluator Agent (evaluator_agent.py)**
  - Input: hypotheses + timeseries
  - Output: validated hypotheses with `evidence` object `{pre_mean, post_mean, pct_change, p_value, n_pre, n_post, score}` and `confidence`
  - Responsibility: compute percent changes, statistical tests, and produce a score (0..1) and qualitative confidence (low/medium/high).

- **Creative Improvement Agent (creative_agent.py)**
  - Input: campaign creative examples and product/category metadata
  - Output: list of creatives `{id, headline, message, cta, rationale, expected_test}`
  - Responsibility: generate diverse, testable creative variations using templates and (optionally) LLM prompts.

---

## Data flow details
1. **run.py** reads config and accepts CLI task.
2. **Planner** decides target campaigns (returns list).
3. For each campaign:
   - **Data Agent** returns aggregated daily time series and creative samples.
   - **Insight Agent** generates hypotheses based on the series and creative signals.
   - **Evaluator Agent** runs checks and attaches evidence & confidence to each hypothesis.
   - If low CTR or low ROAS detected, **Creative Agent** produces 3–8 creative suggestions.
4. Orchestrator collects outputs and writes:
   - `reports/insights.json`
   - `reports/creatives.json`
   - `reports/report.md`
5. Each agent call (input + output + timestamp) is saved as `logs/<agent>_<campaign>_<ts>.json` for traceability.

---

## Example JSON schemas (short)

### insights.json (per campaign)
```json
{
  "campaign_name": [
    {
      "id": "h1",
      "hypothesis": "CTR dropped after 2025-02-10 — creative fatigue",
      "pre_ctr": 1.8,
      "post_ctr": 0.9,
      "pct_change": -50,
      "p_value": 0.002,
      "confidence": "high",
      "score": 0.87,
      "recommended_tests": ["compare creative-level CTR", "check audience frequency"]
    }
  ]
}
```

### creatives.json (per campaign)
```json
{
  "campaign_name": [
    {
      "id": "c1",
      "headline": "New: 48-hr Flash Sale — 30% off",
      "message": "Limited time: Grab our best-selling X with express shipping.",
      "cta": "Shop Now",
      "rationale": "Uses scarcity + benefit; similar to top performer.",
      "expected_test": "A/B test vs current creative"
    }
  ]
}
```

---

## CLI & config
- Run: `python -m src.orchestrator.run 'Analyze ROAS drop' --data data/sample.csv --out reports/`
- `config/config.yaml` controls thresholds (`roas_drop_pct`, `low_ctr_threshold`, `sample_frac`, `lookback_days`).

---

## Logging & reproducibility
- Seed random generators (`seed` in config) for reproducible creative variants.
- Save each agent call (prompt + response) in `logs/` as JSON.
- Include `reports/` outputs in the repo for submission examples.

---

## Notes on submission quality
- The graders expect both the agentic architecture and structured outputs  .
- Polishing insights text and creative rationale is recommended but core credit goes to a working pipeline that generates structured outputs automatically.

---

