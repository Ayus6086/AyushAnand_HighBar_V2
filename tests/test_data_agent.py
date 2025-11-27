import pandas as pd
from src.agents.data_agent import DataAgent

def test_add_metrics():
    df = pd.DataFrame([{
        'date':'2025-01-01','campaign_name':'c1',
        'impressions':100,'clicks':5,'spend':10.0,'revenue':20.0,'creative_text':'x'
    }])
    df['date'] = pd.to_datetime(df['date'])
    da = DataAgent(sample_frac=0)
    df2 = da.add_metrics(df)
    assert 'ctr' in df2.columns
    assert round(df2['ctr'].iloc[0], 5) == 5.0
    assert round(df2['roas'].iloc[0], 5) == 2.0
