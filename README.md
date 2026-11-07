# Instamart Customer Intelligence & Support Copilot

## Overview

The Instamart Customer Intelligence & Support Copilot is a 21-day capstone project designed to address customer intelligence, retention and support operations using data analytics and AI-based workflows.

### Technology Stack

- Python
- pandas and NumPy
- SQLite
- scikit-learn
- joblib
- Git and GitHub

All datasets are synthetic and generated using the supplied `generate_data.py` script. All language-model interactions use the supplied offline `mock_llm.py` file.

## Reproduce

This section will contain the complete numbered instructions to reproduce the project from a clean clone, including environment setup, dependency installation, data generation and execution of all project scripts.

### Initial setup and data generation

1. Create a virtual environment:

   ```powershell
   python -m venv venv
   ```

2. Activate the virtual environment:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Install the required dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Generate the synthetic datasets:

   ```powershell
   python generate_data.py
   ```

   Expected output:

   ```text
   generated: customers=1200 products=40 orders_raw=13084 tickets=164
   ```

*Note: The Reproduce section will be updated as additional scripts are developed, so that the final instructions cover the entire project.*

## Part A — Data Foundation: Clean, Store, Query

### A1 — Project Setup and Synthetic Data Generation

**Objective**

Set up the project environment, install the required dependencies and generate the synthetic datasets needed for the Customer Intelligence & Support Copilot.

**Work completed**

- Created the project repository and initialized Git on the `main` branch.
- Created and activated a Python virtual environment.
- Installed the required Python libraries.
- Created `requirements.txt` and `.gitignore`.
- Created the required project directories.
- Added the supplied `generate_data.py` and `mock_llm.py` files without modifying their contents.
- Executed the data generation script successfully.

**Generated datasets**

The data generation script produced the following datasets:

| Dataset | Records |
|---|---:|
| Customers | 1,200 |
| Products | 40 |
| Orders (raw) | 13,084 |
| Support tickets | 164 |

The generated files include:

- `data/raw/customers.csv`
- `data/raw/products.csv`
- `data/raw/orders.csv`
- `data/raw/tickets.csv`
- `data/raw/policy_eval.csv`
- `data/raw/agent_scenarios.csv`
- Five policy documents in `data/policies/`

**Git**

The initial project setup and synthetic data generation were committed to the `main` branch.

Initial commit message:

`Initial project setup and synthetic data generation is done`

### A2 — Raw Data Audit

**Objective**

The objective of the raw data audit was to understand the structure and quality of the original synthetic datasets before performing any cleaning or transformation.

The audit was performed using Python and pandas on the following datasets:

- `customers.csv`
- `products.csv`
- `orders.csv`

**Dataset overview**

| Dataset | Rows | Columns |
|---|---:|---:|
| Customers | 1,200 | 5 |
| Products | 40 | 4 |
| Orders | 13,084 | 9 |

**Data types and missing-value analysis**

The data types, missing-value counts and missing-value percentages were checked for every column.

**Customers**

| Column | Data type | Missing count | Missing % |
|---|---|---:|---:|
| customer_id | str | 0 | 0.00% |
| city | str | 0 | 0.00% |
| signup_date | str | 0 | 0.00% |
| age | float64 | 61 | 5.08% |
| gender | str | 30 | 2.50% |

**Products**

| Column | Data type | Missing count | Missing % |
|---|---|---:|---:|
| product_id | str | 0 | 0.00% |
| product_name | str | 0 | 0.00% |
| category | str | 0 | 0.00% |
| price_inr | int64 | 0 | 0.00% |

**Orders**

| Column | Data type | Missing count | Missing % |
|---|---|---:|---:|
| order_id | str | 0 | 0.00% |
| customer_id | str | 0 | 0.00% |
| product_id | str | 0 | 0.00% |
| quantity | int64 | 0 | 0.00% |
| order_ts | str | 0 | 0.00% |
| status | str | 0 | 0.00% |
| discount_pct | int64 | 0 | 0.00% |
| order_amount | str | 53 | 0.41% |
| delivery_minutes | float64 | 2,541 | 19.42% |

**Order data quality findings**

| Check | Result |
|---|---:|
| Raw order rows | 13,084 |
| Exact duplicate rows | 119 |
| Pending orders | 656 |
| Distinct order IDs | 12,309 |
| Non-numeric order amounts | 120 |
| Negative delivery times | 106 |
| Blank delivery times | 2,541 |

