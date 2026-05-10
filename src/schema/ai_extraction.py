from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field
from src.enum.product import ProductCondition
from src.enum.request import IntentTopic, EmotionalTone, RequestedAction



class UserIntent(BaseModel):
    """
    Classifies the main topic/intention of the customer's latest message.
    """

    model_config = ConfigDict(extra="forbid")

    topic: Annotated[
        IntentTopic,
        Field(
            description="Primary topic/intention of the customer's latest message.",
            examples=["exchange_request"],
        ),
    ]


class UserReturnRequest(BaseModel):
    """
    Represents structured information extracted from the customer's message.

    This schema is designed for the LLM extraction step. The AI reads the
    customer's message and extracts the order ID, requested action, product
    condition, reason for return, human-support request, and emotional tone.
    The workflow can then decide whether to ask follow-up questions, retrieve
    policy context, check mock ERP data, or escalate to a human.
    """

    model_config = ConfigDict(extra="forbid")

    order_id: Annotated[
        str | None,
        Field(
            description="Order ID mentioned by the customer. If user does not provide order id -> null",
            examples=["ord_1001"],
        ),
    ] = None
    requested_action: Annotated[
        RequestedAction,
        Field(
            default=RequestedAction.UNKNOWN,
            description="Action requested by the customer: return, refund, exchange, or unknown.",
        ),
    ]
    reported_condition: Annotated[
        Optional[ProductCondition],
        Field(
            default=None,
            description="Product condition reported by the customer. If missing or unclear, the assistant should ask a follow-up question.",
            examples=["good"],
        ),
    ]
    customer_reason: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Customer's reason for requesting a return, refund, or exchange.",
            examples=["The item does not fit my needs."],
        ),
    ]
    asks_for_human: Annotated[
        bool,
        Field(
            default=False,
            description="Whether the customer explicitly asks to speak with a human support agent.",
        ),
    ]
    emotional_tone: Annotated[
        EmotionalTone,
        Field(
            default=EmotionalTone.UNKNOWN,
            description="Detected emotional tone of the customer message. Angry, frustrated, or distressed customers may require escalation.",
        ),
    ]


class ExtractedEmail(BaseModel):
    """email extracted from a customer message for account lookup."""

    model_config = ConfigDict(extra="forbid")

    email: Annotated[str | None, Field(description="Email of the customer as mentioned in the message. Null if no email is present.", examples=["minh@example.com"])] = None