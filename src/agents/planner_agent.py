class PlannerAgent:
    def __init__(self, roas_drop_pct=20):
        self.roas_drop_pct = roas_drop_pct

    def decompose(self, task_text, data_summary, df=None):
        """
        Improved planner:
        Select campaigns with the MOST data points (at least 10 days).
        """
        if df is None:
            raise ValueError("PlannerAgent needs full dataframe")

        counts = df['campaign_name'].value_counts()

        eligible = counts[counts >= 10]

        if eligible.empty:
            eligible = counts.head(3)

        target_campaigns = eligible.head(3).index.tolist()

        plan = {
            "task": task_text,
            "target_campaigns": target_campaigns,
            "steps": [
                "get timeseries",
                "generate hypotheses",
                "evaluate hypotheses",
                "generate creatives if needed"
            ]
        }
        return plan
