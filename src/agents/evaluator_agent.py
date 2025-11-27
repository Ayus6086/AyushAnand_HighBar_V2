from scipy import stats
def pct_change(old, new):
    if old == 0:
        return float('inf') if new>0 else 0.0
    return (new - old) / abs(old) * 100

class EvaluatorAgent:
    def validate_roas_change(self, pre_vals, post_vals):
        pre_mean = sum(pre_vals)/len(pre_vals) if pre_vals else 0
        post_mean = sum(post_vals)/len(post_vals) if post_vals else 0
        pct = pct_change(pre_mean, post_mean)
        p_value = 1.0
        try:
            _, p_value = stats.mannwhitneyu(pre_vals, post_vals, alternative='two-sided')
        except Exception:
            p_value = 1.0
        return {
            "pre_mean": pre_mean,
            "post_mean": post_mean,
            "pct_change": pct,
            "p_value": float(p_value),
            "n_pre": len(pre_vals),
            "n_post": len(post_vals)
        }
