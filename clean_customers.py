
import pandas as pd
import os

# 1. Load the raw customer data
customers = pd.read_csv("data/raw/customers.csv")

print("Original shape:", customers.shape)

# 2. Standardise city names
customers["city"] = customers["city"].str.strip().str.title()

# 3. Standardise gender values
customers["gender"] = (customers["gender"].str.strip().str.lower()
    .map({
        "male": "male",
        "m": "male",
        "female": "female",
        "f": "female"
    })
    .fillna("unknown")
)

# 4. Convert age to numeric
customers["age"] = pd.to_numeric(customers["age"], errors="coerce")

# Treat ages outside 10–100 as missing
customers.loc[
    (customers["age"] < 10) | (customers["age"] > 100),
    "age"
] = None

# Fill missing ages using the median age of each city
customers["age"] = customers["age"].fillna(
    customers.groupby("city")["age"].transform("median")
)

# 5. Convert signup_date to datetime
customers["signup_date"] = pd.to_datetime(customers["signup_date"])

# 6. Create the clean data folder if it does not exist
os.makedirs("data/clean", exist_ok=True)

# 7. Save the cleaned customer data
customers.to_csv("data/clean/customers.csv", index=False)

# 8. Display validation results
print("\n--- Customer Cleaning Results ---")

print("\nCity counts:")
print(customers["city"].value_counts().sort_index())

print("\nGender counts:")
print(customers["gender"].value_counts().sort_index())

print("\nAge details:")
print("Missing ages:", customers["age"].isna().sum())
print("Minimum age:", customers["age"].min())
print("Maximum age:", customers["age"].max())

print("\nSignup date data type:")
print(customers["signup_date"].dtype)

print("\nFinal shape:", customers.shape)
print("\nClean customer data saved successfully.")
