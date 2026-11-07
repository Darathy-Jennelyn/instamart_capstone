
import pandas as pd

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# 1. Load features
data = pd.read_csv("outputs/lapse_features.csv")

X = data.drop(columns=["customer_id", "lapsed"])
y = data["lapsed"]


# 2. Separate numerical and categorical columns
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


# 3. Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_features),
        ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"),
         categorical_features)
    ]
)


# 4. Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)


# 5. Cross-validation setup
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


# 6. Logistic Regression pipeline
lr_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LogisticRegression(max_iter=1000, random_state=42))
])

lr_params = {
    "model__C": [0.1, 1, 10],
    "model__class_weight": [None, "balanced"]
}

lr_grid = GridSearchCV(
    lr_pipeline,
    lr_params,
    cv=cv,
    scoring="f1",
    n_jobs=-1
)

lr_grid.fit(X_train, y_train)


# 7. Random Forest pipeline
rf_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestClassifier(random_state=42))
])

rf_params = {
    "model__n_estimators": [100, 200],
    "model__max_depth": [None, 10, 20],
    "model__class_weight": [None, "balanced"]
}

rf_grid = GridSearchCV(
    rf_pipeline,
    rf_params,
    cv=cv,
    scoring="f1",
    n_jobs=-1
)

rf_grid.fit(X_train, y_train)


# 8. Compare models
models = {
    "Logistic Regression": lr_grid,
    "Random Forest": rf_grid
}

print("\nBEST MODEL PARAMETERS")
print("---------------------")

for name, grid in models.items():
    print(f"\n{name}")
    print("Best parameters:", grid.best_params_)
    print("Best CV F1:", round(grid.best_score_, 4))


# 9. Evaluate both models on test data
print("\nTEST SET RESULTS")
print("----------------")

results = []

for name, grid in models.items():

    predictions = grid.best_estimator_.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, zero_division=0)
    recall = recall_score(y_test, predictions, zero_division=0)
    f1 = f1_score(y_test, predictions, zero_division=0)

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    })

    print(f"\n{name}")
    print("Accuracy:", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall:", round(recall, 4))
    print("F1 Score:", round(f1, 4))


# 10. Select the best model based on test F1
results_df = pd.DataFrame(results)

best_model_name = results_df.loc[
    results_df["F1 Score"].idxmax(), "Model"
]

print("\nBEST MODEL BASED ON TEST F1:", best_model_name)

# Save comparison results
results_df.to_csv("outputs/b6_model_comparison.csv", index=False)

print("\nModel comparison saved successfully.")
