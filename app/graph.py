"""LangGraph state machine: the heart of the agent."""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from .intent import classify_intent
from .state import AgentState, LeadStage


def build_graph(crm):
    """Build the conversation graph.

    crm: CRMStore adapter (InMemoryCRM or PostgresCRM)
    """
    def enrich_context(state: AgentState) -> dict:
        # history is already on the lead; stage transitions happen at the end
        return {}

    def update_crm(state: AgentState) -> dict:
        lead = state["lead"]
        crm.append_history(lead["id"], "assistant", state["reply"])
        if state["escalate"]:
            crm.set_stage(lead["id"], LeadStage.HANDOFF)
        elif state["intent"] == "sales_interest":
            crm.set_stage(lead["id"], LeadStage.QUALIFYING)
        elif state["intent"] == "opt_out":
            crm.set_stage(lead["id"], LeadStage.OPTED_OUT)
        return {}

    def route_after_intent(state: AgentState) -> str:
        return "respond"

    g = StateGraph(AgentState)

    g.add_node("classify_intent", classify_intent)
    g.add_node("enrich_context", enrich_context)
    g.add_node("generate_reply", generate_reply)
    g.add_node("update_crm", update_crm)

    g.set_entry_point("classify_intent")
    g.add_edge("classify_intent", "enrich_context")
    g.add_edge("enrich_context", "generate_reply")
    g.add_conditional_edges("generate_reply", route_after_intent, {"respond": "update_crm"})
    g.add_edge("update_crm", END)

    return g.compile()


def process_message(crm, phone: str, message: str, name: str | None = None) -> dict:
    """Full turn: get-or-create lead, run the graph, persist, return reply."""
    lead = crm.get_by_phone(phone)
    if lead is None:
        lead = Lead(
            id="", phone=phone, name=name or "", stage=LeadStage.NEW,
            history=[], tags=[],
        )
        lead = crm.upsert(lead)

    crm.append_history(lead["id"], "user", message)
    lead = crm.get_by_phone(phone)

    graph = build_graph(crm)
    result: AgentState = graph.invoke({
        "lead": lead,
        "inbound_message": message,
        "intent": "",
        "reply": "",
        "confidence": 0.0,
        "escalate": False,
        "tool_results": [],
    })

    return {"reply": result["reply"], "escalate": result["escalate"], "intent": result["intent"]}
