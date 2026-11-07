
import pandas as pd
import os

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score


# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

orders = pd.read_csv("data/clean/orders.csv")
customers = pd.read_csv("data/clean/customers.csv")
products = pd.read_csv("data/clean/products.csv")

orders["order_ts"] = pd.to_datetime(orders["order_ts"])
customers["signup_date"] = pd.to_datetime(customers["signup_date"])


# --------------------------------------------------
# 2. DEFINE DATE BOUNDARIES
# --------------------------------------------------

cutoff_date = pd.Timestamp("2025-09-01")
end_date = pd.Timestamp("2025-10-01")


# --------------------------------------------------
# 3. IDENTIFY PREVIOUSLY ACTIVE CUSTOMERS
# --------------------------------------------------

completed_orders = orders[
    orders["status"] == "completed"
].copy()

previous_orders = completed_orders[
    completed_orders["order_ts"] < cutoff_date
]

active_customers = previous_orders["customer_id"].unique()


# --------------------------------------------------
# 4. CREATE LAPSE TARGET
# --------------------------------------------------

september_orders = completed_orders[
    (completed_orders["order_ts"] >= cutoff_date) &
    (completed_orders["order_ts"] < end_date)
]

september_customers = september_orders["customer_id"].unique()

lapse_cohort = pd.DataFrame({
    "customer_id": active_customers
})

lapse_cohort["lapsed"] = (
    ~lapse_cohort["customer_id"].isin(september_customers)
).astype(int)


# --------------------------------------------------
# 5. CALCULATE HISTORICAL CUSTOMER FEATURES
# --------------------------------------------------

# Recency, frequency, monetary, discount and delivery

customer_features = previous_orders.groupby("customer_id").agg(
    last_order_date=("order_ts", "max"),
    frequency=("order_id", "count"),
    monetary=("order_amount", "sum"),
    avg_discount_pct=("discount_pct", "mean"),
    avg_delivery_minutes=("delivery_minutes", "mean")
).reset_index()

# Calculate recency in days

customer_features["recency_days"] = (
    cutoff_date - customer_features["last_order_date"]
).dt.days

customer_features = customer_features.drop(
    columns=["last_order_date"]
)


# --------------------------------------------------
# 6. CALCULATE CANCELLATION RATE
# --------------------------------------------------

# Use only orders before the cutoff with final statuses

final_orders = orders[
    (orders["order_ts"] < cutoff_date) &
    (orders["status"].isin(["completed", "cancelled"]))
]

cancellation_features = final_orders.groupby("customer_id").agg(
    total_final_orders=("order_id", "count"),
    cancelled_orders=("status", lambda x: (x == "cancelled").sum())
).reset_index()

cancellation_features["cancellation_rate"] = (
    cancellation_features["cancelled_orders"] /
    cancellation_features["total_final_orders"]
)

cancellation_features = cancellation_features[
    ["customer_id", "cancellation_rate"]
]


# --------------------------------------------------
# 7. FIND MOST FREQUENT PRODUCT CATEGORY
# --------------------------------------------------

# Connect historical completed orders with product categories

category_orders = previous_orders.merge(
    products[["product_id", "category"]],
    on="product_id",
    how="left"
)

category_features = category_orders.groupby("customer_id").agg(
    most_frequent_category=(
        "category",
        lambda x: x.mode().iloc[0]
    )
).reset_index()


# --------------------------------------------------
# 8. ADD CUSTOMER DEMOGRAPHIC FEATURES
# --------------------------------------------------

customer_details = customers[
    ["customer_id", "city", "signup_date", "age", "gender"]
].copy()

customer_details["tenure_days"] = (
    cutoff_date - customer_details["signup_date"]
).dt.days

customer_details = customer_details.drop(
    columns=["signup_date"]
)


# --------------------------------------------------
# 9. COMBINE ALL FEATURES
# --------------------------------------------------

customer_features = customer_features.merge(
    cancellation_features,
    on="customer_id",
    how="left"
)

customer_features = customer_features.merge(
    category_features,
    on="customer_id",
    how="left"
)

customer_features = customer_features.merge(
    customer_details,
    on="customer_id",
    how="left"
)

# Combine features with the lapse target

model_data = lapse_cohort.merge(
    customer_features,
    on="customer_id",
    how="left"
)


# --------------------------------------------------
# 10. PREPARE FEATURES AND TARGET
# --------------------------------------------------

X = model_data.drop(
    columns=["customer_id", "lapsed"]
)

y = model_data["lapsed"]


# --------------------------------------------------
# 11. TRAIN-TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)


# --------------------------------------------------
# 12. BASELINE MODEL
# --------------------------------------------------

