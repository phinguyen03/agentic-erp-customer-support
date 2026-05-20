import logging
from uuid import uuid4

from langchain_core.messages import HumanMessage

from src.message.user_message import Context
from src.utils.logger import set_log_context
from src.utils.thread_store import load_thread, save_thread
from src.workflow.base import graph


async def chat(message: str, thread_id: str | None = None) -> dict:
    current_thread_id = thread_id or str(uuid4())
    config = {"configurable": {"thread_id": current_thread_id}}

    result = await graph.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        context=Context(user_id=None, user_name=None),
        config=config,
    )

    user_id = (result.get("data") or {}).get("user_id")
    if not user_id:
        return {**result, "thread_id": current_thread_id}

    set_log_context(thread_id=current_thread_id, user_id=user_id)

    if load_thread(user_id) != current_thread_id:
        save_thread(user_id, current_thread_id)

    return {**result, "thread_id": current_thread_id}
