"""Intent classification node — deterministic rules first, LLM fallback."""
from __future__ import annotations

import re

from .state import AgentState

OPT_OUT = re.compile(r"\b(parar|sair|descadastrar|stop|unsubscribe|remover)\b", re.IGNORECASE)
HUMAN_REQUEST = re.compile(
    r"\b(falar com (um|uma) (atendente|humano|pessoa|vendedor)|atendente|"
    r"human|agent|representative)\b",
    re.IGNORECASE,
)
BUY_SIGNAL = re.compile(
    r"\b(pre[\u00e7]o|valor|quanto custa|comprar|assinar|contratar|planos?|"
    r"demonstra[\u00e7][\u00e3]o|demo)\b",
    re.IGNORECASE,
)
SUPPORT_SIGNAL = re.compile(
    r"\b(problema|erro|n[\u00e3]o funciona|bug|suporte|ajuda t[\u00e9]cnica|d[\u00fa]vida)\b",
    re.IGNORECASE,
)


def classify_intent(state: AgentState) -> dict:
    """Rule-based intent routing. Fast, free and deterministic — the LLM only
    handles messages the rules cannot confidently bucket."""
    msg = state["inbound_message"]

    if OPT_OUT.search(msg):
        return {"intent": "opt_out", "confidence": 0.99}
    if HUMAN_REQUEST.search(msg):
        return {"intent": "human_handoff", "confidence": 0.95}
    if SUPPORT_SIGNAL.search(msg):
        return {"intent": "support", "confidence": 0.85}
    if BUY_SIGNAL.search(msg):
        return {"intent": "sales_interest", "confidence": 0.85}

    return {"intent": "unclear", "confidence": 0.40}
