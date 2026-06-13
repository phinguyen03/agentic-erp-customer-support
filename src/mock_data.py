from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone.utc)

MOCK_CUSTOMERS = [
    {
        "user_id": "cus_001",
        "name": "Anna Nguyen",
        "email": "anna@example.com",
        "loyalty_tier": "standard",
    },
    {
        "user_id": "cus_002",
        "name": "Minh Tran",
        "email": "minh@example.com",
        "loyalty_tier": "gold",
    },
]

MOCK_PRODUCTS = [
    {
        "product_id": "prod_001",
        "name": "Wireless Mouse",
        "category": "electronics",
        "price": 24.99,
        "exchange_allowed": True,
    },
    {
        "product_id": "prod_002",
        "name": "Running Shoes",
        "category": "fashion",
        "price": 79.99,
        "exchange_allowed": True,
    },
    {
        "product_id": "prod_003",
        "name": "Coffee Beans",
        "category": "food",
        "price": 14.99,
        "exchange_allowed": False,
    },
    {
        "product_id": "prod_004",
        "name": "Office Chair",
        "category": "furniture",
        "price": 129.99,
        "exchange_allowed": True,
    },
]

MOCK_ORDERS = [
    {
        "order_id": "ord_1001",
        "customer_id": "cus_001",
        "order_date": (NOW - timedelta(days=10)).strftime("%Y-%m-%d"),
        "status": "delivered",
        "items": [
            {
                "order_item_id": "item_1001_1",
                "product_id": "prod_001",
                "quantity": 1,
                "unit_price": 24.99,
                "condition_reported": "good",
            }
        ],
        "total_amount": 50.99,
    },
    {
        "order_id": "ord_1002",
        "customer_id": "cus_001",
        "order_date": (NOW - timedelta(days=35)).strftime("%Y-%m-%d"),
        "status": "delivered",
        "items": [
            {
                "order_item_id": "item_1002_1",
                "product_id": "prod_002",
                "quantity": 1,
                "unit_price": 79.99,
                "condition_reported": "good",
            }
        ],
        "total_amount": 79.99,
    },
    {
        "order_id": "ord_1003",
        "customer_id": "cus_002",
        "order_date": (NOW - timedelta(days=5)).strftime("%Y-%m-%d"),
        "status": "delivered",
        "items": [
            {
                "order_item_id": "item_1003_1",
                "product_id": "prod_003",
                "quantity": 2,
                "unit_price": 14.99,
                "condition_reported": "opened",
            }
        ],
        "total_amount": 29.98,
    },
    {
        "order_id": "ord_1004",
        "customer_id": "cus_002",
        "order_date": (NOW - timedelta(days=15)).strftime("%Y-%m-%d"),
        "status": "delivered",
        "items": [
            {
                "order_item_id": "item_1004_1",
                "product_id": "prod_004",
                "quantity": 1,
                "unit_price": 129.99,
                "condition_reported": "good",
            }
        ],
        "total_amount": 129.99,
    },
]

MOCK_RETURN_POLICIES = {
    "default": {
        "return_window_days": 30,
        "required_condition": ["good", "unused", "unopened"],
        "auto_refund_limit": 50.00,
    },
    "category_rules": {
        "electronics": {
            "returnable": True,
            "exchange_allowed": True,
        },
        "fashion": {
            "returnable": True,
            "exchange_allowed": True,
        },
        "food": {
            "returnable": False,
            "exchange_allowed": False,
        },
        "furniture": {
            "returnable": True,
            "exchange_allowed": True,
        },
    },
}

MOCK_REFUND_REQUESTS = []

MOCK_MANAGER_APPROVALS = []