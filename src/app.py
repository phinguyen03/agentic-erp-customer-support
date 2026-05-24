import asyncio
import json
import logging
from uuid import uuid4
from pydantic import BaseModel, Field
from typing import Annotated

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from langchain_core.messages import AIMessage, HumanMessage

from src.message.user_message import Context
from src.mock_data import MOCK_CUSTOMERS
from src.utils.logger import set_log_context
from src.utils.thread_store import load_thread, save_thread
from src.workflow.base import graph

app = FastAPI(title="Agentic ERP Customer Support")


class ChatRequest(BaseModel):
    message: Annotated[str, Field(description="User message.")]
    email: Annotated[str, Field(description="Requester's email credential.")]


class ChatResponse(BaseModel):
    message: Annotated[str, Field(description="AI response")]


def _identify_user(email_input: str) -> tuple[str, str] | None:
    """Validate credential against user database. Future: replace with JWT validation."""
    customer = next((c for c in MOCK_CUSTOMERS if c["email"] == email_input), None)
    if not customer:
        return None
    return customer["user_id"], customer["name"]


async def chat(message: str, email_input: str) -> dict:
    user_info = _identify_user(email_input)
    if not user_info:
        return {"messages": [AIMessage(content="Your information is not in our system.")]}

    user_id, user_name = user_info
    logging.warning(f"user id: {user_id}, user name: {user_name}")

    existing = load_thread(user_id)
    thread_id = existing or str(uuid4())
    if not existing:
        save_thread(user_id, thread_id)

    set_log_context(thread_id=thread_id, user_id=user_id)
    context = Context(user_id=user_id, user_name=user_name)

    result = await graph.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        context=context,
        config={"configurable": {"thread_id": thread_id}},
    )

    return result


@app.get("/api/v1/health")
async def health():
    return {"status": "200"}


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest) -> ChatResponse:
    result = await chat(message=req.message, email_input=req.email)
    ai_message = result["messages"][-1].content
    return ChatResponse(message=ai_message)


@app.post("/api/v1/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    user_info = _identify_user(req.email)
    if not user_info:
        async def err():
            yield f"data: {json.dumps({'type': 'message', 'content': 'Your information is not in our system.'})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(content=err(), media_type="text/event-stream")

    user_id, user_name = user_info
    existing = load_thread(user_id)
    thread_id = existing or str(uuid4())
    if not existing:
        save_thread(user_id, thread_id)

    set_log_context(thread_id=thread_id, user_id=user_id)
    context = Context(user_id=user_id, user_name=user_name)

    async def generate():
        async for chunk in graph.astream(
            {"messages": [HumanMessage(content=req.message)]},
            context=context,
            config={"configurable": {"thread_id": thread_id}},
        ):
            for update in chunk.values():
                if "messages" in update:
                    for msg in update["messages"]:
                        if isinstance(msg, AIMessage) and msg.content:
                            yield f"data: {json.dumps({'type': 'message', 'content': msg.content})}\n\n"
                if "data" in update:
                    yield f"data: {json.dumps({'type': 'data', 'payload': update['data']})}\n\n"
                       
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(content=generate(), media_type="text/event-stream")


async def main():
    email_input = input("Email: ").strip()
    if not next((c for c in MOCK_CUSTOMERS if c["email"] == email_input), None):
        logging.warning("User not found: %s", email_input)
        return
    while True:
        logging.warning("START")
        message = input().encode("utf-8", errors="ignore").decode("utf-8")
        response = await chat(message=message, email_input=email_input)
        ai_response = response["messages"][-1].content
        logging.warning("Assistant: %s", ai_response)


if __name__ == "__main__":
    asyncio.run(main())
