import uuid

class CreativeAgent:
    def __init__(self):
        pass

    def suggest(self, campaign_name, top_examples):
        suggestions = []
        base = "Our product"
        if top_examples:
            first = top_examples[0]
            words = str(first).split()
            base = " ".join(words[:5]) if words else base

        templates = [
            "{benefit} — limited time. {cta}",
            "New: {benefit}. {cta}",
            "Only today: {discount} off! {cta}"
        ]
        for idx, t in enumerate(templates):
            suggestions.append({
                'id': str(uuid.uuid4())[:8],
                'headline': t.format(benefit=base, discount="25%", cta="Shop now"),
                'message': f"{base} — best-seller. Hurry up and save.",
                'cta': "Shop now",
                'rationale': "Pattern: benefit + urgency, similar to top performers"
            })
        return suggestions
