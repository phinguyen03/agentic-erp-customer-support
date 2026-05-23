from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.enum.product import ProductCondition
from src.enum.request import IntentTopic, EmotionalTone, RequestedAction


class UserIntent(BaseModel):
    """
    Classifies the main topic/intention of the customer's latest message.
    """

    model_config = ConfigDict(extra="forbid")

    topic: Annotated[
        IntentTopic | None,
        Field(
            description="Primary topic/intention of the customer's latest message.",
            examples=["exchange_request"],
        ),
    ] = None


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
        Field(description="Order ID from the conversation (format: ord_XXXX)."),
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

    @field_validator("requested_action", "emotional_tone", mode="before")
    @classmethod
    def strip_quotes(cls, v):
        return v.strip('"') if isinstance(v, str) else v
