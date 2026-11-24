# DEVLOG

- Setup: repo created with SPEC.md, CLAUDE.md, reviewer subagent and review.ps1.
- Build: added config, schema, prompts, qualifier (one retry with validation error, API errors -> failed), storage (ResultSink + JsonlSink), FastAPI app, requirements.txt, .env.example. Why: implement SPEC.md core.
- Tests: tests/test_app.py covers the 7 spec cases with a fake client (no network). Created .venv, installed deps; 8 tests pass.
- Evals: added evals/leads.jsonl (10 labelled leads: 3 hot, 4 warm, 3 cold; includes no-email, vague, spam, prompt-injection) and evals/run_evals.py (real API, prints expected vs got and accuracy). Added tests/test_evals.py to check the data file offline. Evals not run yet. Why: SPEC.md Evals section.