**Customer data quality findings**

| Check | Result |
|---|---:|
| Blank ages | 61 |
| Ages outside 10–100 | 6 |
| Distinct raw city spellings | 24 |
| Distinct nonblank raw gender values | 10 |
| Blank gender values | 30 |

**Observations**

The raw order dataset contains exact duplicate records and multiple records associated with the same order ID. It also contains pending orders, missing and non-numeric order amounts, negative delivery durations and missing delivery times.

The customer dataset contains missing and invalid ages, inconsistent city and gender spellings, and missing gender values.

The products dataset has no missing values in any of its columns.

The audit identified these issues without modifying the original raw CSV files. These findings will guide the cleaning operations performed in the subsequent tasks.

Audit script: audit_raw_data.py

### A3 — Customer Data Cleaning

**Objective**

The objective was to clean and standardise the raw customer dataset before using it for further analysis.

**Cleaning operations**

| Column | Cleaning operation |
|---|---|
| city | Removed leading and trailing spaces and applied title case |
| gender | Standardised gender values to male, female and unknown |
| age | Converted to numeric, treated values outside 10–100 as missing and filled missing values using the median age of the corresponding city |
| signup_date | Converted to datetime |

**Results after cleaning**

--- Customer Cleaning Results ---

City counts:
city
Bengaluru    197
Chennai      191
Delhi        210
Hyderabad    191
Mumbai       184
Pune         227
Name: count, dtype: int64

Gender counts:
gender
female     610
male       560
unknown     30
Name: count, dtype: int64

Age details:
Missing ages: 0
Minimum age: 18.0
Maximum age: 60.0

The cleaned dataset was saved as `data/clean/customers.csv`. The original raw customer dataset was left unchanged.

**Cleaning script:** `clean_customers.py`

### A4 — Order Data Cleaning

**Objective**

The objective was to clean the raw order dataset by removing duplicate records, correcting invalid monetary values and handling missing delivery times.

**Cleaning operations**

| Column / Issue | Cleaning operation |
|---|---|
| order_ts | Converted to datetime |
| Exact duplicate rows | Removed |
| Duplicate order IDs | Retained only the record with the latest timestamp |
| order_amount | Converted to numeric; missing or invalid values were calculated using product price, quantity and discount |
| Negative delivery_minutes | Replaced with missing values |
| Completed delivery times | Missing values filled using the median delivery time of the corresponding product category |
| Cancelled delivery times | Left missing because cancelled orders were never delivered |

**Results after cleaning**

| Check | Result |
|---|---:|
| Final order rows | 12,309 |
| Completed orders | 11,110 |
| Cancelled orders | 1,199 |
| Pending orders | 0 |
| Missing order amounts | 0 |
| Missing completed delivery times | 0 |
| Missing cancelled delivery times | 1,199 |
| Completed order amount total | INR 2,998,668.80 |

The cleaned order dataset was saved as `data/clean/orders.csv`. The products dataset was also saved unchanged as `data/clean/products.csv`.

The original raw CSV files were left unchanged.

**Cleaning script:** `clean_orders.py`

### A5 — Store cleaned data in SQLite

Created the SQLite database at `data/instamart.db` using Python's `sqlite3` module and pandas.

- Loaded the three cleaned CSV files into SQLite tables: `customers`, `products`, and `orders`.
- Stored `order_ts` in the required `YYYY-MM-DD HH:MM:SS` text format.
- Used `if_exists="replace"` to make database creation reproducible.

**Database validation summary:**

| Table | Rows |
|---|---:|
| customers | 1,200 |
| products | 40 |
| orders | 12,309 |

**Output:** `data/instamart.db`
**Validation Script:** `validate_database.py`

### A6 — SQL Analysis

Created seven SQL queries in `sql/queries.sql` and executed them using Python's `pandas.read_sql_query()` against the SQLite database.

The queries demonstrate filtering, grouping, joins, subqueries, CTEs and window functions.

**Query results:**

