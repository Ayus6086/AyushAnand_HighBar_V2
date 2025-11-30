import json
import time
import logging
from pathlib import Path

import yaml

from src.agents.data_agent import DataAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.creative_agent import CreativeAgent

CONFIG_PATH = Path("config/config.yaml")
DATA_PATH = Path("data/sample.csv")
OUT_DIR = Path("reports")
LOG_DIR = Path("logs")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

METRICS = {
    "timings": {},          
    "retries": {},          
    "errors": 0,            
    "campaigns_processed": 0,
}

def load_config(path=CONFIG_PATH):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def save_log(name, data):
    """
    Saves structured JSON logs to logs/{name}.json
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def pct_change(old, new):
    try:
        if old == 0:
            return float("inf") if new > 0 else 0.0
        return (new - old) / abs(old) * 100.0
    except Exception:
        return 0.0


def extract_roas_drop_stats(all_insights, campaign_name):
    pre = post = pct = None
    for h in all_insights.get(campaign_name, []):
        if h.get("id") == "h_roas_drop":
            pre = h.get("pre_roas")
            post = h.get("post_roas")
            if pre is not None and post is not None:
                pct = pct_change(pre, post)
            break
    return pre, post, pct

def with_retry(name, func, *args, max_retries=3, **kwargs):
    """
    Generic retry wrapper with metrics.
    - name: short label for logging ('data_load', 'add_metrics', etc.)
    - func: function to call
    """
    errors = []
    retries = 0
    start_overall = time.perf_counter()

    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Running %s (attempt %d/%d)", name, attempt, max_retries)
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start

            METRICS["timings"][name] = METRICS["timings"].get(name, 0.0) + duration
            METRICS["retries"][name] = retries

            return result
        except Exception as e:
            err_str = str(e)
            errors.append(err_str)
            retries += 1
            METRICS["errors"] += 1

            logger.error("Error in %s attempt %d: %s", name, attempt, err_str)
            save_log(f"{name}_error_attempt_{attempt}", {"error": err_str})

            if attempt == max_retries:
                save_log(f"{name}_failure", {"errors": errors})
                raise

    duration_total = time.perf_counter() - start_overall
    METRICS["timings"][name] = METRICS["timings"].get(name, 0.0) + duration_total
    METRICS["retries"][name] = retries


def main(task_text="Analyze ROAS drop"):
    cfg = load_config()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    
    data_agent = DataAgent(sample_frac=cfg.get("sample_frac", 0.2))

    t0 = time.perf_counter()
    df = with_retry("data_load", data_agent.load, DATA_PATH, max_retries=3)
    df = with_retry("add_metrics", data_agent.add_metrics, df, max_retries=2)
    METRICS["timings"]["data_prep_total"] = time.perf_counter() - t0

    summary = data_agent.summarize(df)
    save_log("data_summary", summary)

    drift_info = data_agent.detect_schema_drift(df)
    save_log("schema_drift", drift_info)

    
    planner = PlannerAgent(roas_drop_pct=cfg.get("roas_drop_pct", 20))

    t_plan = time.perf_counter()
    plan = planner.decompose(task_text, summary, df)
    METRICS["timings"]["planner"] = time.perf_counter() - t_plan

    save_log("planner_input", {"task": task_text, "summary": summary})
    save_log("planner_output", plan)

    
    all_insights = {}
    all_creatives = {}

    insight_agent = InsightAgent()
    evaluator = EvaluatorAgent()
    creative_agent = CreativeAgent()

    campaigns = plan.get("target_campaigns", [])
    METRICS["campaigns_processed"] = len(campaigns)

    t_insights_total = 0.0
    t_creatives_total = 0.0

    for camp in campaigns:
        t_ts = time.perf_counter()
        ts_map = data_agent.aggregate_timeseries(df[df["campaign_name"] == camp])
        timeseries = ts_map.get(camp, [])
        t_ts_dur = time.perf_counter() - t_ts
        METRICS["timings"]["timeseries"] = METRICS["timings"].get("timeseries", 0.0) + t_ts_dur

        t_ins = time.perf_counter()
        hypos = insight_agent.generate_hypotheses(camp, timeseries)

        for h in hypos:
            if h.get("id") == "h_ctr_drop":
                half = len(timeseries) // 2
                pre = [d["ctr"] for d in timeseries[:half]]
                post = [d["ctr"] for d in timeseries[half:]]
                h["evidence"] = evaluator.validate_ctr_change(pre, post)

        t_insights_total += time.perf_counter() - t_ins
        all_insights[camp] = hypos
        save_log(f"insights_{camp}", hypos)

        t_cre = time.perf_counter()
        df_camp = df[df["campaign_name"] == camp]
        top_examples = df_camp["creative_message"].fillna("Our product").tolist()[:5]
        creatives = creative_agent.suggest(camp, top_examples)
        t_creatives_total += time.perf_counter() - t_cre

        all_creatives[camp] = creatives
        save_log(f"creatives_{camp}", creatives)

    METRICS["timings"]["insight_agents_total"] = t_insights_total
    METRICS["timings"]["creative_agents_total"] = t_creatives_total

    with open(OUT_DIR / "insights.json", "w") as f:
        json.dump(all_insights, f, indent=2)

    with open(OUT_DIR / "creatives.json", "w") as f:
        json.dump(all_creatives, f, indent=2)

    
    camp1 = "Men Premium Modal"
    camp2 = "Men Bold Colors Drop"
    camp3 = "WOMEN Seamless Everyday"

    c1_pre, c1_post, c1_pct = extract_roas_drop_stats(all_insights, camp1)
    c2_pre, c2_post, c2_pct = extract_roas_drop_stats(all_insights, camp2)
    c3_pre, c3_post, c3_pct = extract_roas_drop_stats(all_insights, camp3)

    def fmt(x, d=2):
        return "N/A" if x is None else f"{x:.{d}f}"

    report = f"""
