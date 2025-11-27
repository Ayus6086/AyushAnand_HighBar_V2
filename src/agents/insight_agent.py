class InsightAgent:
    def __init__(self):
        pass

    def generate_hypotheses(self, campaign_name, timeseries):
        n = len(timeseries)
        if n < 6:
            return [{'id':'h0','hypothesis':'insufficient data','confidence':'low'}]

        half = n // 2
        pre = timeseries[:half]
        post = timeseries[half:]

        def avg(key, arr):
            vals = [d.get(key, 0) for d in arr]
            return sum(vals)/len(vals) if vals else 0

        pre_ctr = avg('ctr', pre)
        post_ctr = avg('ctr', post)
        pre_roas = avg('roas', pre)
        post_roas = avg('roas', post)
        hypos = []
        if post_ctr < pre_ctr * 0.85:
            hypos.append({
                'id':'h_ctr_drop',
                'hypothesis': 'CTR decreased (possible creative or targeting issue)',
                'pre_ctr': pre_ctr,
                'post_ctr': post_ctr,
                'confidence': 'medium'
            })
        if post_roas < pre_roas * 0.85:
            hypos.append({
                'id':'h_roas_drop',
                'hypothesis': 'ROAS decreased (could be conversion issue or spend/channel mix)',
                'pre_roas': pre_roas,
                'post_roas': post_roas,
                'confidence': 'medium'
            })
        if not hypos:
            hypos.append({'id':'h_none', 'hypothesis':'No major change detected','confidence':'low'})
        return hypos
