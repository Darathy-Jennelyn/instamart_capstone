
import sqlite3
from pathlib import Path

DB_PATH = Path("data/instamart.db")

with sqlite3.connect(DB_PATH) as conn:

    # Check table row counts
    assert conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 1200
    assert conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 40
    assert conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 12309

    # Check unique IDs
    assert conn.execute("SELECT COUNT(DISTINCT customer_id) FROM customers").fetchone()[0] == 1200
    assert conn.execute("SELECT COUNT(DISTINCT product_id) FROM products").fetchone()[0] == 40
    assert conn.execute("SELECT COUNT(DISTINCT order_id) FROM orders").fetchone()[0] == 12309

    # Check customer data
    assert conn.execute("SELECT COUNT(*) FROM customers WHERE age IS NULL").fetchone()[0] == 0

    # Check order data
    assert conn.execute("SELECT COUNT(*) FROM orders WHERE order_amount IS NULL").fetchone()[0] == 0

    assert conn.execute("""
        SELECT COUNT(*) FROM orders
        WHERE status = 'completed'
    """).fetchone()[0] == 11110

    assert conn.execute("""
        SELECT COUNT(*) FROM orders
        WHERE status = 'cancelled'
    """).fetchone()[0] == 1199

    assert conn.execute("""
        SELECT COUNT(*) FROM orders
        WHERE status = 'completed' AND delivery_minutes IS NULL
    """).fetchone()[0] == 0

    # Check completed-order revenue
    revenue = conn.execute("""
        SELECT ROUND(SUM(order_amount), 2)
        FROM orders
        WHERE status = 'completed'
    """).fetchone()[0]

    assert revenue == 2998668.80

print("ALL CHECKPOINTS PASSED")
