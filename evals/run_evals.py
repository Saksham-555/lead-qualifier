"""Runs labelled leads through qualify_lead using the REAL API. Not part of pytest.

Usage: .venv\\Scripts\\python evals\\run_evals.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import anthropic  # noqa: E402

from config import load_settings  # noqa: E402
from qualifier import qualify_lead  # noqa: E402
from schema import Lead  # noqa: E402

LEADS_FILE = Path(__file__).resolve().parent / "leads.jsonl"


def load_cases(path: Path = LEADS_FILE) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> int:
    settings = load_settings()
    client = anthropic.Anthropic(
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=settings.timeout_seconds,
    )
    cases = load_cases()
    correct = 0
    for i, case in enumerate(cases, 1):
        lead = Lead(**case["lead"])
        outcome = qualify_lead(lead, client, settings.model)
        got = outcome.result.intent if outcome.result else f"FAILED ({outcome.error})"
        match = got == case["expected"]
        correct += match
        print(f"{i:2d}. {lead.name[:20]:<20} expected={case['expected']:<5} got={got:<5} {'OK' if match else 'MISS'}")
    print(f"\nAccuracy: {correct}/{len(cases)} = {correct / len(cases):.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
