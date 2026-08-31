from app.intent import classify_intent


def make_state(msg: str) -> dict:
    return {"lead": {"id": "1", "phone": "x", "name": "Ana", "stage": "new", "history": [], "tags": []},
            "inbound_message": msg, "intent": "", "reply": "", "confidence": 0.0,
            "escalate": False, "tool_results": []}


def test_opt_out_has_top_priority():
    r = classify_intent(make_state("quero o preco e depois quero SAIR"))
    assert r["intent"] == "opt_out"
    assert r["confidence"] >= 0.9


def test_human_request_detected():
    r = classify_intent(make_state("quero falar com um atendente"))
    assert r["intent"] == "human_handoff"


def test_buy_signal_detected():
    r = classify_intent(make_state("quanto custa o plano?"))
    assert r["intent"] == "sales_interest"


def test_support_signal_detected():
    r = classify_intent(make_state("o sistema nao funciona, da erro"))
    assert r["intent"] == "support"


def test_unclear_falls_back_low_confidence():
    r = classify_intent(make_state("oi"))
    assert r["intent"] == "unclear"
    assert r["confidence"] < 0.5