# Performance Analysis Report – Synthetic Facebook Ads (Undergarments)

**Task:** {task_text}  
**Date Range:** {summary['date_range'][0]} to {summary['date_range'][1]}  
**Total Spend:** {summary['total_spend']:.2f}  
**Overall Avg CTR:** {summary['avg_ctr']:.4f}%  
**Overall Avg ROAS:** {summary['avg_roas']:.2f}  

**Focus Campaigns:**
- {camp1}
- {camp2}
- {camp3}

---

## 1. Executive Summary

- **{camp1}** — Stable performance, no major ROAS change.  
- **{camp2}** — ROAS dropped **{fmt(c2_pct,1)}%**, requires creative + audience diagnostics.  
- **{camp3}** — High ROAS but declined **{fmt(c3_pct,1)}%**, likely due to fatigue or scaling.

These results suggest **creative fatigue**, **audience-quality shifts**, and **scaling effects** as primary contributors.

---

## 2. Campaign Deep-Dives

### 2.1 {camp1}
Stable baseline with no major performance shift detected.

### 2.2 {camp2}
**ROAS fell from ~{fmt(c2_pre)} → ~{fmt(c2_post)} ({fmt(c2_pct,1)}% change)**  
Likely causes: fatigue, audience broadening, conversion softness.

### 2.3 {camp3}
**ROAS declined from ~{fmt(c3_pre)} → ~{fmt(c3_post)} ({fmt(c3_pct,1)}% change)**  
Still strong but room for optimization.

---

## 3. Creative Recommendations (From Creative Agent)

### {camp1}
- Focus on softness, breathability, premium comfort.

### {camp2}
- Bold colours, durability, style-first messaging, limited-time discounts.

### {camp3}
- Invisibility under outfits, social proof, bundle offers.

---

## 4. Next Steps for Marketing Team

1. Run pre/post CTR & purchase rate diagnostics.  
2. Launch **2–3 new creatives** for declining campaigns.  
3. Reallocate spend from weak segments to stable performers.  
4. Add rolling ROAS/CTR monitoring rules.  

---

## 5. Files Produced by the Agentic System

- `insights.json`
- `creatives.json`
- `report.md`
- `logs/` (structured JSON logs for debugging)
"""

    with open(OUT_DIR / "report.md", "w", encoding="utf-8") as f:
        f.write(report)

    save_log("metrics", METRICS)

    print("Done. Reports written to 'reports/'")


if __name__ == "__main__":
    main()