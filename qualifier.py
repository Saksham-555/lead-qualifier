import json
from dataclasses import dataclass
from typing import Optional

import anthropic
from pydantic import ValidationError

from config import load_settings
from prompts import SYSTEM_PROMPT, build_user_prompt
from schema import Lead, QualifyResult

MAX_ATTEMPTS = 2


@dataclass
class Outcome:
    status: str
    attempts: int
    result: Optional[QualifyResult] = None
    error: Optional[str] = None


def _parse(text: str) -> QualifyResult:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end < start:
        raise ValueError("no JSON object found")
    return QualifyResult.model_validate(json.loads(text[start : end + 1]))


def qualify_lead(lead: Lead, client=None, model: Optional[str] = None) -> Outcome:
    """Spec form is qualify_lead(lead); client/model can be injected (tests, evals, app)."""
    if client is None or model is None:
        settings = load_settings()
        model = model or settings.model
        client = client or anthropic.Anthropic(
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout=settings.timeout_seconds,
            max_retries=0,
        )
    error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": build_user_prompt(lead, error)}],
            )
            text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        except anthropic.APIError as e:
            return Outcome("failed", attempt, error=f"API error: {type(e).__name__}")
        except Exception as e:  # never let an unexpected error skip saving the lead
            return Outcome("failed", attempt, error=f"unexpected error: {type(e).__name__}")
        try:
            return Outcome("ok", attempt, result=_parse(text))
        except (ValueError, ValidationError) as e:  # JSONDecodeError is a ValueError
            error = str(e)[:500]
        except Exception as e:
            return Outcome("failed", attempt, error=f"unexpected error: {type(e).__name__}")
    return Outcome("failed", MAX_ATTEMPTS, error="invalid model output after retry")