| Query | Analysis | Result |
|---|---|---|
| Q1 | Completed orders above ₹500 and customers with qualifying spend above ₹8,000 | 30 customers |
| Q2 | Revenue by city and product category using three-table JOIN | 30 rows; total ₹29,98,668.80 |
| Q3 | Products priced above the average catalogue price | 11 products |
| Q4 | Customers without any completed orders using LEFT JOIN | 25 customers |
| Q5 | Customers spending above the average completed-order spend using CTEs | 550 customers above the overall average customer spend of ₹2,552.06 |
| Q6 | Customer spending rankings by city using RANK(), DENSE_RANK() and ROW_NUMBER() | 1,175 customers; 8 rows where RANK() differs from ROW_NUMBER() |
| Q7 | Daily completed revenue and cumulative revenue using a window function | 183 days; final cumulative revenue ₹29,98,668.80 |

**Q6 observation:** RANK() leaves gaps after tied positions, whereas ROW_NUMBER() assigns a unique sequential number to every row, even when customers have the same spend.

**Output:** Seven SQL queries stored in `sql/queries.sql` and executed through `run_sql_queries.py`.

### A7 — Pandas Cross-Check and Exploratory Analysis

**Objective**

The objective was to cross-check the SQL revenue results using pandas and perform exploratory analysis on completed orders.

**Analysis performed**

- Used `pivot_table()` to calculate revenue by city and product category.
- Used `groupby()` and aggregation to calculate total revenue, average order amount and order count for each city.
- Calculated mean, median, skewness, quartiles and interquartile range (IQR) of order amounts.
- Identified potential outliers using the 1.5 × IQR method.
- Calculated correlations between order amount, discount percentage, quantity and delivery time.

**Results**

**Revenue cross-check**

The total revenue calculated using pandas was ₹29,98,668.80, matching the total obtained from the SQL analysis.

**City-wise revenue**

| City | Total Revenue (₹) | Average Order Amount (₹) | Order Count |
|---|---:|---:|---:|
| Bengaluru | 5,23,643.40 | 276.47 | 1,894 |
| Chennai | 4,63,629.15 | 272.72 | 1,700 |
| Delhi | 5,02,829.80 | 243.62 | 2,064 |
| Hyderabad | 5,28,589.90 | 284.95 | 1,855 |
| Mumbai | 4,79,058.50 | 297.00 | 1,613 |
| Pune | 5,00,918.05 | 252.48 | 1,984 |

**Order amount distribution**

| Statistic | Value |
|---|---:|
| Mean | ₹269.91 |
| Median | ₹135.00 |
| Skewness | 4.61 |
| Q1 | ₹64.80 |
| Q3 | ₹297.00 |
| IQR | ₹232.20 |
| Lower fence | -₹283.50 |
| Upper fence | ₹645.30 |
| Outliers above upper fence | 897 |
| Outliers below lower fence | 0 |

The mean being higher than the median and the positive skewness indicate a right-skewed order amount distribution. The 897 high-value outliers are statistical observations and are not necessarily data errors.

**Correlation analysis**

The strongest absolute correlation was between `order_amount` and `discount_pct`, at -0.095. This is a very weak negative correlation and does not establish a causal relationship.

**Script:** `pandas_analysis.py`

### A8 — Final Data Validation

**Objective**

The objective was to verify that the cleaned datasets and SQLite database satisfy the expected data quality checkpoints before proceeding to the next project part.

**Validation checks**

The validation scripts checked the following:

- Customer record count and unique customer IDs.
- Expected city and gender distributions.
- Missing customer ages and valid age range.
- Order record count and unique order IDs.
- Completed and cancelled order counts.
- Missing order amounts.
- Missing delivery times in completed orders.
- Missing delivery times in cancelled orders.
- Total completed-order revenue.
- SQLite table existence and record counts.

**Expected validation results**

| Check | Expected Result |
|---|---:|
| Customers | 1,200 |
| Products | 40 |
| Orders | 12,309 |
| Unique order IDs | 12,309 |
| Completed orders | 11,110 |
| Cancelled orders | 1,199 |
| Missing customer ages | 0 |
| Missing order amounts | 0 |
| Missing completed delivery times | 0 |
| Missing cancelled delivery times | 1,199 |
| Completed revenue | ₹29,98,668.80 |

The validation scripts were executed to check the cleaned data and database against these expected results.

**Scripts:**
- `validate_clean_data.py`
- `validate_database.py`

**Successful validation output:**

`ALL CHECKPOINTS PASSED`

PART - B

### B1 — RFM Analysis

Calculated customer-level RFM (Recency, Frequency, Monetary) values using cleaned customer order data.

- **Snapshot date:** 2025-10-01
- **Orders considered:** Completed orders only
- **Customers included:** 1,175

