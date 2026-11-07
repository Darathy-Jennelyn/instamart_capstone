
import pandas as pd
import os

# 1. Load raw orders and products
orders = pd.read_csv("data/raw/orders.csv")
products = pd.read_csv("data/raw/products.csv")

print("Original order rows:", len(orders))

# 2. Convert order timestamp to datetime
orders["order_ts"] = pd.to_datetime(orders["order_ts"])

# 3. Remove exact duplicate rows
orders = orders.drop_duplicates()

print("Rows after removing exact duplicates:", len(orders))

# 4. Keep only the latest record for each order_id
orders = orders.sort_values("order_ts")
orders = orders.drop_duplicates(subset="order_id", keep="last")

print("Rows after removing duplicate order IDs:", len(orders))

# 5. Get product price and category using product_id
product_prices = products.set_index("product_id")["price_inr"]
product_categories = products.set_index("product_id")["category"]

orders["price_inr"] = orders["product_id"].map(product_prices)
orders["category"] = orders["product_id"].map(product_categories)

# 6. Convert order_amount to numeric
orders["order_amount"] = pd.to_numeric(
    orders["order_amount"], errors="coerce"
)

print(
    "Missing order amounts before filling:",
    orders["order_amount"].isna().sum()
)

# 7. Fill missing order amounts using the required formula
missing_amounts = orders["order_amount"].isna()

orders.loc[missing_amounts, "order_amount"] = (
    orders.loc[missing_amounts, "price_inr"]
    * orders.loc[missing_amounts, "quantity"]
    * (1 - orders.loc[missing_amounts, "discount_pct"] / 100)
).round(2)

# 8. Replace negative delivery times with missing values
negative_delivery = orders["delivery_minutes"] < 0

print("Negative delivery times:", negative_delivery.sum())

orders.loc[negative_delivery, "delivery_minutes"] = None

# 9. Fill missing delivery times only for completed orders
completed_mask = orders["status"] == "completed"

completed_orders = orders.loc[completed_mask]

category_medians = completed_orders.groupby("category")[
    "delivery_minutes"
].transform("median")

missing_completed = completed_orders["delivery_minutes"].isna()

print(
    "Missing completed delivery times before filling:",
    missing_completed.sum()
)

orders.loc[completed_mask, "delivery_minutes"] = (
    completed_orders["delivery_minutes"].fillna(category_medians)
)

# 10. Remove temporary columns
orders = orders.drop(columns=["price_inr", "category"])

# 11. Save cleaned orders and unchanged products
os.makedirs("data/clean", exist_ok=True)

orders.to_csv(
    "data/clean/orders.csv",
    index=False,
    date_format="%Y-%m-%d %H:%M:%S"
)

products.to_csv("data/clean/products.csv", index=False)

# 12. Display final validation results
print("\n--- Order Cleaning Results ---")

print("\nFinal shape:", orders.shape)

print("\nOrder status counts:")
print(orders["status"].value_counts())

print("\nUnique order IDs:", orders["order_id"].nunique())

print("\nMissing order amounts:", orders["order_amount"].isna().sum())

print(
    "Missing completed delivery times:",
    orders.loc[completed_mask, "delivery_minutes"].isna().sum()
)

print(
    "Missing cancelled delivery times:",
    orders.loc[orders["status"] == "cancelled", "delivery_minutes"].isna().sum()
)

print(
    "\nCompleted order amount total:",
    round(orders.loc[completed_mask, "order_amount"].sum(), 2)
)

print("\nOrder timestamp data type:", orders["order_ts"].dtype)

print("\nCleaned orders and products saved successfully.")
