# app/llm/confidence.py
def compute_confidence(action: str) -> float:
    if action.startswith("get_"):
        return 0.95
    if action.startswith("update_"):
        return 0.85
    if "refund" in action or "cancel" in action:
        return 0.7
    return 0.5
