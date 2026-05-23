import logging
from dotenv import load_dotenv
import os

os.environ["LANGGRAPH_STRICT_MSGPACK"] = "true"

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from src.message.user_message import MessagesState, Context
from src.schema.ai_extraction import UserIntent
from src.utils.formatting import format_history, to_oai_messages
from src.utils.llm import extract_structured

from src.workflow.handle_request import HandleRequestExecutor
from src.workflow.manager import ApprovalStatusNode

load_dotenv()

INTENT_SYSTEM_PROMPT = """You are an intent classifier for an e-commerce customer support assistant.

Classify by the customer's latest message:
- return_request: wants to return an item.
- refund_request: wants money back or asks about refund status/policy.
- exchange_request: wants to exchange an item for another item.
- policy_question: asks about return, refund, or exchange rules.
- human_support_request: asks to speak with a human/agent/manager.
- approval_status: asks about the status of a pending approval/request.
- out_of_scope: anything unrelated (product recommendations, store hours, shipping tracking, jokes, weather).

Rules:
- Focus on the customer's latest message. Use history only for context.
- Do not force every message into return/refund/exchange.
- Do not guess order_id, condition, reason, or requested action.

Return structured data matching the provided schema.
"""


class ClassifyIntent:
    async def classify_intent(
        self,
        state: MessagesState,
        runtime: Runtime[Context],
    ) -> MessagesState:
        messages = list(state["messages"])

        user_id = runtime.context.user_id
        if not user_id:
            return {
                "messages": [AIMessage(content="Authentication required. Please provide your email.")],
                "need_provide_email": True,
                "data": {},
            }

        data_update: dict = {}
        if user_id != state.get("data", {}).get("user_id"):
            data_update = {"user_id": user_id, "user_name": runtime.context.user_name}

        classify_topic: UserIntent = await extract_structured(
            UserIntent, to_oai_messages(messages), INTENT_SYSTEM_PROMPT
        )
        logging.warning(f"[ClassifyIntent]: {classify_topic}")

        return {
            "need_provide_email": False,
            "data": {**data_update, "user_id": user_id, "topic": classify_topic.topic.value},
            "llm_calls": state.get("llm_calls", 0) + 1,
        }


class EscalateExecutor:
    async def escalate(
        self,
        state: MessagesState,
        runtime: Runtime[Context],
    ) -> dict:
        messages = list(state["messages"])
        logging.warning(f"[ESCALATE]: {format_history(messages)}")
        return {"messages": [AIMessage(content="I only support return, exchange, refund, and approval status requests.")], "conversation_complete": True}


def route_intent(state: MessagesState):
    if state.get("need_provide_email"):
        return END
    topic = state["data"].get("topic")
    if topic in ("return_request", "refund_request", "exchange_request", "policy_question", "human_support_request"):
        return "handle_request"
    if topic == "approval_status":
        return "check_approval_status"
    return "handle_out_of_scope"


def build_graph():
    workflow = StateGraph(MessagesState, context_schema=Context)
    classify = ClassifyIntent()
    escalate = EscalateExecutor()
    handle_request = HandleRequestExecutor()
    approval_status = ApprovalStatusNode()

    workflow.add_node("classify_intent", classify.classify_intent)
    workflow.add_node("escalate", escalate.escalate)
    workflow.add_node("handle_request", handle_request.handle_request)
    workflow.add_node("check_approval_status", approval_status.check_status)

    workflow.add_edge(START, "classify_intent")
    workflow.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            END: END,
            "handle_request": "handle_request",
            "check_approval_status": "check_approval_status",
            "handle_out_of_scope": "escalate",
        },
    )
    workflow.add_edge("handle_request", END)
    workflow.add_edge("check_approval_status", END)
    workflow.add_edge("escalate", END)
    return workflow.compile(checkpointer=MemorySaver())

graph = build_graph()
