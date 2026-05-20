import asyncio
import logging
from dotenv import load_dotenv

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from src.message.user_message import MessagesState, Context
from src.schema.ai_extraction import UserIntent
from src.schema.ai_extraction import ExtractedEmail
from src.utils.formatting import format_history, to_oai_messages
from src.utils.llm import OpenAISetup, LLM_MODEL
from src.mock_data import MOCK_CUSTOMERS


from src.workflow.handle_request import HandleRequestExecutor
from src.workflow.manager import ApprovalStatusNode

load_dotenv()

INTENT_SYSTEM_PROMPT = """You are an intent classifier for an e-commerce customer support assistant.

Your job is to classify the customer's latest request using the full conversation history for context.

Supported in-scope intents:
- return_request: the customer wants to return an item.
- refund_request: the customer wants money back or asks about refund status/policy.
- exchange_request: the customer wants to exchange an item for another item.
- policy_question: the customer asks about return, refund, or exchange rules.
- human_support_request: the customer asks to speak with a human/agent/manager.
- approval_status: the customer asks about the status of a pending approval/request.
- user_email: the customer has to provide the email first.

Out-of-scope intent:
- out_of_scope: the customer asks about anything unrelated to returns, refunds, exchanges, or support handoff.
  Examples: product recommendation, store opening hours, shipping tracking, jokes, weather, coding help, personal questions.

Rules:
- Focus on the customer's latest message.
- Use conversation history only to resolve context.
- Do not force every message into return/refund/exchange.
- If the latest message is unrelated to the supported workflow, classify it as out_of_scope.
- If information is missing, still classify the intent first, then leave missing fields as null.
- Do not guess order_id, condition, reason, or requested action.
- If the user asks for a human, set asks_for_human=true.

Return structured data matching the provided schema.
"""


EXTRACT_EMAIL_PROMPT = """You are analyzing a customer support conversation to identify the email and whether a NEW user is now speaking.

Rules:
- email: return only if the latest message EXPLICITLY contains an email address. Do NOT guess.
- is_new_user: set True if the latest message indicates a DIFFERENT person than the current identified user.
  Examples of is_new_user=True:
    - "I want to return for Minh" when current user is Anna
    - "for my friend", "for my colleague", mentions a name different from the current user
    - provides an email that belongs to a different person
  Examples of is_new_user=False:
    - same user continuing their conversation
    - no prior user identified yet (first message)
    - user re-states their own name or email
- {current_user_context}"""



client = OpenAISetup()


class ClassifyIntent:
    async def classify_intent(
        self,
        state: MessagesState,
        runtime: Runtime[Context],
    ) -> dict:
        messages = list(state["messages"])

        prev_user_id = state.get("data", {}).get("user_id")
        prev_user_name = state.get("data", {}).get("user_name")
        user_id = prev_user_id
        data_update: dict = {}

        extracted = await _extract_email(messages, current_user_name=prev_user_name)

        if extracted.is_new_user:
            if not extracted.email:
                # Different user detected but no email given — ask for it
                return {
                    "messages": [AIMessage(content="It looks like you're a different user. Could you please provide your email address?")],
                    "need_provide_email": True,
                    "data": {
                        "user_id": None,
                        "user_name": None,
                        "order_info": None,
                        "action": None,
                        "needs_manager_approval": False,
                        "topic": None,
                    },
                }
            # New user provided email — identify them
            customer = next((c for c in MOCK_CUSTOMERS if c["email"] == extracted.email), None)
            if not customer:
                return {
                    "messages": [AIMessage(content="I couldn't find an account with that email.")],
                    "need_provide_email": True,
                    "data": {},
                }
            user_id = customer["user_id"]
            data_update = {
                "user_id": user_id,
                "user_name": customer["name"],
                "order_info": None,
                "action": None,
                "needs_manager_approval": False,
                "topic": None,
            }
        elif extracted.email and not user_id:
            # First-time identification
            customer = next((c for c in MOCK_CUSTOMERS if c["email"] == extracted.email), None)
            if not customer:
                return {
                    "messages": [AIMessage(content="I couldn't find an account with that email.")],
                    "need_provide_email": True,
                    "data": {},
                }
            user_id = customer["user_id"]
            data_update = {"user_id": user_id, "user_name": customer["name"]}
        elif not user_id:
            return {
                "messages": [AIMessage(content="Could you please provide your email so I can find your account?")],
                "need_provide_email": True,
                "data": {},
            }

        response = await client.beta.chat.completions.parse(
            model=LLM_MODEL,
            messages=to_oai_messages(messages, INTENT_SYSTEM_PROMPT),
            response_format=UserIntent,
        )
        classify_topic: UserIntent = response.choices[0].message.parsed
        logging.warning(f"[ClassifyIntent]: {classify_topic}")

        return {
            "need_provide_email": False,
            "data": {**data_update, "user_id": user_id, "topic": classify_topic.topic},
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
        return {"messages": [AIMessage(content="I only support return, exchange, refund, manager request.")], "conversation_complete": True}


async def _extract_email(messages: list, current_user_name: str | None = None) -> ExtractedEmail:
    current_user_context = (
        f"Current identified user: {current_user_name}."
        if current_user_name
        else "No user identified yet."
    )
    prompt = EXTRACT_EMAIL_PROMPT.replace("{current_user_context}", current_user_context)
    completion = await client.beta.chat.completions.parse(
        model=LLM_MODEL,
        messages=to_oai_messages(messages, prompt),
        response_format=ExtractedEmail,
    )
    result: ExtractedEmail = completion.choices[0].message.parsed
    logging.warning(f"Extract email: {result}")
    return result if result else ExtractedEmail()


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
        {END: END, "handle_request": "handle_request", "check_approval_status": "check_approval_status", "handle_out_of_scope": "escalate"},
    )
    workflow.add_edge("handle_request", END)
    workflow.add_edge("check_approval_status", END)
    workflow.add_edge("escalate", END)
    return workflow.compile(checkpointer=MemorySaver())

graph = build_graph()


async def main():
    from src.app import chat
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
