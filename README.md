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
| Q5 | Customers spending above the average completed-order spend using CTEs | 550 customers; average ₹2,552.06 |
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