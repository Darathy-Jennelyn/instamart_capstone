
import pandas as pd

# 1. Read the raw datasets
customers = pd.read_csv("data/raw/customers.csv")
products = pd.read_csv("data/raw/products.csv")
orders = pd.read_csv("data/raw/orders.csv", low_memory=False)

# 2. Check shape, data types and missing values
for name, df in [
    ("Customers", customers),
    ("Products", products),
    ("Orders", orders)
]:
    print(f"\n--- {name} ---")
    print("Shape:", df.shape)
    print("\nData types:")
    print(df.dtypes)
    print("\nMissing values:")
    print(pd.DataFrame({
        "Missing Count": df.isna().sum(),
        "Missing %": (df.isna().mean() * 100).round(2)
    }))

# 3. Orders audit
print("\n--- Orders Audit ---")
print("Exact duplicates:", orders.duplicated().sum())
print("Pending orders:", (orders["status"] == "pending").sum())
print("Distinct order IDs:", orders["order_id"].nunique())

amount = pd.to_numeric(orders["order_amount"], errors="coerce")
delivery = pd.to_numeric(orders["delivery_minutes"], errors="coerce")

print("Non-numeric order amounts:", amount.isna().sum())
print("Negative delivery times:", (delivery < 0).sum())
print("Blank delivery times:",
      orders["delivery_minutes"].isna().sum() +
      orders["delivery_minutes"].astype(str).str.strip().eq("").sum())

# 4. Customers audit
print("\n--- Customers Audit ---")
age = pd.to_numeric(customers["age"], errors="coerce")

print("Blank ages:", customers["age"].isna().sum())
print("Ages outside 10-100:",
      (age.notna() & ~age.between(10, 100)).sum())

print("Distinct raw city spellings:", customers["city"].nunique())
print("Distinct nonblank gender values:",
      customers.loc[
          customers["gender"].notna() &
          customers["gender"].astype(str).str.strip().ne(""),
          "gender"
      ].nunique())

print("Blank genders:",
      customers["gender"].isna().sum() +
      customers["gender"].astype(str).str.strip().eq("").sum())

print("\nRAW DATA AUDIT COMPLETED.")
