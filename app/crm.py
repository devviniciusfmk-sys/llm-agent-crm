"""CRM persistence port with an in-memory adapter (swap for Postgres in prod)."""
from __future__ import annotations

import threading
import uuid

from .state import Lead, LeadStage


class CRMStore:
    """Port. Production impl backs this with PostgreSQL + row locking."""

    def upsert(self, lead: Lead) -> Lead: ...
    def get_by_phone(self, phone: str) -> Lead | None: ...
    def append_history(self, lead_id: str, role: str, content: str) -> None: ...
    def set_stage(self, lead_id: str, stage: LeadStage) -> None: ...
    def count_handoffs(self) -> int: ...


class InMemoryCRM(CRMStore):
    def __init__(self) -> None:
        self._leads: dict[str, Lead] = {}
        self._lock = threading.Lock()

    def upsert(self, lead: Lead) -> Lead:
        with self._lock:
            if not lead.get("id"):
                lead["id"] = uuid.uuid4().hex[:12]
            self._leads[lead["id"]] = lead
            return lead

    def get_by_phone(self, phone: str) -> Lead | None:
        with self._lock:
            return next((l for l in self._leads.values() if l["phone"] == phone), None)

    def append_history(self, lead_id: str, role: str, content: str) -> None:
        with self._lock:
            self._leads[lead_id]["history"].append({"role": role, "content": content})

    def set_stage(self, lead_id: str, stage: LeadStage) -> None:
        with self._lock:
            self._leads[lead_id]["stage"] = stage

    def count_handoffs(self) -> int:
        with self._lock:
            return sum(1 for l in self._leads.values() if l["stage"] == LeadStage.HANDOFF)
