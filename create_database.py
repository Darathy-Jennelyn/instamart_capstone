
from pathlib import Path
import sqlite3
import pandas as pd

# Project paths
BASE_DIR = Path(__file__).resolve().parent
CLEAN_DIR = BASE_DIR / "data" / "clean"
DB_PATH = BASE_DIR / "data" / "instamart.db"

# Read the three cleaned CSV files
customers = pd.read_csv(CLEAN_DIR / "customers.csv")
products = pd.read_csv(CLEAN_DIR / "products.csv")
orders = pd.read_csv(CLEAN_DIR / "orders.csv")

# Store dates in the required text format
customers["signup_date"] = (
    pd.to_datetime(customers["signup_date"])
    .dt.strftime("%Y-%m-%d")
)

orders["order_ts"] = (
    pd.to_datetime(orders["order_ts"])
    .dt.strftime("%Y-%m-%d %H:%M:%S")
)

# Connect to SQLite and load the three tables
with sqlite3.connect(DB_PATH) as conn:

    customers.to_sql(
        "customers", conn, if_exists="replace", index=False
    )

    products.to_sql(
        "products", conn, if_exists="replace", index=False
    )

    orders.to_sql(
        "orders", conn, if_exists="replace", index=False
    )

    # Display database tables and their row counts
    tables = pd.read_sql_query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """,
        conn
    )

    print("Database created successfully!")
    print("\nTables and row counts:")

    for table in tables["name"]:
        count = pd.read_sql_query(
            f"SELECT COUNT(*) AS total FROM {table}",
            conn
        )["total"].iloc[0]

        print(f"{table}: {count} rows")

    # Check the stored order timestamp format
    sample = pd.read_sql_query(
        "SELECT order_ts FROM orders LIMIT 3",
        conn
    )

    print("\nSample order timestamps:")
    print(sample.to_string(index=False))

print(f"\nDatabase location: {DB_PATH}")
