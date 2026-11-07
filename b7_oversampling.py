
import pandas as pd

from imblearn.over_sampling import RandomOverSampler

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# 1. Load dataset
data = pd.read_csv("outputs/lapse_features.csv")

X = data.drop(columns=["customer_id", "lapsed"])
y = data["lapsed"]


# 2. Separate numerical and categorical features
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


# 3. Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)


# 4. Check original training distribution
print("BEFORE OVERSAMPLING")
print("-------------------")
print(y_train.value_counts())


# 5. Apply Random Oversampling only to training data
oversampler = RandomOverSampler(random_state=42)

X_train_over, y_train_over = oversampler.fit_resample(
    X_train,
    y_train
)

print("\nAFTER OVERSAMPLING")
print("------------------")
print(y_train_over.value_counts())

print("\nTraining shape before:", X_train.shape)
print("Training shape after:", X_train_over.shape)
print("Testing shape:", X_test.shape)


# 6. Create preprocessing function
def create_preprocessor():
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_features),
            ("cat", OneHotEncoder(
                drop="first",
                handle_unknown="ignore"
            ), categorical_features)
        ]
    )


# 7. Train original Logistic Regression
original_model = Pipeline([
    ("preprocessor", create_preprocessor()),
    ("model", LogisticRegression(
        C=0.1,
        class_weight=None,
        max_iter=1000,
        random_state=42
    ))
])

original_model.fit(X_train, y_train)


# 8. Train oversampled Logistic Regression
oversampled_model = Pipeline([
    ("preprocessor", create_preprocessor()),
    ("model", LogisticRegression(
        C=0.1,
        class_weight=None,
        max_iter=1000,
        random_state=42
    ))
])

oversampled_model.fit(X_train_over, y_train_over)


# 9. Evaluate both models on the same test data
models = {
    "Original Logistic Regression": original_model,
    "Oversampled Logistic Regression": oversampled_model
}

results = []

print("\nMODEL COMPARISON")
print("----------------")

for name, model in models.items():

    predictions = model.predict(X_test)

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


# 10. Save comparison
results_df = pd.DataFrame(results)

results_df.to_csv(
    "outputs/b7_model_comparison.csv",
    index=False
)

print("\nComparison saved successfully.")
