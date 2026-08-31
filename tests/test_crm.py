from app.crm import InMemoryCRM
from app.state import Lead, LeadStage


def make_lead() -> Lead:
    return Lead(id="", phone="+551199", name="Ana", stage=LeadStage.NEW, history=[], tags=[])


def test_upsert_assigns_id_once():
    crm = InMemoryCRM()
    lead = crm.upsert(make_lead())
    first_id = lead["id"]
    assert first_id
    crm.upsert(lead)
    assert lead["id"] == first_id  # not regenerated


def test_get_by_phone():
    crm = InMemoryCRM()
    crm.upsert(make_lead())
    assert crm.get_by_phone("+551199") is not None
    assert crm.get_by_phone("+550000") is None


def test_stage_and_handoff_count():
    crm = InMemoryCRM()
    lead = crm.upsert(make_lead())
    crm.set_stage(lead["id"], LeadStage.HANDOFF)
    assert crm.count_handoffs() == 1


def test_history_appends():
    crm = InMemoryCRM()
    lead = crm.upsert(make_lead())
    crm.append_history(lead["id"], "user", "hello")
    crm.append_history(lead["id"], "assistant", "hi!")
    assert len(crm.get_by_phone("+551199")["history"]) == 2
