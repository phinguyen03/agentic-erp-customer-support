# Agentic ERP Support Frontend

Modern React frontend for the `Agentic ERP Customer Support` backend.

This app provides a polished customer support chat interface for:

- Returns
- Refunds
- Exchanges
- Approval status checks
- Human escalation / unsupported request handling

It is intentionally isolated inside `frontend/` and does not mix any UI code into the FastAPI backend under `src/`.

## Stack

- Vite
- React
- TypeScript
- Tailwind CSS
- shadcn-style UI components
- Zustand
- lucide-react

## Backend Contract

The frontend expects the existing FastAPI backend to expose:

- `GET /api/v1/health`
- `POST /api/v1/chat`
- `POST /api/v1/chat/stream`

Default backend base URL:

```env
VITE_API_BASE_URL=http://localhost:8000
```

The streaming endpoint uses `POST` and returns Server-Sent Events, so this frontend does **not** use `EventSource`. It uses `fetch()` with `ReadableStream` and manually parses SSE chunks.

Supported stream payloads:

```txt
data: {"type": "message", "content": "AI text here"}

data: {"type": "data", "payload": {...}}

data: {"type": "done"}

data: [DONE]
```

## Features

- Email gate before entering chat
- Email persisted locally with Zustand
- Responsive SaaS-style layout
- Desktop sidebar and right info panel
- Mobile-first single-column behavior
- Streaming assistant responses over `POST /api/v1/chat/stream`
- Fallback non-streaming request support via `POST /api/v1/chat`
- Structured backend payload rendering
- Retry flow for failed assistant responses
- Local conversation clearing

## Project Structure

```txt
frontend/
  src/
    app/
      App.tsx
    components/
      auth/
        EmailGate.tsx
      chat/
        ChatWindow.tsx
        ChatInput.tsx
        EmptyState.tsx
        MessageBubble.tsx
        StructuredDataCard.tsx
        TypingIndicator.tsx
      layout/
        AppShell.tsx
        Sidebar.tsx
        RightInfoPanel.tsx
      ui/
        badge.tsx
        button.tsx
        card.tsx
        input.tsx
        scroll-area.tsx
        separator.tsx
        textarea.tsx
    hooks/
      useChatStream.ts
    lib/
      api.ts
      sse.ts
      utils.ts
    stores/
      chatStore.ts
    types/
      chat.ts
    index.css
    main.tsx
```

## Getting Started

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Configure environment

Create a local env file if needed:

```bash
cp .env.example .env
```

Or set:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start the backend

From the repository root:

```bash
uv run uvicorn src.app:app --reload
```

### 4. Start the frontend

```bash
cd frontend
npm run dev
```

### 5. Open the app

By default Vite runs on:

```txt
http://localhost:5173
```

## Available Scripts

```bash
npm run dev
```

Starts the Vite development server.

```bash
npm run typecheck
```

Runs TypeScript checks without emitting files.

```bash
npm run build
```

Builds the production bundle into `frontend/dist`.

```bash
npm run preview
```

Serves the production build locally.

## State Management

Zustand store lives in:

- `src/stores/chatStore.ts`

Tracked state includes:

- `email`
- `messages`
- `isStreaming`
- `error`

Email is persisted locally. Recent messages are also persisted for convenience, while the backend remains the source of truth for workflow memory and thread continuity.

## Streaming Implementation

Core files:

- `src/lib/api.ts`
- `src/lib/sse.ts`
- `src/hooks/useChatStream.ts`

Implementation details:

- Uses `fetch()` for `POST /api/v1/chat/stream`
- Reads `response.body.getReader()`
- Decodes chunks with `TextDecoder`
- Buffers partial chunks safely
- Splits SSE blocks by blank lines
- Extracts `data:` lines only
- Supports both JSON envelopes and `[DONE]`
- Handles non-200 responses and interrupted streams
- Falls back to `POST /api/v1/chat` when appropriate

The parser is designed to tolerate both:

- token-like incremental updates
- full-message-per-node workflow updates

## Structured Payload Rendering

Structured backend events are rendered with:

- `src/components/chat/StructuredDataCard.tsx`

Behavior:

- Approval-like payloads render as a dedicated approval card
- Unknown payloads render as collapsible JSON preview cards

Known approval-oriented fields:

- `request_id`
- `order_id`
- `action`
- `amount`
- `status`

## UI Notes

The interface is styled to feel closer to a production SaaS support workspace than a demo:

- soft neutral surfaces
- rounded cards
- subtle shadows
- responsive panel layout
- accessible forms and buttons
- mobile-friendly chat flow

## Testing Notes

Frontend validation completed with:

```bash
npm run typecheck
npm run build
```

If you want full manual verification, start the FastAPI backend and test:

- login with a customer email
- send a return/refund/exchange request
- verify streamed assistant responses
- verify structured approval payload rendering
- verify retry behavior on failures

## Example Test Prompts

- `I want to return my order`
- `I want a refund for ord_1001`
- `What is the status of my approval?`
- `I want to exchange an item`

## Notes

- This frontend does not enforce business rules in the browser.
- The backend remains responsible for workflow logic and approval decisions.
- `node_modules/` and `dist/` are intentionally ignored.