| Metric | Result |
|---|---:|
| Median Recency | 19 days |
| Minimum Recency | 0 days |
| Maximum Recency | 180 days |
| Mean Frequency | 9.46 |
| Maximum Frequency | 33 |
| Mean Monetary | ₹2,552.06 |
| Maximum Monetary | ₹14,766.55 |

**Output:** RFM values calculated in `customer_segmentation.py` for customer segmentation.

### B2 — K-Means Clustering

Standardized the RFM values using `StandardScaler` and applied K-Means clustering with K values from 2 to 8.

- **Scaling:** StandardScaler
- **Algorithm:** K-Means
- **n_init:** 10
- **random_state:** 42
- **Evaluation metrics:** Inertia and Silhouette Score

| K | Inertia | Silhouette Score |
|---:|---:|---:|
| 2 | 1820.761 | 0.465 |
| 3 | 1268.235 | 0.445 |
| 4 | 743.071 | 0.526 |
| 5 | 617.367 | 0.480 |
| 6 | 503.171 | 0.482 |
| 7 | 408.460 | 0.416 |
| 8 | 366.503 | 0.412 |

**Selected K: 4**

K = 4 was selected because it had the highest silhouette score and was around the elbow point, where the reduction in inertia started slowing down. The final choice will also be assessed through business interpretation of the customer segments in B3.

**Output:** RFM values calculated in `customer_segmentation.py` for customer segmentation.

### B3 — Customer Segment Profiling and PCA

Applied K-Means clustering with K = 4 and profiled customers using their RFM values.

| Segment | Customer Count | Mean Recency | Mean Frequency | Mean Monetary |
|---|---:|---:|---:|---:|
| Regular Customers | 436 | 28.86 | 3.77 | ₹1,057.62 |
| High-Value Customers | 138 | 24.12 | 6.77 | ₹7,129.70 |
| Frequent Customers | 419 | 8.77 | 19.40 | ₹3,410.02 |
| At-Risk Customers | 182 | 109.04 | 2.20 | ₹685.99 |

- **Premium segment:** High-Value Customers (Segment 1).
- **PCA:** Reduced the three RFM features to two principal components for visualization.
- **Explained variance:** PC1 = 63.4%, PC2 = 21.8%, total = 85.2%.

**Output files:**
- `outputs/customer_segments.csv`
- `outputs/customer_segments_pca.png`

The four segments represent different customer behaviours and can help identify high-value customers, frequent shoppers, regular customers, and customers who may need retention campaigns.

### B4 – Lapse Cohort, Feature Engineering and Baseline Evaluation

**Objective:** Identify previously active customers who did not place a completed order during September 2025 and prepare the dataset for lapse prediction.

**1. Lapse Cohort and Target Creation**

- Cutoff date: 2025-09-01.
- Included customers with at least one completed order before the cutoff date.
- Identified customers who placed at least one completed order between September 1 and September 30, 2025.
- Created the target variable `lapsed`:
  - `1` – Customer did not place a completed order during September.
  - `0` – Customer placed at least one completed order during September.

**Cohort Results:**

| Metric | Result |
|---|---:|
| Previously active customers | 1,156 |
| Lapsed customers | 443 |
| Not lapsed customers | 713 |
| Lapse percentage | 38.32% |

**2. Customer Feature Engineering**

Created 11 customer features using orders dated strictly before September 1, 2025, and the cleaned customer and product datasets.

| Feature | Description |
|---|---|
| recency_days | Days between cutoff date and last completed order |
| frequency | Number of completed orders |
| monetary | Total spending from completed orders |
| avg_discount_pct | Average discount percentage |
| cancellation_rate | Cancelled orders divided by all orders with a final status |
| avg_delivery_minutes | Average delivery time |
| most_frequent_category | Most frequently purchased product category |
| city | Customer city |
| age | Customer age |
| gender | Customer gender |
| tenure_days | Days between signup date and cutoff date |

**3. Data Leakage Prevention**

- Used only orders dated before September 1, 2025, for historical order-based features.
- September order activity was used only to generate the target variable.
- Excluded customer segment labels from B3.
- Used the cleaned customer table for demographic and signup information.

**4. Train-Test Split**

Used stratified train-test splitting with the following configuration:

- Test size: 20%
- Random state: 42
- Stratification: Target variable (`lapsed`)

| Dataset | Rows |
|---|---:|
| Training | 924 |
| Testing | 232 |
| Total | 1,156 |

