from app.crm import InMemoryCRM
from app.graph import process_message
from app.state import LeadStage


def test_full_turn_new_lead_sales():
    crm = InMemoryCRM()
    out = process_message(crm, phone="+551199", message="quanto custa?", name="Ana")
    assert out["intent"] == "sales_interest"
    assert out["escalate"] is False
    lead = crm.get_by_phone("+551199")
    assert lead["stage"] == LeadStage.QUALIFYING
    roles = [h["role"] for h in lead["history"]]
    assert roles == ["user", "assistant"]


def test_full_turn_opt_out():
    crm = InMemoryCRM()
    out = process_message(crm, phone="+552288", message="quero sair")
    assert out["intent"] == "opt_out"
    assert crm.get_by_phone("+552288")["stage"] == LeadStage.OPTED_OUT


def test_full_turn_handoff():
    crm = InMemoryCRM()
    out = process_message(crm, phone="+553377", message="falar com atendente")
    assert out["escalate"] is True
    assert crm.count_handoffs() == 1


def test_second_message_reuses_lead():
    crm = InMemoryCRM()
    process_message(crm, phone="+551199", message="quanto custa?", name="Ana")
    process_message(crm, phone="+551199", message="oi")
    lead = crm.get_by_phone("+551199")
    assert len(lead["history"]) == 4  # 2 turns x 2 messages
