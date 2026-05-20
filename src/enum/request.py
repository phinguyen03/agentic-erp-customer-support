from enum import StrEnum


class RequestedAction(StrEnum):
    RETURN = "return"
    REFUND = "refund"
    EXCHANGE = "exchange"
    UNKNOWN = "unknown"


class EmotionalTone(StrEnum):
    NEUTRAL = "neutral"
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    DISTRESSED = "distressed"
    POLITE = "polite"
    UNKNOWN = "unknown"


class IntentTopic(StrEnum):
    RETURN_REQUEST = "return_request"
    REFUND_REQUEST = "refund_request"
    EXCHANGE_REQUEST = "exchange_request"
    POLICY_QUESTION = "policy_question"
    HUMAN_SUPPORT_REQUEST = "human_support_request"
    USER_EMAIL = "user_email"
    APPROVAL_STATUS = "approval_status"
    OUT_OF_SCOPE = "out_of_scope"