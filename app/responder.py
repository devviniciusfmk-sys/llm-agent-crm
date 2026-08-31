"""Reply generation node — templated by intent, LLM slot pluggable."""
from __future__ import annotations

from .state import AgentState

TEMPLATES: dict[str, str] = {
    "sales_interest": (
        "Hi {name}! Great to hear you are interested. We have plans starting at "
        "R$97/month. Would you like a quick demo this week?"
    ),
    "support": (
        "Sorry to hear you are having trouble, {name}. I have logged your issue — "
        "a specialist will follow up shortly. Could you share more details?"
    ),
    "unclear": (
        "Thanks for reaching out, {name}! Could you tell me a bit more about "
        "what you are looking for?"
    ),
}


def generate_reply(state: AgentState) -> dict:
    """Intent-templated reply with confidence-based escalation.

    In production the unclear branch calls the LLM with a response policy
    (no promises, no pricing below floor, always one question). The template
    below demonstrates the deterministic path.
    """
    intent = state["intent"]
    confidence = state["confidence"]
    name = state["lead"].get("name") or "there"

    if intent == "human_handoff":
        return {"reply": "Of course! Transferring you to a specialist right now.", "escalate": True}

    if intent == "opt_out":
        return {"reply": "You have been unsubscribed. No further messages will be sent.", "escalate": False}

    if confidence < 0.5:
        return {"reply": TEMPLATES["unclear"].format(name=name), "escalate": True}

    return {"reply": TEMPLATES.get(intent, TEMPLATES["unclear"]).format(name=name), "escalate": False}