# Predict every test customer as not lapsed (0)

baseline_predictions = [0] * len(y_test)

baseline_accuracy = accuracy_score(
    y_test,
    baseline_predictions
)

baseline_f1 = f1_score(
    y_test,
    baseline_predictions,
    zero_division=0
)


# --------------------------------------------------
# 13. SAVE OUTPUTS
# --------------------------------------------------

os.makedirs("outputs", exist_ok=True)

lapse_cohort.to_csv(
    "outputs/lapse_cohort.csv",
    index=False
)

model_data.to_csv(
    "outputs/lapse_features.csv",
    index=False
)


# --------------------------------------------------
# 14. DISPLAY RESULTS
# --------------------------------------------------

print("\nB4 - LAPSE PREDICTION RESULTS")
print("--------------------------------")

print("\nCohort Results")

print("Previously active customers:", len(lapse_cohort))
print("Lapsed customers:", (y == 1).sum())
print("Not lapsed customers:", (y == 0).sum())

print("Lapse percentage:",
      round(y.mean() * 100, 2), "%")


print("\nFeature Information")

print("Number of features:", X.shape[1])
print("Feature columns:")
print(X.columns.tolist())

print("\nMissing values:")
print(X.isnull().sum())


print("\nTrain-Test Split")

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))


print("\nBaseline Model Results")

print("Baseline accuracy:",
      round(baseline_accuracy, 4))

print("Baseline lapsed-class F1:",
      round(baseline_f1, 4))


print("\nOutput files saved:")
print("outputs/lapse_cohort.csv")
print("outputs/lapse_features.csv")


# ==================================================
# B5 - FEATURE PREPARATION AND PREPROCESSING
# ==================================================

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


# 1. Load B4 feature dataset

data = pd.read_csv("outputs/lapse_features.csv")


# 2. Separate features and target

X = data.drop(columns=["customer_id", "lapsed"])
y = data["lapsed"]


# 3. Identify numerical and categorical columns

numeric_features = [
    "frequency",
    "monetary",
    "avg_discount_pct",
    "avg_delivery_minutes",
    "recency_days",
    "cancellation_rate",
    "age",
    "tenure_days"
]

categorical_features = [
    "most_frequent_category",
    "city",
    "gender"
]


# 4. Split the data into training and testing sets

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)


# 5. Create preprocessing steps

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(
            drop="first",
            handle_unknown="ignore"
        ), categorical_features)
    ]
)


# 6. Create a Pipeline

preprocessing_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor)
    ]
)


# 7. Fit preprocessing on training data only

X_train_processed = preprocessing_pipeline.fit_transform(X_train)

# Transform test data using the fitted training preprocessing
X_test_processed = preprocessing_pipeline.transform(X_test)


# 8. Get the transformed feature names

feature_names = preprocessing_pipeline.named_steps[
    "preprocessor"
].get_feature_names_out()


# 9. Convert processed data into DataFrames

# Convert sparse output to normal array if required

if hasattr(X_train_processed, "toarray"):
    X_train_processed = X_train_processed.toarray()

if hasattr(X_test_processed, "toarray"):
    X_test_processed = X_test_processed.toarray()


train_processed = pd.DataFrame(
    X_train_processed,
    columns=feature_names
)

test_processed = pd.DataFrame(
    X_test_processed,
    columns=feature_names
)


# 10. Add target column

train_processed["lapsed"] = y_train.reset_index(drop=True)

test_processed["lapsed"] = y_test.reset_index(drop=True)


# 11. Save processed datasets

train_processed.to_csv(
    "outputs/X_train_processed.csv",
    index=False
)

test_processed.to_csv(
    "outputs/X_test_processed.csv",
    index=False
)


# 12. Display results

print("\nB5 - FEATURE PREPROCESSING RESULTS")
print("-----------------------------------")

print("\nOriginal feature count:", X.shape[1])

print("Numerical features:", len(numeric_features))
print("Categorical features:", len(categorical_features))

print("\nTraining shape:", train_processed.shape)
print("Testing shape:", test_processed.shape)

print("\nTransformed feature count:", len(feature_names))

print("\nTransformed feature names:")
print(list(feature_names))

print("\nTraining target distribution:")
print(train_processed["lapsed"].value_counts().sort_index())

print("\nTesting target distribution:")
print(test_processed["lapsed"].value_counts().sort_index())

print("\nMissing values in training data:",
      train_processed.isnull().sum().sum())

print("Missing values in testing data:",
      test_processed.isnull().sum().sum())

print("\nSaved files:")
print("outputs/X_train_processed.csv")
print("outputs/X_test_processed.csv")
