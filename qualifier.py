import json
from dataclasses import dataclass
from typing import Optional

import anthropic
from pydantic import ValidationError

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


def qualify_lead(lead: Lead, client, model: str = "claude-haiku-5-5") -> Outcome:
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
        try:
            return Outcome("ok", attempt, result=_parse(text))
        except (ValueError, ValidationError) as e:  # JSONDecodeError is a ValueError
            error = str(e)[:500]
    return Outcome("failed", MAX_ATTEMPTS, error="invalid model output after retry")
