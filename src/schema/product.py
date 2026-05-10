from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from src.enum.product import LoyaltyTier, ProductCondition, OrderStatus, ProductCategory


class Customer(BaseModel):
    """
    Represents a customer account in the mock ERP system.

    This schema stores basic customer identity information used for
    order lookup, refund requests, exchange requests, and support
    workflow personalization.
    """

    model_config = ConfigDict(extra="forbid")

    customer_id: Annotated[
        str,
        Field(
            description="Unique customer identifier used to connect customers with their orders.",
            examples=["cus_001"],
        ),
    ]

    name: Annotated[
        str,
        Field(
            min_length=1,
            description="Full name of the customer.",
            examples=["Anna Nguyen"],
        ),
    ]

    email: Annotated[
        EmailStr,
        Field(
            description="Customer email address used for contact and support communication.",
            examples=["anna@example.com"],
        ),
    ]

    loyalty_tier: Annotated[
        LoyaltyTier,
        Field(
            default=LoyaltyTier.STANDARD,
            description="Customer loyalty level. This can be used later for priority handling or special return rules.",
        ),
    ]


class Product(BaseModel):
    """
    Represents a product sold by the store.

    This schema is used to identify the product category, price, and
    whether the product normally supports exchanges. The product data
    is used together with policy documents and order data to make
    return, refund, and exchange decisions.
    """

    model_config = ConfigDict(extra="forbid")

    product_id: Annotated[
        str,
        Field(
            description="Unique product identifier used inside orders and product lookups.",
            examples=["prod_001"],
        ),
    ]

    name: Annotated[
        str,
        Field(
            min_length=1,
            description="Display name of the product.",
            examples=["Wireless Mouse"],
        ),
    ]

    category: Annotated[
        ProductCategory,
        Field(
            description="Product category used for return and exchange policy checks.",
        ),
    ]

    price: Annotated[
        float,
        Field(
            gt=0,
            description="Unit price of the product at the time of sale.",
            examples=[24.99],
        ),
    ]

    exchange_allowed: Annotated[
        bool,
        Field(
            default=False,
            description="Whether this product is normally eligible for exchange based on store rules.",
        ),
    ]


class OrderItem(BaseModel):
    """
    Represents a single item inside an order.

    Each order can contain one or more order items. This schema stores
    the product reference, quantity, purchase price, and the customer's
    reported condition of the item.
    """

    model_config = ConfigDict(extra="forbid")

    order_item_id: Annotated[
        str,
        Field(
            description="Unique identifier for this item inside an order.",
            examples=["item_1001_1"],
        ),
    ]

    product_id: Annotated[
        str,
        Field(
            description="Product identifier that links this order item to product data.",
            examples=["prod_001"],
        ),
    ]

    quantity: Annotated[
        int,
        Field(
            ge=1,
            description="Number of units purchased for this order item.",
        ),
    ]

    unit_price: Annotated[
        float,
        Field(
            gt=0,
            description="Price per unit when the order was placed.",
        ),
    ]

    condition_reported: Annotated[
        ProductCondition,
        Field(
            description="Condition of the item as reported by the customer or mock ERP data.",
        ),
    ]


class Order(BaseModel):
    """
    Represents a customer order in the mock ERP system.

    This schema is used by the AI workflow to look up purchase date,
    order status, purchased items, and refund amount. The order data
    is combined with customer answers and policy RAG results to decide
    whether a return, refund, or exchange request can continue.
    """

    model_config = ConfigDict(extra="forbid")

    order_id: Annotated[
        str,
        Field(
            description="Unique order identifier provided by the customer or found in ERP data.",
            examples=["ord_1001"],
        ),
    ]

    customer_id: Annotated[
        str,
        Field(
            description="Customer identifier linked to this order.",
            examples=["cus_001"],
        ),
    ]

    order_date: Annotated[
        datetime,
        Field(
            description="Date and time when the order was placed. Used to check the return window.",
        ),
    ]

    status: Annotated[
        OrderStatus,
        Field(
            description="Current order status, such as delivered, cancelled, or refunded.",
        ),
    ]

    items: Annotated[
        list[OrderItem],
        Field(
            default_factory=list,
            description="List of products included in this order.",
        ),
    ]

    total_amount: Annotated[
        float,
        Field(
            ge=0,
            description="Total order amount. Used to decide whether manager approval is required for a refund.",
        ),
    ]