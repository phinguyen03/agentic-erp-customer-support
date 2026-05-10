from enum import StrEnum


class LoyaltyTier(StrEnum):
    STANDARD = "standard"
    GOLD = "gold"
    PREMIUM = "premium"


class ProductCategory(StrEnum):
    ELECTRONICS = "electronics"
    FASHION = "fashion"
    FOOD = "food"
    FURNITURE = "furniture"


class OrderStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ProductCondition(StrEnum):
    GOOD = "good"
    UNUSED = "unused"
    UNOPENED = "unopened"
    OPENED = "opened"
    DAMAGED = "damaged"
    MISSING_PARTS = "missing_parts"