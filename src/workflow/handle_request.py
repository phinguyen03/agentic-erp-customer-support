
import logging

from src.message.user_message import MessagesState, Context
from src.utils.formatting import format_history, to_oai_messages
from src.utils.llm import OpenAISetup, LLM_MODEL
from src.schema.ai_extraction import UserReturnRequest
from src.schema.product import Order
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
    ) -> dict:
        messages = list(state["messages"])

        response = await client.beta.chat.completions.parse(
            model=LLM_MODEL,
            messages=to_oai_messages(messages, USER_REQUEST_EXTRACTION_PROMPT),
            response_format=UserReturnRequest,
        )
        user_request: UserReturnRequest = response.choices[0].message.parsed
        
        if not user_request.order_id:
            return {"messages": [AIMessage(content="Would you like to give me your order Id, so I can find them?")]}
        
        #customer_id = runtime.context.user_id
        order_info: Order = []
        for order in MOCK_ORDERS:
            if user_request.order_id == order["order_id"]:
                order_info.append({
                    "order_date": order["order_date"],
                    "order_status": order["status"],
                    "order_item": order["items"]
                })

        if not order_info:
            return {"messages": [AIMessage(content=f"You don't have any items related to {user_request.order_id}")]}
        
        logging.warning(f"[HANDLEREQUEST] History: {format_history(messages)}, Order items: {order_info}")