import asyncio
import logging
from uuid import uuid4

from fastapi import FastAPI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import Annotated

from src.message.user_message import Context
from src.utils.logger import set_log_context
from src.utils.thread_store import load_thread, save_thread
from src.workflow.base import graph

app = FastAPI(title="Agentic ERP Customer Support")


class ChatRequest(BaseModel):
    message: Annotated[str, Field(description="Customer message")]
    thread_id: Annotated[str | None, Field(description="Existing thread ID to continue conversation")] = None


class ChatResponse(BaseModel):
    message: Annotated[str, Field(description="AI response")]
    thread_id: Annotated[str, Field(description="Thread ID for next turn")]


async def chat(message: str, thread_id: str | None = None) -> dict:
    current_thread_id = thread_id or str(uuid4())

    result = await graph.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        context=Context(user_id=None, user_name=None),
        config={"configurable": {"thread_id": current_thread_id}},
    )

    user_id = (result.get("data") or {}).get("user_id")
    if not user_id:
        return {**result, "thread_id": current_thread_id}

    set_log_context(thread_id=current_thread_id, user_id=user_id)

    existing_thread_id = load_thread(user_id)
    if existing_thread_id:
        current_thread_id = existing_thread_id
    else:
        user_thread_id = str(uuid4())
        save_thread(user_id, user_thread_id)
        current_thread_id = user_thread_id

    return {**result, "thread_id": current_thread_id}


@app.get("/api/v1/health")
async def health():
    return {"status": "200"}


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest) -> ChatResponse:
    result = await chat(message=req.message, thread_id=req.thread_id)
    ai_message = result["messages"][-1].content
    return ChatResponse(message=ai_message, thread_id=result["thread_id"])


async def main():
    thread_id = None
    while True:
        logging.warning("START")
        message = input()
        response = await chat(message=message, thread_id=thread_id)
        thread_id = response.get("thread_id", thread_id)
        ai_response = response["messages"][-1].content
        logging.warning("Assistant: %s", ai_response)


if __name__ == "__main__":
    asyncio.run(main())
