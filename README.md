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