import json
from collections import Counter
from pathlib import Path

from schema import Lead

LEADS = Path(__file__).resolve().parent.parent / "evals" / "leads.jsonl"


def test_eval_leads_file_is_valid_and_balanced():
    cases = [json.loads(line) for line in LEADS.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert Counter(c["expected"] for c in cases) == {"hot": 3, "warm": 4, "cold": 3}
    for c in cases:
        Lead(**c["lead"])
    assert any(not c["lead"].get("email") for c in cases)
