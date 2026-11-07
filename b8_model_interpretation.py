
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


# 1. Load lapse prediction data
df = pd.read_csv("outputs/lapse_features.csv")

X = df.drop(columns=["customer_id", "lapsed"])
y = df["lapsed"]
customer_ids = df["customer_id"]


# 2. Define numerical and categorical features
numerical_features = [
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


# 3. Split the data
X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
    X,
    y,
    customer_ids,
    test_size=0.2,
    stratify=y,
    random_state=42
)


# 4. Create preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_features),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"),
         categorical_features)
    ]
)


# 5. Train the selected Logistic Regression model from B6
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", LogisticRegression(C=0.1, class_weight="balanced",
                                 max_iter=1000))
])

model.fit(X_train, y_train)


# 6. Feature interpretation using model coefficients
feature_names = model.named_steps["preprocessor"].get_feature_names_out()

coefficients = model.named_steps["model"].coef_[0]

feature_importance = pd.DataFrame({
    "feature": feature_names,
    "coefficient": coefficients
})

feature_importance["absolute_coefficient"] = (
    feature_importance["coefficient"].abs()
)

feature_importance = feature_importance.sort_values(
    by="absolute_coefficient",
    ascending=False
)

print("\nTOP 10 IMPORTANT FEATURES")
print("-------------------------")
print(feature_importance.head(10))

feature_importance.to_csv(
    "outputs/b8_feature_importance.csv",
    index=False
)


# 7. Save the trained model
joblib.dump(model, "outputs/lapse_model.joblib")

print("\nModel saved successfully.")


# 8. Load the saved model and verify predictions
loaded_model = joblib.load("outputs/lapse_model.joblib")

original_predictions = model.predict(X_test)
loaded_predictions = loaded_model.predict(X_test)

print("\nMODEL VERIFICATION")
print("------------------")
print("Predictions match:",
      (original_predictions == loaded_predictions).all())


# 9. Get lapse probabilities for test customers
lapse_probabilities = loaded_model.predict_proba(X_test)[:, 1]

test_results = pd.DataFrame({
    "customer_id": id_test.values,
    "lapse_probability": lapse_probabilities,
    "actually_lapsed": y_test.values
})


# 10. Identify Premium customers
# 10. Identify Premium customers
segments = pd.read_csv("outputs/customer_segments.csv")

premium_customers = segments[
    segments["is_premium"] == True
]["customer_id"]

retention_list = test_results[
    test_results["customer_id"].isin(premium_customers)
]


# 11. Rank Premium customers by lapse probability
retention_list = retention_list.sort_values(
    by="lapse_probability",
    ascending=False
)

retention_list = retention_list.head(10)

retention_list.to_csv(
    "outputs/retention_list.csv",
    index=False
)

print("\nRETENTION LIST")
print("--------------")
print(retention_list)

print("\nNumber of customers in retention list:",
      len(retention_list))

print("\nB8 completed successfully.")
