
import pandas as pd

# 1. Load cleaned data
customers = pd.read_csv("data/clean/customers.csv")
orders = pd.read_csv("data/clean/orders.csv")

# --------------------------------------------------
# CUSTOMER VALIDATION (A3)
# --------------------------------------------------

# Check customer count
assert len(customers) == 1200

# Check city counts
city_counts = customers["city"].value_counts().to_dict()

assert city_counts == {
    "Pune": 227,
    "Delhi": 210,
    "Bengaluru": 197,
    "Chennai": 191,
    "Hyderabad": 191,
    "Mumbai": 184
}

# Check gender counts
gender_counts = customers["gender"].value_counts().to_dict()

assert gender_counts == {
    "female": 610,
    "male": 560,
    "unknown": 30
}

# Check that no ages are missing
assert customers["age"].isna().sum() == 0

# Check that all ages are within the valid range
assert customers["age"].between(18, 60).all()

# --------------------------------------------------
# ORDER VALIDATION (A4)
# --------------------------------------------------

# Check total order count
assert len(orders) == 12309

# Check that every order ID is unique
assert orders["order_id"].nunique() == 12309

# Check order status counts
status_counts = orders["status"].value_counts().to_dict()

assert status_counts == {
    "completed": 11110,
    "cancelled": 1199
}

# Check that no order amount is missing
assert orders["order_amount"].isna().sum() == 0

# Check completed orders have no missing delivery times
completed = orders[orders["status"] == "completed"]

assert completed["delivery_minutes"].isna().sum() == 0

# Check cancelled orders have missing delivery times
cancelled = orders[orders["status"] == "cancelled"]

assert cancelled["delivery_minutes"].isna().sum() == 1199

# Check completed order revenue
revenue = completed["order_amount"].sum()

assert round(revenue, 2) == 2998668.80

# Print success message
print("ALL CHECKPOINTS PASSED")