**5. Baseline Model Evaluation**

Established a baseline by predicting every test customer as not lapsed.

| Metric | Result |
|---|---:|
| Accuracy | 61.64% |
| Lapsed-class F1 score | 0.00 |

The baseline achieved 61.64% accuracy but failed to identify any lapsed customers. This provides a reference for evaluating the actual classification models in subsequent tasks.

**6. Output Files**

- `outputs/lapse_cohort.csv` – Customer IDs and lapse target labels.
- `outputs/lapse_features.csv` – Customer features combined with the lapse target.

**Status:** B4 completed and validated against the project reference values.

**Output:** lapse_prediction.py

### B5 – Feature Preparation and Preprocessing

**Objective:** Prepare customer features for machine learning by scaling numerical features and encoding categorical features.

**1. Feature Separation**

The 11 original features were divided into two groups:

- Numerical features: 8
- Categorical features: 3

**Numerical features:**
- frequency
- monetary
- avg_discount_pct
- avg_delivery_minutes
- recency_days
- cancellation_rate
- age
- tenure_days

**Categorical features:**
- most_frequent_category
- city
- gender

**2. Preprocessing Techniques**

- **StandardScaler:** Applied to numerical features to standardize their values.
- **OneHotEncoder:** Applied to categorical features to convert them into numerical representations.
- Used `drop="first"` to remove the first category from each categorical feature.
- Used `handle_unknown="ignore"` to handle categories not encountered during training.
- Used `ColumnTransformer` to apply the appropriate transformations to each feature group.
- Used a scikit-learn Pipeline to combine the preprocessing steps.

**3. Train-Test Split**

Used the same stratified split configuration established in B4:

- Test size: 20%
- Random state: 42
- Stratification: Target variable (`lapsed`)

| Dataset | Rows |
|---|---:|
| Training | 924 |
| Testing | 232 |

**4. Preprocessing Results**

| Metric | Result |
|---|---:|
| Original features | 11 |
| Numerical features | 8 |
| Categorical features | 3 |
| Transformed features | 19 |
| Training rows | 924 |
| Testing rows | 232 |
| Missing values in training | 0 |
| Missing values in testing | 0 |

The transformed dataset contains 19 features after OneHotEncoder expands the categorical columns.

**5. Data Leakage Prevention**

- Split the data before fitting preprocessing.
- Fitted StandardScaler and OneHotEncoder using training data only.
- Used the fitted preprocessing Pipeline to transform the test data.
- Test data was not used to calculate scaling parameters or learn encoding categories.

For subsequent cross-validation, preprocessing will be included inside the model Pipeline so that each fold fits its own preprocessing using only its training portion.

**6. Output Files**

- `outputs/X_train_processed.csv` – Preprocessed training dataset with target.
- `outputs/X_test_processed.csv` – Preprocessed testing dataset with target.

**Status:** B5 completed and verified successfully.

### B6 – Model Training and Hyperparameter Tuning

**Objective:** Train and compare Logistic Regression and Random Forest models to predict customer lapse.

**Approach:**

1. Loaded the original `outputs/lapse_features.csv` dataset.
2. Separated input features and the lapse target.
3. Used an 80:20 stratified train-test split with `random_state=42`.
4. Applied StandardScaler to numerical features and OneHotEncoder to categorical features.
5. Combined preprocessing and model training using Scikit-learn Pipelines to prevent data leakage during cross-validation.
6. Used 5-fold StratifiedKFold cross-validation.
7. Applied GridSearchCV with F1-score as the evaluation metric.
8. Compared both models using accuracy, precision, recall and F1-score on the test dataset.

**Best Hyperparameters:**

| Model | Best Parameters | CV F1 |
|---|---|---:|
| Logistic Regression | C=0.1, class_weight=balanced | 0.7014 |
| Random Forest | n_estimators=200, max_depth=10, class_weight=balanced | 0.6920 |

**Test Set Results:**

| Metric | Logistic Regression | Random Forest |
|---|---:|---:|
| Accuracy | 0.7284 | 0.7284 |
| Precision | 0.5915 | 0.6048 |
| Recall | 0.9438 | 0.8427 |
| F1-score | 0.7273 | 0.7042 |

**Selected Model:** Logistic Regression.

Logistic Regression achieved the highest test F1-score of 0.7273, exceeding the required target of 0.55. It also achieved higher recall (0.9438), making it effective at identifying previously active customers who lapsed.

