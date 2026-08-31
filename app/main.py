"""WhatsApp Business API webhook endpoint."""
from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from .crm import InMemoryCRM
from .graph import process_message

app = FastAPI(title="llm-agent-crm", version="0.1.0")
crm = InMemoryCRM()
WEBHOOK_SECRET = os.environ.get("WHATSAPP_WEBHOOK_SECRET", "dev-secret")


class InboundMessage(BaseModel):
    phone: str
    name: str | None = None
    message: str


@app.get("/webhook")
async def verify_webhook(request: Request):
    """Meta webhook verification handshake (hub.challenge)."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == WEBHOOK_SECRET:
        return int(challenge) if challenge and challenge.isdigit() else 0
    raise HTTPException(status_code=403, detail="verification failed")


@app.post("/webhook")
async def receive_message(msg: InboundMessage) -> dict:
    result = process_message(crm, phone=msg.phone, message=msg.message, name=msg.name)
    return {
        "reply": result["reply"],
        "intent": result["intent"],
        "escalated": result["escalate"],
    }


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "handoffs_pending": crm.count_handoffs()}
