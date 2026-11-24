# Lead Qualifier

A small web service. You POST a lead as JSON. A Claude model scores the lead's intent (hot, warm or cold) and pulls out key details. It also drafts a follow-up SMS. The result is checked against a schema and saved to a local file. If anything goes wrong, the service returns a `failed` status instead of crashing.

## Run it

Python 3.10+ is required.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`:

| Variable | Meaning | Default |
|---|---|---|
| `LQ_API_KEY` | API key (required) | none |
| `LQ_BASE_URL` | Custom endpoint for an Anthropic-compatible API (optional) | SDK default |
| `LQ_MODEL` | Model name | `claude-haiku-5-5` |
| `LQ_TIMEOUT_SECONDS` | Request timeout | `30` |

Start the server:

```powershell
.venv\Scripts\python -m uvicorn main:app --port 8000
```

Try it:

```bash
curl -X POST http://localhost:8000/leads \
  -H "Content-Type: application/json" \
  -d '{"name":"Dana","message":"We need a new roof by March, budget about $15k, in Austin.","source":"website","email":"dana@example.com"}'
```

The response has `lead_id`, `status` (`ok` or `failed`), `attempts`, `result` (null if failed) and `error` (null if ok). `GET /health` returns `{"status":"ok"}`.

Every lead and its result is appended to `results.jsonl`.

Run the tests (no network, the client is mocked):

```powershell
.venv\Scripts\python -m pytest
```

Run the evals (these call the real API and cost money):

```powershell
.venv\Scripts\python evals\run_evals.py
```

## Design choices

- **Validated structured output.** The model is asked for JSON only. The reply is parsed and checked with pydantic. Bad output never reaches the caller.
- **One retry, with the error fed back.** If the JSON or schema is invalid, the prompt is sent again with the validation error added, so the model can fix its mistake. After a second failure the lead is marked `failed`.
- **`failed` status, not a crash.** Timeouts, 429s, 5xx errors and any other unexpected error give `status: "failed"` and a short message. The lead is still saved.
- **`max_retries=0` on the client.** The SDK retries by default, which can hide minutes of latency. Setting it to 0 means the only retry is the explicit one above.
- **Untrusted lead text in delimiters.** Name, source and message are wrapped in clear start/end markers. The prompt tells the model never to follow instructions inside them. Any marker text inside the lead is replaced with `[removed]`, so a message cannot close the block early.
- **A sink interface.** `ResultSink` is a small interface, and `JsonlSink` is the only implementation. Saving somewhere else later means adding one class.
- **Safe logging.** Each request logs `lead_id`, `status`, `attempts` and `latency_ms`, with no personal data and no API key.

## How failures are handled

| Situation | What happens |
|---|---|
| Invalid JSON or schema | One retry with the error added. If it fails again, `failed`. |
| API timeout, 429, 5xx | `failed` with a short error. No retry. |
| Any other unexpected error | `failed`. The lead is still saved. |
| Saving to the file fails | The request still returns 200. |
| Message empty or over 2000 characters | Rejected with 422. |
| `LQ_API_KEY` missing | The service refuses to start. |

## Evals

`evals/leads.jsonl` holds 10 hand-labelled leads (3 hot, 4 warm, 3 cold). They include edge cases: no email, a vague message, spam and a message that tries to override the instructions.

| Model | Endpoint | Correct |
|---|---|---|
| `kimi-k3.1-pro` | Anthropic-compatible endpoint set by `LQ_BASE_URL` | 10/10 |

This is a small smoke test, not a benchmark. Ten leads, labelled by hand, says little about real-world accuracy.

Moving to Claude means changing `LQ_BASE_URL` and `LQ_MODEL` in `.env`. I have not run the evals against Claude yet.

## Known limitations

- `logger.exception` may log record contents when an error occurs.
- There are no tests for an empty message or one of exactly 2000 characters.
- The `reason` field has no length cap.
- No authentication on the endpoints.
- Results go to a local JSONL file only.