**Output:** - `outputs/b6_model_comparison.csv`
**Script:** - `b6_model_training.py`
**Result:** Both models were successfully trained and evaluated. Logistic Regression was selected based on its higher cross-validation and test F1-scores.

### B7 – Class Balance Experiment Using Oversampling

**Objective:**  
To understand how oversampling the minority class affects the performance of the lapse prediction model.

**Method:**
- Used RandomOverSampler with `random_state=42`.
- Oversampled only the training dataset.
- Kept all original training rows and added randomly duplicated lapsed customer records until both classes had equal counts.
- Used the same original test dataset for both models.
- Compared an unweighted Logistic Regression model trained on the original imbalanced data with another unweighted Logistic Regression model trained on the oversampled data.

**Class distribution:**

| Dataset | Not Lapsed (0) | Lapsed (1) |
|---|---:|---:|
| Before oversampling | 570 | 354 |
| After oversampling | 570 | 570 |

Training rows increased from 924 to 1,140. The test dataset remained unchanged at 232 rows.

**Model Comparison:**

| Metric | Original Model | Oversampled Model |
|---|---:|---:|
| Accuracy | 0.7629 | 0.7198 |
| Precision | 0.6545 | 0.5870 |
| Recall | 0.8090 | 0.9101 |
| F1 Score | 0.7236 | 0.7137 |

**Observation:**

Oversampling increased recall from 80.90% to 91.01%, meaning the model identified more lapsed customers. However, precision decreased from 65.45% to 58.70%, indicating that more active customers could also be incorrectly flagged as lapsed.

Recall showed the largest change among the evaluated metrics.

**Business Interpretation:**

The oversampled model can help the retention team identify more potentially lapsed customers. However, the lower precision means the team may need to contact more customers who are not actually lapsed. The choice between the models depends on whether identifying more at-risk customers or reducing unnecessary customer outreach is the higher priority.

**Output:** `outputs/b7_model_comparison.csv`
**Script:** `b7_oversampling.py`

### B8 – Feature Interpretation, Model Saving and Retention List

**Objective:**

To understand the important features influencing lapse predictions, save the selected model and generate a retention list of Premium customers with high predicted lapse probabilities.

**1. Feature Interpretation**

Extracted Logistic Regression coefficients to understand how different customer attributes influence lapse predictions.

Top 10 features based on absolute coefficient values:

| Feature | Coefficient |
|---|---:|
| frequency | -1.2862 |
| most_frequent_category_Electronics | -0.3421 |
| most_frequent_category_Snacks | -0.2065 |
| city_Delhi | -0.1850 |
| most_frequent_category_Grocery | -0.1814 |
| city_Pune | 0.1203 |
| gender_male | -0.1050 |
| city_Hyderabad | -0.1042 |
| cancellation_rate | -0.1041 |
| most_frequent_category_Personal Care | 0.0949 |

Frequency was the most influential feature based on its absolute coefficient. Its negative coefficient indicates that higher purchase frequency is associated with a lower predicted likelihood of lapse in this model.

**2. Model Saving and Verification**

- Trained the selected Logistic Regression model using the B6 configuration.
- Saved the trained model using Joblib.
- Loaded the saved model and compared its predictions with the original model.

Verification result: `Predictions match: True`

Saved model: `outputs/lapse_model.joblib`

**3. Retention List Generation**

- Predicted lapse probabilities for customers in the test dataset.
- Identified Premium customers using the existing B3 segmentation output.
- Ranked these customers by predicted lapse probability.
- Selected the top 10 customers for the retention list.

The generated list contained 10 customers, with predicted lapse probabilities ranging from approximately 56.54% to 67.87%.

Among these 10 customers, 2 were actually lapsed and 8 were not lapsed.

**Business Interpretation:**

The retention list demonstrates how customer risk scores can help prioritise retention efforts. Customers with higher predicted lapse probabilities can be considered for further review or targeted retention activities.

**Limitation:** Premium customer selection uses the B3 segmentation output, which was generated using the wider observation period. Therefore, this Premium classification is illustrative and may include information beyond the lapse prediction cutoff. It should not be treated as a leakage-free deployment approach.

**Output Files:**
- `outputs/b8_feature_importance.csv`
- `outputs/lapse_model.joblib`
- `outputs/retention_list.csv`

**Script:** `b8_model_interpretation.py`