import logging
from uuid import uuid4

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.message.user_message import Context, MessagesState
from src.utils.logger import set_log_context
from src.utils.thread_store import load_thread, save_thread
from src.workflow.base import graph


async def chat(message: str, thread_id: str | None = None) -> dict:
    """Load/Save user thread"""

    result = await graph.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        context=Context(user_id=None, user_name=None),
        config={"configurable": {"thread_id": thread_id}},
    )

    existing = load_thread(result["data"].get("user_id"))
    is_new = thread_id is None and existing is None
    thread_id = thread_id or existing or str(uuid4())
    set_log_context(thread_id=thread_id, user_id=result["data"].get("user_id"))

    if is_new:
        save_thread(result["data"].get("user_id"), thread_id)
    return result
