import asyncio
import logging
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, HumanMessage
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

load_dotenv()

INTENT_SYSTEM_PROMPT = """You are an intent classifier for an e-commerce customer support assistant.

Your job is to classify the customer's latest request using the full conversation history for context.

Supported in-scope intents:
- return_request: the customer wants to return an item.
- refund_request: the customer wants money back or asks about refund status/policy.
- exchange_request: the customer wants to exchange an item for another item.
- policy_question: the customer asks about return, refund, or exchange rules.
- human_support_request: the customer asks to speak with a human/agent/manager.
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


EXTRACT_EMAIL_PROMPT = """You are identifying which customer is contacting support through email.

Rules:
- Only return a email if the customer EXPLICITLY states their email in the message.
- Do NOT guess or infer a email from context.
- If no email is explicitly stated, return null."""


RESPONSE_SYSTEM_PROMPT = """You are a helpful customer support assistant for an e-commerce store.
Based on the conversation and extracted intent, write a natural, concise reply to the customer.
- If order_id is missing, ask for it politely.
- If emotional_tone is angry or distressed, be empathetic.
- Keep responses short and focused."""


client = OpenAISetup()


class ClassifyIntent:
    async def classify_intent(
        self,
        state: MessagesState,
        runtime: Runtime[Context],
    ) -> dict:
        messages = list(state["messages"])
        last_user_msg = next(
            (m.content for m in reversed(messages) if isinstance(m, HumanMessage)), ""
        )

        user_id = state.get("data", {}).get("user_id")
        data_update: dict = {}

        if not user_id:
            email = await _extract_email(last_user_msg)
            if not email:
                return {
                    "messages": [AIMessage(content="Could you please provide your email so I can find your account?")],
                    "need_provide_email": True,
                    "data": {},
                }
            customer = next((c for c in MOCK_CUSTOMERS if c["email"] == email), None)
            if not customer:
                return {
                    "messages": [AIMessage(content="I couldn't find an account with that email.")],
                    "need_provide_email": True,
                    "data": {},
                }
            user_id = customer["user_id"]
            data_update = {"user_id": user_id, "user_name": customer["name"]}

        logging.warning("Chat History:\n%s", format_history(messages))
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


class ResponseWriter:
    async def write_response(
        self,
        state: MessagesState,
        runtime: Runtime[Context],
    ) -> dict:
        data = state["data"]
        history = format_history(list(state["messages"]))
        logging.warning(f"history chat -> {history}")
        prompt = (
            f"Conversation so far:\n{history}\n\n"
            f"Extracted intent: {data.get('intent')}, "
            f"order_id: {data.get('order_id')}, "
            f"emotional_tone: {data.get('emotional_tone')}"
        )
        completion = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": RESPONSE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        response_text = completion.choices[0].message.content
        logging.info("response_writer: %s", response_text)
        return {
            "messages": [AIMessage(content=response_text)],
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
        return {"messages": [AIMessage(content="I only support return, exchange, refund, manager request.")]}


async def _extract_email(message: str) -> str | None:
    completion = await client.beta.chat.completions.parse(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": EXTRACT_EMAIL_PROMPT},
            {"role": "user", "content": message},
        ],
        response_format=ExtractedEmail,
    )
    result: ExtractedEmail = completion.choices[0].message.parsed
    logging.warning(f"Extract email: {result}")
    return result.email if result else None


def route_intent(state: MessagesState):
    if state.get("need_provide_email"):
        return END
    topic = state["data"].get("topic")
    if topic in ("user_email", "return_request", "refund_request", "exchange_request", "policy_question", "human_support_request"):
        return "handle_request"
    return "handle_out_of_scope"


def build_graph():
    workflow = StateGraph(MessagesState, context_schema=Context)
    classify = ClassifyIntent()
    escalate = EscalateExecutor()
    handle_request = HandleRequestExecutor()
    workflow.add_node("classify_intent", classify.classify_intent)
    workflow.add_node("escalate", escalate.escalate)
    workflow.add_node("handle_request", handle_request.handle_request)
    workflow.add_edge(START, "classify_intent")
    workflow.add_conditional_edges(
        "classify_intent",
        route_intent,
        {END: END, "handle_request": "handle_request", "handle_out_of_scope": "escalate"},
    )
    workflow.add_edge("escalate", END)
    workflow.add_edge("handle_request", END)
    return workflow.compile(checkpointer=MemorySaver())

graph = build_graph()


async def main():
    from src.app import chat
    while True:
        logging.warning("START")
        message = input()
        response = await chat(message=message)
        ai_response = response["messages"][-1].content
        logging.warning("Assistant: %s", ai_response)
        #logging.warning("History:\n%s", format_history(response["messages"]))

if __name__ == "__main__":
    asyncio.run(main())
