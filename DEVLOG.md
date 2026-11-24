# DEVLOG

- Setup: repo created with SPEC.md, CLAUDE.md, reviewer subagent and review.ps1.
- Build: added config, schema, prompts, qualifier (one retry with validation error, API errors -> failed), storage (ResultSink + JsonlSink), FastAPI app, requirements.txt, .env.example. Why: implement SPEC.md core.
- Tests: tests/test_app.py covers the 7 spec cases with a fake client (no network). Created .venv, installed deps; 8 tests pass.
- Evals: added evals/leads.jsonl (10 labelled leads: 3 hot, 4 warm, 3 cold; includes no-email, vague, spam, prompt-injection) and evals/run_evals.py (real API, prints expected vs got and accuracy). Added tests/test_evals.py to check the data file offline. Evals not run yet. Why: SPEC.md Evals section.
- Review fix 1: prompts.py now puts name, source and message all inside the delimiters; START/END markers are replaced with "[removed]" in all three. System prompt updated. Why: name/source were outside the untrusted block and a message could close it early.
- Review fix 2: max_retries=0 on the Anthropic client in main.py, run_evals.py and the qualify_lead default client. Why: SDK default of 2 retries hid up to ~3 min latency; spec retries only invalid output.
- Review fix 3: app lifespan calls get_settings() so a missing LQ_API_KEY stops startup; qualify_lead catches any unexpected Exception (client call and parse) and returns failed so the lead is still saved.
- Review fix 6: qualify_lead(lead, client=None, model=None); with no client it builds one from config, matching the spec's qualify_lead(lead).
- Review fix 8: added pytest.ini (pythonpath=., testpaths=tests) so imports work however pytest is launched.
- Review fix 10: retry test now asserts the real validation error text ("no JSON object found") is in the second prompt.
- Review fix 11: run_evals.py catches per-case errors, handles zero cases, and exits 1 if any case failed/errored. Evals not run.
- Review finding 5 tests (tests/test_more.py): 429/500/503 -> failed, one call, saved; unexpected error saved; client max_retries==0; JsonlSink; config defaults/required/key not in repr; startup fails without key; save failure still 200; logs have no personal data or key; prompt delimiter tests.
- Skipped: findings 4, 7, 9, 12 (not requested). All 7 requested findings were verified in code and held up.
