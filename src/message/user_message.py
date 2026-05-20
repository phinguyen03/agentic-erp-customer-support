from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated, NotRequired
from typing import Any
from dataclasses import dataclass
import operator


def merge_dicts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    return {**left, **right}


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    data: Annotated[dict[str, Any], merge_dicts]
    llm_calls: int
    need_provide_email: NotRequired[bool]
    conversation_complete: NotRequired[bool]                  

 
@dataclass
class Context:
    user_id: str
    user_name: str