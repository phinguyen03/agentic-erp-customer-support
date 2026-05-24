# Agentic ERP Customer Support

An agentic AI workflow for automating e-commerce customer support tasks: returns, refunds, exchanges, and manager approval routing.

Built to practice AI system design and workflow automation in an ERP-like business domain. Uses structured extraction, deterministic business-rule enforcement, and conversation state to handle customer requests step by step — not a simple chatbot.

## Architecture

```
Customer Message
  -> FastAPI /api/v1/chat  (or /api/v1/chat/stream for SSE)
  -> LangGraph Workflow
      classify_intent -> route
        |- handle_request  (return / refund / exchange / policy / human)
        |- check_approval_status
        +- escalate (out of scope)
  -> JSON approval store
  -> SSE streaming response
```

**Core design rule:** LLM handles language (intent extraction, response generation). Deterministic Python handles all business logic (policy checks, routing, financial decisions).

## Implemented Features

### Conversation & Auth
- Email-based customer identification at session start
- Conversation state persisted across turns via LangGraph `MemorySaver`
- Per-user thread tracking (JSON store)

### Intent Classification
- `return_request`, `refund_request`, `exchange_request`
- `policy_question`, `human_support_request`
- `approval_status`
- `out_of_scope` -> escalation response

### Return / Refund / Exchange Workflow
- Asks for order ID if missing
- Looks up order by customer ID
- Enforces 30-day return window
- Checks reported product condition
- **Auto-approves** requests under $50
- **Routes to manager approval** for orders >= $50 (idempotent -- no duplicate submissions)

### Manager Approval
- Approval requests stored in `src/data/pending_approvals.json`
- Customers can query approval status mid-conversation

### Streaming (SSE)
- `/api/v1/chat/stream` endpoint streams responses as each graph node completes
- Two event types:
  - `{"type": "message", "content": "..."}` -- AI text
  - `{"type": "data", "payload": {...}}` -- structured UI data (ready for future use)
- Terminated with `[DONE]` sentinel

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Uvicorn |
| Workflow | LangGraph (StateGraph + MemorySaver) |
| LLM | Anthropic Claude (`claude-sonnet-4-5`) via `messages.parse()` |
| Schema | Pydantic v2 |
| Runtime | Python 3.13, uv |
| Container | Docker |

## Running Locally

```bash
# install deps
uv sync

# add .env
ANTHROPIC_API_KEY=...
ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-4-5

# run CLI
uv run python -m src.app

# run API server
uv run uvicorn src.app:app --reload
```

## Docker

```bash
uv lock
docker build -t agentic-erp .
docker run -p 8000:8000 --env-file .env agentic-erp
```

API at `http://localhost:8000`

```json
POST /api/v1/chat
{ "email": "anna@example.com", "message": "I want to return my order" }

POST /api/v1/chat/stream
{ "email": "anna@example.com", "message": "I want to return my order" }
```

SSE stream example response:
```
data: {"type": "message", "content": "Your return for order ord_1001 has been approved."}

data: [DONE]
```

## Business Rules (Deterministic -- never delegated to LLM)

- Return window: 30 days from order date
- Auto-approve threshold: < $50
- Manager approval required: >= $50
- Condition check: item must be in good condition to be eligible
- Customers can only return their own orders

## Planned

- PostgreSQL persistence (replace JSON files)
- Exchange workflow handler
- Policy question handler (RAG)
- Human escalation node
- Audit logging
