"""Shared agent state and lead domain model."""
from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, TypedDict


class LeadStage(str, Enum):
    NEW = "new"
    QUALIFYING = "qualifying"
    FOLLOW_UP = "follow_up"
    HANDOFF = "handoff"
    WON = "won"
    LOST = "lost"
    OPTED_OUT = "opted_out"


class Lead(TypedDict):
    id: str
    phone: str
    name: str
    stage: LeadStage
    history: list[dict[str, str]]
    tags: list[str]


class AgentState(TypedDict):
    """State flowing through the LangGraph graph."""
    lead: Lead
    inbound_message: str
    intent: str
    reply: str
    confidence: float
    escalate: bool
    tool_results: Annotated[list[dict[str, Any]], lambda a, b: a + b]
