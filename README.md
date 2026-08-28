# LLM Agent CRM

Reference implementation of a LangGraph agent that orchestrates multi-step CRM conversations over the WhatsApp Business API.

Note: this is a from-scratch reference build reproducing the architecture of a production system I built and operate (20,000+ leads/month). Proprietary business logic, customer data and infra config are not included here for confidentiality reasons -- this repo demonstrates the agent design, state machine and integration pattern.

## Architecture

WhatsApp Business API to Webhook (FastAPI) to LangGraph StateGraph to CRM store.

Graph nodes: classify_intent routes the inbound message (new_lead, follow_up, support, opt_out); enrich_context pulls lead history from the CRM; generate_response drafts an LLM reply constrained by a response policy; human_handoff escalates to a rep on low confidence or explicit request; update_crm persists the interaction and advances the lead stage.

## Stack

Python, LangGraph, LangChain, FastAPI, PostgreSQL, WhatsApp Business API.

## Run locally

pip install -r requirements.txt

export OPENAI_API_KEY=sk-your-key

uvicorn app:app --reload

## Status

Agent graph and webhook are implemented and runnable end to end with an in-memory CRM. Swap InMemoryCRM in app.py for a Postgres-backed store to go to production.
