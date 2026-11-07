
import pandas as pd
import matplotlib.pyplot as plt
import os

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA


# ---------------- B1: RFM Calculation ----------------

orders = pd.read_csv("data/clean/orders.csv")

orders["order_ts"] = pd.to_datetime(orders["order_ts"])

# Keep completed orders only
orders = orders[orders["status"] == "completed"]

snapshot = pd.Timestamp("2025-10-01 00:00:00")

rfm = orders.groupby("customer_id").agg(
    recency=("order_ts", lambda x: (snapshot - x.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("order_amount", "sum")
)

print("Number of customers:", len(rfm))


# ---------------- B2: K-Means Clustering ----------------

rfm_values = rfm[["recency", "frequency", "monetary"]]

scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_values)

results = []

for k in range(2, 9):

    model = KMeans(
        n_clusters=k,
        n_init=10,
        random_state=42
    )

    labels = model.fit_predict(rfm_scaled)

    inertia = model.inertia_
    silhouette = silhouette_score(rfm_scaled, labels)

    results.append([k, inertia, silhouette])

results_df = pd.DataFrame(
    results,
    columns=["K", "Inertia", "Silhouette"]
)

print("\nB2: K-Means Results")
print(results_df.round(3).to_string(index=False))


# ---------------- B3: Customer Segment Profiling ----------------

# Apply the selected K = 4
kmeans = KMeans(
    n_clusters=4,
    n_init=10,
    random_state=42
)

rfm["segment_id"] = kmeans.fit_predict(rfm_scaled)

# Calculate the number of customers in each segment
segment_sizes = rfm["segment_id"].value_counts().sort_index()

print("\nB3: Number of Customers in Each Segment")
print(segment_sizes)

# Calculate average RFM values for each segment
segment_profile = rfm.groupby("segment_id").agg(
    customer_count=("recency", "count"),
    mean_recency=("recency", "mean"),
    mean_frequency=("frequency", "mean"),
    mean_monetary=("monetary", "mean")
)

print("\nB3: Segment Profiles")
print(segment_profile.round(2))


# Assign meaningful names based on segment behaviour

high_value_id = segment_profile["mean_monetary"].idxmax()
frequent_id = segment_profile["mean_frequency"].idxmax()

remaining_ids = [
    segment_id for segment_id in segment_profile.index
    if segment_id not in [high_value_id, frequent_id]
]

# Of the remaining groups, higher recency indicates less recent activity
at_risk_id = segment_profile.loc[remaining_ids, "mean_recency"].idxmax()

regular_id = [
    segment_id for segment_id in remaining_ids
    if segment_id != at_risk_id
][0]

segment_names = {
    high_value_id: "High-Value Customers",
    frequent_id: "Frequent Customers",
    at_risk_id: "At-Risk Customers",
    regular_id: "Regular Customers"
}

rfm["segment_name"] = rfm["segment_id"].map(segment_names)

# Premium customers belong to the segment with the highest mean monetary value
rfm["is_premium"] = rfm["segment_id"] == high_value_id

print("\nB3: Segment Names")
for segment_id, name in segment_names.items():
    print(segment_id, ":", name)

print("\nPremium Segment ID:", high_value_id)


# Save customer segment details
os.makedirs("outputs", exist_ok=True)

customer_segments = rfm.reset_index()

customer_segments = customer_segments[
    [
        "customer_id",
        "recency",
        "frequency",
        "monetary",
        "segment_id",
        "segment_name",
        "is_premium"
    ]
]

customer_segments.to_csv(
    "outputs/customer_segments.csv",
    index=False
)

print("\nCustomer segments saved successfully.")


# ---------------- B3: PCA Visualization ----------------

pca = PCA(n_components=2)

pca_values = pca.fit_transform(rfm_scaled)

print("\nPCA Explained Variance:")
print("PC1:", round(pca.explained_variance_ratio_[0], 3))
print("PC2:", round(pca.explained_variance_ratio_[1], 3))
print(
    "Total:",
    round(sum(pca.explained_variance_ratio_), 3)
)

# Create a DataFrame for plotting
pca_df = pd.DataFrame(
    pca_values,
    columns=["PC1", "PC2"]
)

pca_df["segment_id"] = rfm["segment_id"].values

# Plot the four clusters
for segment_id in sorted(pca_df["segment_id"].unique()):

    segment_data = pca_df[
        pca_df["segment_id"] == segment_id
    ]

    plt.scatter(
        segment_data["PC1"],
        segment_data["PC2"],
        label=segment_names[segment_id],
        alpha=0.6
    )

plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.title("Customer Segments - PCA Visualization")
plt.legend()
plt.tight_layout()

plt.savefig("outputs/customer_segments_pca.png")
plt.show()

print("\nPCA plot saved successfully.")

