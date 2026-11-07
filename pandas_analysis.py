
import pandas as pd

# 1. Load cleaned data
orders = pd.read_csv("data/clean/orders.csv")
customers = pd.read_csv("data/clean/customers.csv")
products = pd.read_csv("data/clean/products.csv")

# 2. Select completed orders
completed = orders[orders["status"] == "completed"]

# 3. Add city and category information
data = completed.merge(customers[["customer_id", "city"]], on="customer_id")
data = data.merge(products[["product_id", "category"]], on="product_id")

# --------------------------------------------------
# PART A: PANDAS CROSS-CHECK
# --------------------------------------------------

print("\nPART A: PANDAS CROSS-CHECK")

# 4. Recreate SQL Q2 using pivot_table
pivot = pd.pivot_table(
    data,
    index="city",
    columns="category",
    values="order_amount",
    aggfunc="sum",
    fill_value=0,
    margins=True
)

print("\nRevenue by City and Category:")
print(pivot.round(2))

pivot_total = pivot.loc["All", "All"]
sql_total = completed["order_amount"].sum()

print("\nPivot Total:", round(pivot_total, 2))
print("SQL Total:", round(sql_total, 2))
print("Totals Match:", pivot_total == sql_total)

# 5. City-wise revenue, average and order count
city_stats = data.groupby("city").agg(
    total_revenue=("order_amount", "sum"),
    average_order=("order_amount", "mean"),
    order_count=("order_amount", "count")
)

print("\nCity-wise Statistics:")
print(city_stats.round(2))


# --------------------------------------------------
# PART B: EXPLORATORY DATA ANALYSIS
# --------------------------------------------------

print("\nPART B: EXPLORATORY DATA ANALYSIS")

amount = completed["order_amount"]

# 6. Mean, median and skewness
print("\nOrder Amount Statistics:")
print("Mean:", round(amount.mean(), 2))
print("Median:", round(amount.median(), 2))
print("Skewness:", round(amount.skew(), 2))

# 7. Quartiles and IQR
q1 = amount.quantile(0.25)
q2 = amount.quantile(0.50)
q3 = amount.quantile(0.75)

iqr = q3 - q1

lower_fence = q1 - 1.5 * iqr
upper_fence = q3 + 1.5 * iqr

print("\nQuartiles:")
print("Q1:", round(q1, 2))
print("Median:", round(q2, 2))
print("Q3:", round(q3, 2))
print("IQR:", round(iqr, 2))

print("\nOutlier Fences:")
print("Lower Fence:", round(lower_fence, 2))
print("Upper Fence:", round(upper_fence, 2))

# 8. Count outliers
print("\nOutlier Counts:")
print("Below Lower Fence:", (amount < lower_fence).sum())
print("Above Upper Fence:", (amount > upper_fence).sum())

# 9. Correlation matrix
columns = [
    "order_amount",
    "discount_pct",
    "quantity",
    "delivery_minutes"
]

correlation = completed[columns].corr()

print("\nCorrelation Matrix:")
print(correlation.round(3))

# 10. Find the strongest correlation
correlation_values = correlation.abs()

# Remove diagonal values (each column correlated with itself)
for column in correlation_values.columns:
    correlation_values.loc[column, column] = 0

strongest = correlation_values.stack().idxmax()

print("\nStrongest Correlation:")
print(strongest[0], "and", strongest[1])
print("Correlation:", round(correlation.loc[strongest[0], strongest[1]], 3))
