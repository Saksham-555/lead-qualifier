import logging
import time
import uuid
from functools import lru_cache

import anthropic
from fastapi import Depends, FastAPI

from config import load_settings
from qualifier import qualify_lead
from schema import Lead, LeadResponse
from storage import JsonlSink, ResultSink

logger = logging.getLogger("lead_qualifier")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Lead Qualifier")


@lru_cache
def get_settings():
    return load_settings()


@lru_cache
def get_client():
    s = get_settings()
    return anthropic.Anthropic(api_key=s.api_key, base_url=s.base_url, timeout=s.timeout_seconds)


@lru_cache
def get_sink() -> ResultSink:
    return JsonlSink()


def get_model() -> str:
    return get_settings().model


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/leads", response_model=LeadResponse)
def post_lead(
    lead: Lead,
    client=Depends(get_client),
    sink: ResultSink = Depends(get_sink),
    model: str = Depends(get_model),
):
    lead_id = str(uuid.uuid4())
    t0 = time.perf_counter()
    outcome = qualify_lead(lead, client, model)
    resp = LeadResponse(
        lead_id=lead_id,
        status=outcome.status,
        attempts=outcome.attempts,
        result=outcome.result,
        error=outcome.error,
    )
    try:
        sink.save({"lead_id": lead_id, "lead": lead.model_dump(), "response": resp.model_dump()})
    except Exception:
        logger.exception("save failed lead_id=%s", lead_id)
    logger.info(
        "lead_id=%s status=%s attempts=%d latency_ms=%d",
        lead_id, resp.status, resp.attempts, (time.perf_counter() - t0) * 1000,
    )
    return resp
