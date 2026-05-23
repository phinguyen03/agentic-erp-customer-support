import logging

from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime

from src.message.user_message import MessagesState, Context
from src.utils.approval_store import get_user_approvals


class ApprovalStatusNode:
    async def check_status(self, state: MessagesState, runtime: Runtime[Context]) -> dict:
        user_id = state["data"].get("user_id")
        approvals = get_user_approvals(user_id)

        if not approvals:
            return {"messages": [AIMessage(content="No pending approval requests found for your account.")], "conversation_complete": True}

        lines = []
        for a in approvals:
            status_label = {"pending": "Pending", "approved": "Approved", "declined": "Declined"}.get(a["status"], a["status"])
            lines.append(f"Request {a['request_id']}: {a['action']} for order {a['order_id']} (${a['amount']:.2f}) — {status_label}")

        msg = "Your approval requests:\n" + "\n".join(lines)
        return {"messages": [AIMessage(content=msg)], "conversation_complete": True}
