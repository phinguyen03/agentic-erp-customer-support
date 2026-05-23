from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


def format_history(messages: list[BaseMessage]) -> str:
    parts = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            parts.append(f"<user>{msg.content}</user>")
        elif isinstance(msg, AIMessage):
            parts.append(f"<assistant>{msg.content}</assistant>")
    return "\n".join(parts)


def to_oai_messages(messages) -> list[dict]:
    result = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            result.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            result.append({"role": "assistant", "content": msg.content})
    return result
