# Agentic ERP Customer Support

An agentic AI workflow for automating e-commerce customer support tasks such as product returns, refunds, exchanges, and human handoff.

This project is built to practice AI system design and workflow automation in an ERP-like business domain. Instead of acting like a simple chatbot, the system uses structured extraction, business-rule checks, tool calls, and conversation state to handle customer requests step by step.

## Current Features

- Intent classification for customer support requests
- Email-based customer identification
- Structured extraction of return request details
- Conversation state management with LangGraph threads
- Return request workflow:
  - asks for order ID when missing
  - looks up order information
  - checks order date
  - checks reported product condition
- Mock ERP data for local development

## Planned Features

- Refund approval workflow
- Auto-approval for eligible refunds under a defined threshold
- Manager approval routing for higher-value refunds
- Exchange workflow
- Human escalation for emotional, unclear, or unsupported cases
- Audit logging for workflow decisions
- Streaming responses
- PostgreSQL persistence
- Policy retrieval with RAG

## Tech Stack

- Python
- FastAPI
- LangGraph
- Pydantic
- OpenAI-compatible LLM API
- uv

## Project Goal

The goal of this project is to explore how agentic AI systems can be designed for real business workflows, where the AI must:

- understand the customer request
- collect missing information
- call tools to retrieve business data
- apply deterministic business rules
- maintain conversation state
- decide when to continue automation or escalate to a human

## Current Status

The AI architecture has been designed, and the initial return request flow is implemented.

Example supported flow:

1. Customer says: “I want to return my order.”
2. AI asks for the order ID if it is missing.
3. AI checks the order date and product condition before continuing the workflow.

## Notes

This is a learning and portfolio project using mock ERP data, not a production ERP integration.