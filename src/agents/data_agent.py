import pandas as pd

class DataAgent:
    def __init__(self, sample_frac=0.2):
        self.sample_frac = sample_frac

    def load(self, path):
        df = pd.read_csv(path, parse_dates=['date'])
        if 0 < self.sample_frac < 1:
            return df.sample(frac=self.sample_frac, random_state=42).reset_index(drop=True)
        return df

    def add_metrics(self, df):
        df = df.copy()
        df['impressions'] = df['impressions'].fillna(0).astype(float)
        df['clicks'] = df['clicks'].fillna(0).astype(float)
        df['spend'] = df['spend'].fillna(0).astype(float)
        df['revenue'] = df['revenue'].fillna(0).astype(float)

        df['ctr'] = (df['clicks'] / df['impressions']).replace([float('inf')], 0).fillna(0) * 100
        df['roas'] = (df['revenue'] / df['spend']).replace([float('inf')], 0).fillna(0)
        return df

    def summarize(self, df):
        df2 = self.add_metrics(df)
        date_min = df2['date'].min()
        date_max = df2['date'].max()
        summary = {
            'date_range': [str(date_min.date()), str(date_max.date())],
            'total_spend': float(df2['spend'].sum()),
            'avg_ctr': float(df2['ctr'].mean()),
            'avg_roas': float(df2['roas'].mean()),
            'campaigns_count': int(df2['campaign_name'].nunique()),
            'top_by_roas': df2.groupby('campaign_name')['roas'].mean().sort_values(ascending=False).to_dict()
        }
        return summary

    def aggregate_timeseries(self, df, group_by='campaign_name'):
        df = self.add_metrics(df)
        out = {}
        for name, g in df.groupby(group_by):
            agg = g.set_index('date').resample('D').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'spend': 'sum',
                'revenue': 'sum'
            }).fillna(0)
            agg['ctr'] = (agg['clicks'] / agg['impressions']).replace([float('inf')], 0).fillna(0) * 100
            agg['roas'] = (agg['revenue'] / agg['spend']).replace([float('inf')], 0).fillna(0)
            out[name] = agg.reset_index().to_dict(orient='records')
        return out
