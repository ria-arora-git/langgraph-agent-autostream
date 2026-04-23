import json
import os
from pathlib import Path


_KB_PATH = Path(__file__).parent.parent / "data" / "knowledge_base.json"

_kb_cache: dict | None = None


def _load_kb() -> dict:
    global _kb_cache
    if _kb_cache is None:
        with open(_KB_PATH, "r", encoding="utf-8") as f:
            _kb_cache = json.load(f)
    return _kb_cache


def get_full_context() -> str:
    kb = _load_kb()

    lines = []

    c = kb["company"]
    lines.append(f"## Company: {c['name']}")
    lines.append(f"Tagline: {c['tagline']}")
    lines.append(c["description"])
    lines.append("")

    lines.append("## Pricing Plans")
    for plan in kb["pricing"]["plans"]:
        lines.append(f"### {plan['name']} — ${plan['price_monthly']}/month")
        for feat in plan["features"]:
            lines.append(f"  - {feat}")
        lines.append(f"  Best for: {plan['ideal_for']}")
        lines.append("")

    lines.append("## Policies")
    p = kb["policies"]
    lines.append(f"- Refund Policy: {p['refund_policy']}")
    lines.append(f"- Support: {p['support']}")
    lines.append(f"- Cancellation: {p['cancellation']}")
    lines.append(f"- Free Trial: {p['free_trial']}")
    lines.append("")

    lines.append("## FAQs")
    for faq in kb["faqs"]:
        lines.append(f"Q: {faq['question']}")
        lines.append(f"A: {faq['answer']}")
        lines.append("")

    return "\n".join(lines)


def retrieve(query: str) -> str:
    kb = _load_kb()
    query_lower = query.lower()

    snippets = []

    c = kb["company"]
    snippets.append(f"{c['name']}: {c['description']}")

    price_keywords = {
        "price", "pricing", "plan", "cost", "dollar", "$", "cheap",
        "expensive", "subscription", "pay", "basic", "pro", "4k",
        "unlimited", "resolution", "video", "caption"
    }

    if price_keywords & set(query_lower.split()) or any(k in query_lower for k in price_keywords):
        for plan in kb["pricing"]["plans"]:
            feat_str = ", ".join(plan["features"])
            snippets.append(
                f"{plan['name']}: ${plan['price_monthly']}/month — {feat_str}"
            )

    policy_keywords = {
        "refund", "cancel", "return", "support", "trial", "free",
        "money", "back", "help", "24/7", "upgrade"
    }

    if policy_keywords & set(query_lower.split()) or any(k in query_lower for k in policy_keywords):
        p = kb["policies"]
        snippets.append(f"Refund policy: {p['refund_policy']}")
        snippets.append(f"Support: {p['support']}")
        snippets.append(f"Free trial: {p['free_trial']}")

    for faq in kb["faqs"]:
        faq_words = set(faq["question"].lower().split())
        query_words = set(query_lower.split())
        if len(faq_words & query_words) >= 2:
            snippets.append(f"Q: {faq['question']} | A: {faq['answer']}")

    return "\n".join(snippets) if snippets else get_full_context()