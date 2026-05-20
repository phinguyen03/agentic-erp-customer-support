
import logging
from datetime import datetime

from src.message.user_message import MessagesState, Context
from src.utils.formatting import format_history, to_oai_messages
from src.utils.llm import OpenAISetup, LLM_MODEL
from src.utils.approval_store import submit_approval
from src.schema.ai_extraction import UserReturnRequest
from src.mock_data import MOCK_ORDERS

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.runtime import Runtime


USER_REQUEST_EXTRACTION_PROMPT = """
    You are an information extraction agent for an e-commerce return/refund/exchange workflow.

    Extract only the fields required by the UserReturnRequest schema from the customer's message.

    Rules:
    - Do not invent missing information.
    - If order ID is not mentioned, set order_id to null.
    - If product condition is missing or unclear, set reported_condition to null.
    - If the reason is not clearly stated, set customer_reason to null.
    - requested_action must be one of: return, refund, exchange, or unknown.
    - Set asks_for_human to true only if the customer clearly asks for a human, staff, manager, or real person.
    - Detect emotional_tone from the customer's wording. Use unknown if unclear.
    - Return only structured data matching the schema.
"""


client = OpenAISetup()


class HandleRequestExecutor:
    async def handle_request(
        self,
        state: MessagesState,
        runtime: Runtime[Context],
    ) -> MessagesState:
        messages = list(state["messages"])

        response = await client.beta.chat.completions.parse(
            model=LLM_MODEL,
            messages=to_oai_messages(messages, USER_REQUEST_EXTRACTION_PROMPT),
            response_format=UserReturnRequest,
        )
        user_request: UserReturnRequest = response.choices[0].message.parsed

        # Normalize LLM hallucinated string "null"/"none" to actual None
        if user_request.order_id and user_request.order_id.lower() in ("null", "none", "n/a"):
            user_request.order_id = None

        if not user_request.order_id:
            return {"messages": [AIMessage(content="Would you like to give me your order Id, so I can find them?")]}
        
        order_info: list[dict] = []
        for order in MOCK_ORDERS:
            if user_request.order_id == order["order_id"]:
                order_info.append({
                    "order_date": order["order_date"],
                    "order_status": order["status"],
                    "order_items": order["items"],
                    "order_id": order["order_id"],
                    "condition_reported": order["items"][0]["condition_reported"],
                    "total_amount": order["total_amount"]
                })

        if not order_info:
            return {"messages": [AIMessage(content=f"You don't have any items related to {user_request.order_id}")], "conversation_complete": True}

        today = datetime.now().date()
        order_date = datetime.fromisoformat(order_info[0]["order_date"]).date()
        order_day_offset = (today - order_date).days
        if order_day_offset > 30:
            return {"messages": [AIMessage(content=f"Your order {user_request.order_id} is over 30 days. So you can't return item.")], "conversation_complete": True}
        elif order_info[0]["condition_reported"] != "good":
            return {"messages": [AIMessage(content=f"Your order {user_request.order_id} is not in good condition. So you can't return item.")], "conversation_complete": True}
        elif order_info[0]["total_amount"] >= 50:
            user_id = state["data"].get("user_id")
            action = user_request.requested_action.value
            request_id = submit_approval(
                user_id=user_id,
                order_id=user_request.order_id,
                action=action,
                amount=order_info[0]["total_amount"],
            )
            return {
                "messages": [AIMessage(content=f"Your {action} request for order {user_request.order_id} (${order_info[0]['total_amount']:.2f}) requires manager approval. Submitted as request #{request_id}. You can ask me for the status anytime.")],
                "conversation_complete": True,
            }

        logging.warning(f"[HANDLEREQUEST] History: {format_history(messages)}")

        action = user_request.requested_action.value
        success_msg = {
            "return": f"Your return for order {user_request.order_id} has been approved and submitted.",
            "refund": f"Your refund for order {user_request.order_id} has been approved. Amount returns within 3-5 business days.",
        }.get(action, f"Your {action} request for order {user_request.order_id} has been processed.")

        return {"messages": [AIMessage(content=success_msg)], "conversation_complete": True}