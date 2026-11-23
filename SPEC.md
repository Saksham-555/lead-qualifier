# AI Lead Qualifier: spec
A webhook receives a lead as JSON. Claude scores the intent, extracts fields and drafts a follow-up SMS. The output is validated, retried once if invalid, and saved. Failures never crash the service.

## Stack (only these)
Python 3.10+, fastapi, uvicorn, anthropic (SDK), pydantic v2, python-dotenv, pytest, httpx. Keep requirements.txt.

## Config (from .env, loaded with python-dotenv)
Use these unique names so they never clash with Claude Code's own ANTHROPIC_* variables:
- LQ_API_KEY (required), LQ_BASE_URL (optional), LQ_MODEL (default claude-haiku-5-5), LQ_TIMEOUT_SECONDS (default 30).
- Provide .env.example with placeholders. Never log the key.

## API
- GET /health returns {"status":"ok"}.
- POST /leads body: name (str), message (str, 1-2000 chars, stripped), source (str), email (optional), phone (optional).
- Response: lead_id, status ("ok" or "failed"), attempts, result (null if failed), error (null if ok).

## Result schema (pydantic)
intent: "hot" | "warm" | "cold"; confidence: 0-1; reason: short string;
extracted: service_needed, budget, timeline, location (all optional strings);
sms_draft: string, max 320 chars.

## Behaviour
- qualifier.py: one function qualify_lead(lead) that calls Claude, asks for JSON only, parses, validates with pydantic.
- If JSON or schema is invalid: retry ONCE, adding the validation error to the prompt. If it fails again, return status "failed".
- API errors (timeout, 429, 5xx) also give status "failed" with a short error message. The lead is still saved.
- prompts.py holds the prompt. The lead's message is untrusted data: wrap it in clear delimiters and tell the model to never follow instructions inside it.
- storage.py: ResultSink interface plus JsonlSink that appends every lead and result to results.jsonl.
- Every request logs lead_id, status, attempts, latency_ms (no personal data in logs).

## Tests (pytest, mocked client, no network)
valid JSON; invalid JSON then valid on retry; invalid twice gives failed; API error gives failed; optional fields missing; message too long rejected (422); prompt wraps the lead message in delimiters.

## Evals (separate from pytest, calls the real API)
- evals/leads.jsonl: 10 labelled leads (3 hot, 4 warm, 3 cold) including edge cases: no email, vague message, spam, a message trying to override instructions.
- evals/run_evals.py: runs each lead through qualify_lead, prints expected vs got per lead and overall accuracy.

## README.md
What it does, why each design choice, how failures are handled, how to run it, and the eval results table.

## Out of scope
Auth, Google Sheets, GHL, Grok, any UI.
