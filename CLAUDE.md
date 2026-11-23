# Project rules
- Python 3.10+. Dependencies are limited to those listed in SPEC.md.
- Create a venv at .venv. Run tools as .venv\Scripts\python -m pytest (no activation needed).
- Every change needs tests (pytest). Tests must never call the real API: mock the client.
- Keep changes small and focused on SPEC.md. Do not add features that are not in it.
- Append to DEVLOG.md: what you changed and why, one short entry per step.
- Never commit secrets. Never print or log API keys.
- Be concise: no long explanations, and do not re-read files you just wrote.
