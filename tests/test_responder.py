from app.responder import generate_reply


def make_state(intent: str, confidence: float) -> dict:
    return {"lead": {"id": "1", "phone": "x", "name": "Ana", "stage": "new", "history": [], "tags": []},
            "inbound_message": "m", "intent": intent, "reply": "", "confidence": confidence,
            "escalate": False, "tool_results": []}


def test_human_handoff_escalates():
    r = generate_reply(make_state("human_handoff", 0.95))
    assert r["escalate"] is True
    assert "specialist" in r["reply"].lower()


def test_opt_out_does_not_escalate():
    r = generate_reply(make_state("opt_out", 0.99))
    assert r["escalate"] is False


def test_low_confidence_escalates_for_review():
    r = generate_reply(make_state("unclear", 0.40))
    assert r["escalate"] is True


def test_sales_reply_mentions_demo():
    r = generate_reply(make_state("sales_interest", 0.85))
    assert r["escalate"] is False
    assert "demo" in r["reply"].lower()
