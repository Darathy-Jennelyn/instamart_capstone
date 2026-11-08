
import sqlite3
import json
from pathlib import Path
from datetime import datetime

from d2_tfidf_retrieval import retrieve


# Project paths
DB_PATH = "data/instamart.db"
LEDGER_PATH = Path("outputs/refund_ledger.jsonl")


# 1. Get order details from SQLite
def get_order(order_id):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT order_id, status, order_amount, delivery_minutes
        FROM orders
        WHERE order_id = ?
        """,
        (order_id,)
    )

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return {"error": "order not found"}

    return {
        "order_id": result[0],
        "status": result[1],
        "order_amount": result[2],
        "delivery_minutes": result[3]
    }


# 2. Search relevant policy information
def search_policy(query):

    results = retrieve(query, k=3)

    return {"results": results}


# 3. Calculate the refund amount
def calculate_refund(order_amount, delivery_minutes):

    if delivery_minutes > 45:
        refund = order_amount
    else:
        refund = 0

    return {"refund_inr": round(refund, 2)}


# 4. Issue a refund and record it in the ledger
def issue_refund(order_id, refund_inr):

    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": "issue_refund",
        "order_id": order_id,
        "refund_inr": refund_inr
    }

    with open(LEDGER_PATH, "a") as file:
        file.write(json.dumps(entry) + "\n")

    return {"refund_inr": refund_inr}


# 5. Escalate refund to a human
def escalate_to_human(order_id, refund_inr):

    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": "escalate_to_human",
        "order_id": order_id,
        "refund_inr": refund_inr
    }

    with open(LEDGER_PATH, "a") as file:
        file.write(json.dumps(entry) + "\n")

    return {"refund_inr": refund_inr}


# Tool specifications
TOOLS_SPEC = [

    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "Fetch order details using the order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": "Search the policy documents for relevant information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "calculate_refund",
            "description": "Calculate the refund amount based on delivery time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_amount": {"type": "number"},
                    "delivery_minutes": {"type": "number"}
                },
                "required": ["order_amount", "delivery_minutes"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "issue_refund",
            "description": "Issue an eligible refund and record it in the refund ledger.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "refund_inr": {"type": "number"}
                },
                "required": ["order_id", "refund_inr"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Record a refund above INR 1000 for human escalation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "refund_inr": {"type": "number"}
                },
                "required": ["order_id", "refund_inr"]
            }
        }
    }

]


# Map tool names to Python functions
TOOL_MAP = {
    "get_order": get_order,
    "search_policy": search_policy,
    "calculate_refund": calculate_refund,
    "issue_refund": issue_refund,
    "escalate_to_human": escalate_to_human
}
