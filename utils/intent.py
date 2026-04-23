import re


_GREETING_PATTERNS = re.compile(
    r"\b(hi|hello|hey|howdy|greetings|good\s*(morning|afternoon|evening)|what'?s\s*up|sup)\b",
    re.IGNORECASE
)

_HIGH_INTENT_PATTERNS = re.compile(
    r"\b(sign\s*up|sign\s*me\s*up|buy|purchase|subscribe|get\s*started|try|start|"
    r"i\s*want|i'?d\s*like|i\s*am\s*interested|interested\s*in|ready\s*to|"
    r"let'?s\s*do|go\s*ahead|sounds?\s*good|sign\s*me|register|join|enroll)\b",
    re.IGNORECASE
)

_PRODUCT_PATTERNS = re.compile(
    r"\b(price|pricing|plan|cost|feature|video|edit|caption|resolution|4k|720p|"
    r"refund|support|cancel|trial|free|basic|pro|how\s*much|tell\s*me|what\s*is|"
    r"explain|compare|differ|does\s*it|can\s*i|can\s*you)\b",
    re.IGNORECASE
)


def classify_intent(message: str) -> str:
    if _HIGH_INTENT_PATTERNS.search(message):
        return "high_intent_lead"

    if _GREETING_PATTERNS.search(message) and not _PRODUCT_PATTERNS.search(message):
        return "greeting"

    return "product_inquiry"


def is_collecting_lead_info(state: dict) -> bool:
    lead = state.get("lead_info", {})
    return state.get("collecting_lead", False) or bool(lead)


def lead_info_complete(state: dict) -> bool:
    lead = state.get("lead_info", {})
    return all([
        lead.get("name"),
        lead.get("email"),
        lead.get("platform"),
    ])