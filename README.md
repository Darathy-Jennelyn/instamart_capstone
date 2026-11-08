# Overview

The **Instamart Customer Intelligence & Support Copilot** is an end-to-end data analytics and AI-assisted customer support project built using Python, SQL, machine learning, and a supplied offline mock language model.

The project uses Instamart-style customer, product, order, and support-ticket data to demonstrate how raw business data can be transformed into useful insights and how customer support workflows can be automated.

The project is divided into four parts:

- **Part A – Data Engineering and SQL:** Auditing and cleaning raw data, creating a SQLite database, performing SQL analysis, and validating results using pandas.
- **Part B – Customer Segmentation and Lapse Prediction:** Building RFM features, clustering customers, identifying lapsed customers, comparing classification models, and generating a retention list.
- **Part C – Ticket Classification and Support Triage:** Applying input guardrails, PII redaction, resilient model calls, answer validation, zero-shot and few-shot classification, token-budget handling, and support routing.
- **Part D – Policy RAG Assistant and Refund Agent:** Chunking policy documents, retrieving relevant information using TF-IDF, evaluating RAG responses, implementing refund tools, and building a ReAct agent with safe stopping and checkpoint recovery.

The project uses Python 3.13.6 and a local SQLite database. The supplied `mock_llm.py` provides offline model responses, allowing the workflows to be tested without depending on an external LLM API.

# Reproduce

The following instructions describe how to reproduce the project from a clean clone of the `main` branch.

Run the commands from the repository root. The commands below use Windows PowerShell.

## 1. Clone the repository

```powershell
git clone https://github.com/Darathy-Jennelyn/instamart_capstone.git
cd instamart_capstone
```

## 2. Create and activate the virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, use the following command for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Generate the raw data

```powershell
python generate_data.py
```

This generates the raw customer, product, order, ticket, policy-evaluation, and agent-scenario data used throughout the project.

## 5. Run Part A – Data Engineering and SQL

Audit the generated raw data:

```powershell
python audit_raw_data.py
```

Clean customer data:

```powershell
python clean_customers.py
```

Clean order and product data:

```powershell
python clean_orders.py
```

Validate the cleaned data:

```powershell
python validate_clean_data.py
```

Create the SQLite database:

```powershell
python create_database.py
```

Validate the database:

```powershell
python validate_database.py
```

Execute the SQL queries:

```powershell
python run_sql_queries.py
```

Perform the pandas analysis:

```powershell
python pandas_analysis.py
```

## 6. Run Part B – Customer Segmentation and Lapse Prediction

Run customer segmentation:

```powershell
python customer_segmentation.py
```

Prepare lapse prediction features and processed datasets:

```powershell
python lapse_prediction.py
```

Train and compare classification models:

```powershell
python b6_model_training.py
```

Evaluate oversampling:

```powershell
python b7_oversampling.py
```

Interpret the model and generate the retention list:

```powershell
python b8_model_interpretation.py
```

## 7. Run Part C – Ticket Classification and Support Triage

Run the complete ticket classification and support triage workflow:

```powershell
python part_c.py
```

This executes the input guardrails, PII redaction, prompt-based classification, resilient calls, answer validation, model comparison, token-budget demonstration, and final support routing.

## 8. Run Part D – Policy RAG Assistant and Refund Agent

Chunk the policy documents:

```powershell
python d1_policy_chunking.py
```

Run TF-IDF retrieval:

```powershell
python d2_tfidf_retrieval.py
```

Run the RAG assistant:

```powershell
python d3_rag_assistant.py
```

Run the chunk-boundary inspection:

```powershell
python d4_boundary_check.py
```

Evaluate normal-overlap and zero-overlap retrieval:

```powershell
python d4_evaluation.py
```

The refund tools are implemented in `d5_refund_tools.py` and imported by the agent workflows. They do not need to be executed as a separate script.

Run the seven ReAct scenarios:

```powershell
python d6_react_agent.py
```

Run the safe-stopping demonstrations:

```powershell
python d7_safe_stopping.py
```

Run the checkpoint and resume demonstration:

```powershell
python d8_checkpoint_resume.py
```

**Important:** The D6 and D8 workflows can issue refunds and write entries to `outputs/refund_ledger.jsonl`. The D8 demonstration also uses checkpoint state. The committed output files contain the results used in this submission. Do not rerun an already completed refund demonstration merely to inspect its output, as doing so may change the local ledger or state.

## 9. Verify the required outputs

After running the relevant workflows, confirm that the required files exist:

```powershell
Test-Path data/clean/customers.csv
Test-Path data/clean/products.csv
Test-Path data/clean/orders.csv
Test-Path data/instamart.db
Test-Path outputs/customer_segments.csv
Test-Path outputs/lapse_model.joblib
Test-Path outputs/retention_list.csv
Test-Path outputs/triage_results.csv
Test-Path outputs/triage_budget_demo.csv
Test-Path outputs/agent_runs.jsonl
Test-Path outputs/refund_ledger.jsonl
Test-Path state
```

The expected result for each path is `True`.

# Part A

## A1 – Data Generation

The supplied `generate_data.py` script generated the raw datasets used in the project.

| Dataset | Records |
|---|---:|
| Customers | 1,200 |
| Products | 40 |
| Raw orders | 13,084 |
| Support tickets | 164 |

The generated data includes customer, product, order, ticket, policy-evaluation, and agent-scenario records.

## A2 – Raw Data Audit

The raw datasets were inspected to identify missing values, invalid values, duplicate records, and inconsistent categories.

### Raw order issues

| Issue | Count |
|---|---:|
| Exact duplicate orders | 119 |
| Pending orders | 656 |
| Nonnumeric order amounts | 120 |
| Negative delivery times | 106 |
| Blank delivery times | 2,541 |
| Distinct order IDs | 12,309 |

### Raw customer issues

| Issue | Count |
|---|---:|
| Missing ages | 61 |
| Ages outside the 10–100 range | 6 |
| Distinct city spellings | 24 |
| Distinct nonblank gender values | 10 |
| Blank genders | 30 |

**Script:** `audit_raw_data.py`

## A3 – Customer Data Cleaning

Customer data was cleaned by handling missing and invalid values and standardizing city and gender categories.

### Final customer distribution

| City | Customers |
|---|---:|
| Bengaluru | 197 |
| Chennai | 191 |
| Delhi | 210 |
| Hyderabad | 191 |
| Mumbai | 184 |
| Pune | 227 |
| **Total** | **1,200** |

### Gender distribution

| Gender | Customers |
|---|---:|
| Female | 610 |
| Male | 560 |
| Unknown | 30 |
| **Total** | **1,200** |

Final customer data validation:

- Missing ages: 0
- Minimum age: 18
- Maximum age: 60

The cleaned customer dataset was saved to `data/clean/customers.csv`.

**Output:** `data/clean/customers.csv`

**Script:** `clean_customers.py`

## A4 – Order and Product Data Cleaning

Order data was cleaned by removing duplicate and invalid records, handling pending orders, correcting data types, and applying the required delivery-time rules.

### Final order distribution

| Metric | Count |
|---|---:|
| Cleaned orders | 12,309 |
| Completed orders | 11,110 |
| Cancelled orders | 1,199 |
| Pending orders | 0 |
| Missing order amounts | 0 |
| Missing delivery times for completed orders | 0 |
| Missing delivery times for cancelled orders | 1,199 |

The final completed-order revenue was **₹29,98,668.80**.

Cleaned datasets were saved to:

- `data/clean/orders.csv`
- `data/clean/products.csv`
**Script:** `clean_orders.py`

## A5 – SQLite Database Creation

A SQLite database was created using the cleaned datasets.

Database location: `data/instamart.db`
**Script:** `create_database.py`

| Table | Records |
|---|---:|
| customers | 1,200 |
| products | 40 |
| orders | 12,309 |

The database contains the three required tables: `customers`, `products`, and `orders`.

## A6 – SQL Analysis

Seven SQL queries were written in `sql/queries.sql` and executed using `run_sql_queries.py`.

| Query | Result |
|---|---|
| Q1 | 30 customers |
| Q2 | 30 rows; total revenue ₹29,98,668.80 |
| Q3 | 11 products |
| Q4 | 25 customers |
| Q5 | 550 customers above the average spend of ₹2,552.06 |
| Q6 | 1,175 customers; 8 rows where RANK differs from ROW_NUMBER |
| Q7 | 183 days; cumulative revenue ₹29,98,668.80 |

The queries cover customer spending, product performance, ranking, and cumulative revenue analysis.

## A7 – Pandas Analysis and Cross-Validation

Pandas was used to independently validate the revenue calculation and perform descriptive statistical analysis.

The completed-order revenue calculated using pandas matched the SQL result:

**₹29,98,668.80**

### Order amount statistics

| Metric | Value |
|---|---:|
| Mean | ₹269.91 |
| Median | ₹135.00 |
| Skewness | 4.61 |
| First quartile (Q1) | ₹64.80 |
| Third quartile (Q3) | ₹297.00 |
| Interquartile range (IQR) | ₹232.20 |
| Lower outlier fence | -₹283.50 |
| Upper outlier fence | ₹645.30 |
| Outliers above upper fence | 897 |

The strongest absolute correlation identified was between `order_amount` and `discount_pct`, with a correlation of **-0.095**.

### Revenue by city

| City | Revenue (₹) | Average order amount (₹) | Orders |
|---|---:|---:|---:|
| Bengaluru | 523,643.40 | 276.47 | 1,894 |
| Chennai | 463,629.15 | 272.72 | 1,700 |
| Delhi | 502,829.80 | 243.62 | 2,064 |
| Hyderabad | 528,589.90 | 284.95 | 1,855 |
| Mumbai | 479,058.50 | 297.00 | 1,613 |
| Pune | 500,918.05 | 252.48 | 1,984 |

**Script:** `pandas_analysis.py`

## A8 – Final Data Validation

The cleaned datasets and database were checked against the expected conditions.

Validation checks included:

- Required customer, product, and order records.
- No missing order amounts.
- No missing delivery times for completed orders.
- Missing delivery times for all 1,199 cancelled orders.
- Completed-order revenue matching ₹29,98,668.80.

Final validation output:

```text
ALL CHECKPOINTS PASSED
```
**Scripts:**

- `validate_clean_data.py`
- `validate_database.py`

# Part B

## B1 – RFM Analysis

RFM features were calculated using completed orders and a snapshot date of **2025-10-01**.

| Metric | Result |
|---|---:|
| Customers | 1,175 |
| Median recency | 19 days |
| Minimum recency | 0 days |
| Maximum recency | 180 days |
| Mean frequency | 9.46 |
| Maximum frequency | 33 |
| Mean monetary value | ₹2,552.06 |
| Maximum monetary value | ₹14,766.55 |

The RFM dataset provides recency, frequency, and monetary features for customer segmentation.

**Script:** `customer_segmentation.py`

## B2 – Customer Clustering

K-Means clustering was evaluated for values of K from 2 to 8.

The features were standardized using `StandardScaler`. The clustering configuration used `n_init=10` and `random_state=42`.

| K | Inertia | Silhouette score |
|---:|---:|---:|
| 2 | 1820.761 | 0.465 |
| 3 | 1268.235 | 0.445 |
| 4 | 743.071 | 0.526 |
| 5 | 617.367 | 0.480 |
| 6 | 503.171 | 0.482 |
| 7 | 408.460 | 0.416 |
| 8 | 366.503 | 0.412 |

**K=4 was selected**, as it produced the highest silhouette score of 0.526 among the tested configurations.


## B3 – Customer Segment Profiling

The four customer segments were profiled using recency, frequency, and monetary value.

| Segment | Customers | Average recency | Average frequency | Average monetary value |
|---|---:|---:|---:|---:|
| Regular | 436 | 28.86 | 3.77 | ₹1,057.62 |
| High-Value | 138 | 24.12 | 6.77 | ₹7,129.70 |
| Frequent | 419 | 8.77 | 19.40 | ₹3,410.02 |
| At-Risk | 182 | 109.04 | 2.20 | ₹685.99 |

The High-Value segment was identified as the premium customer segment (Segment 1).

### PCA analysis

| Component | Explained variance |
|---|---:|
| PC1 | 63.4% |
| PC2 | 21.8% |
| **Combined** | **85.2%** |

The first two principal components explain 85.2% of the variance in the standardized RFM features.

The segment assignments were saved in `outputs/customer_segments.csv`.

**Script:** `customer_segmentation.py

## B4 – Lapse Cohort and Baseline

The lapse cohort was created using **2025-09-01** as the cutoff date.

| Metric | Result |
|---|---:|
| Previously active customers | 1,156 |
| Lapsed customers | 443 |
| Not-lapsed customers | 713 |
| Lapse rate | 38.32% |
| Features | 11 |
| Training records | 924 |
| Testing records | 232 |
| Baseline accuracy | 61.64% |
| Baseline lapsed-class F1 score | 0 |

The feature set was designed to avoid direct target leakage from future activity.

## B5 – Feature Preprocessing

The lapse prediction dataset contained:

- 11 input features.
- 8 numeric features.
- 3 categorical features.
- 19 transformed features after preprocessing.
- 924 training records.
- 232 testing records.
- No missing values in the processed training or testing datasets.

The preprocessing pipeline used numerical scaling and categorical encoding.

Processed files:

- `outputs/X_train_processed.csv`
- `outputs/X_test_processed.csv`

**Script:** `lapse_prediction.py`

## B6 – Model Training and Comparison

Logistic Regression and Random Forest were compared using five-fold cross-validation.

### Cross-validation results

| Model | Configuration | CV F1 score |
|---|---|---:|
| Logistic Regression | C=0.1, class_weight=balanced | 0.7014 |
| Random Forest | 200 estimators, max_depth=10, class_weight=balanced | 0.6920 |

### Test-set results

| Model | Accuracy | Precision | Recall | F1 score |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.7284 | 0.5915 | 0.9438 | 0.7273 |
| Random Forest | 0.7284 | 0.6048 | 0.8427 | 0.7042 |

Logistic Regression was selected based on its higher test F1 score and cross-validation performance.

The comparison was saved to `outputs/b6_model_comparison.csv`.

**Script:** `b6_model_training.py`

## B7 – Oversampling

Random oversampling was applied to the training dataset only.

### Class distribution

| Dataset | Not lapsed | Lapsed | Total |
|---|---:|---:|---:|
| Before oversampling | 570 | 354 | 924 |
| After oversampling | 570 | 570 | 1,140 |

The test dataset remained unchanged at 232 records.

### Model comparison

| Model | Accuracy | Precision | Recall | F1 score |
|---|---:|---:|---:|---:|
| Original Logistic Regression | 0.7629 | 0.6545 | 0.8090 | 0.7236 |
| Oversampled Logistic Regression | 0.7198 | 0.5870 | 0.9101 | 0.7137 |

Oversampling increased recall but reduced precision and the overall F1 score in this experiment.

The comparison was saved to `outputs/b7_model_comparison.csv`.

**Script:** `b7_oversampling.py`

## B8 – Model Interpretation and Retention List

The Logistic Regression model was interpreted using its feature coefficients.

### Top 10 feature coefficients

| Feature | Coefficient |
|---|---:|
| frequency | -1.2862 |
| Electronics | -0.3421 |
| Snacks | -0.2065 |
| Delhi | -0.1850 |
| Grocery | -0.1814 |
| Pune | 0.1203 |
| gender_male | -0.1050 |
| Hyderabad | -0.1042 |
| cancellation_rate | -0.1041 |
| Personal Care | 0.0949 |

The trained model was saved to `outputs/lapse_model.joblib`.

**Script:** `b8_model_interpretation.py`

Prediction consistency was verified, with matching predictions between the saved and reconstructed model workflows.

### Premium customer retention list

The top 10 premium customers were selected using predicted lapse probabilities.

- Number of customers in the retention list: 10
- Predicted lapse probabilities: approximately 56.54%–67.87%
- Customers who actually lapsed: 2
- Customers who did not lapse: 8

The list was saved to `outputs/retention_list.csv`.

This list is illustrative. The premium segment was selected using a wider observation period, which may introduce future-information leakage into the selection. It should not be interpreted as a fully independent prospective retention evaluation.

# Part C

## C1 – Input Guardrails

Input guardrails were applied before sending support tickets to the model.

The maximum allowed estimated input length was **400 tokens**.

| Status | Tickets |
|---|---:|
| Eligible | 156 |
| Skipped empty | 4 |
| Flagged long | 4 |
| **Total** | **164** |

The four long tickets had an estimated length of 734 tokens each.

Output: `outputs/c1_input_guardrails.csv`

## C2 – PII Redaction

Personally identifiable information was detected and redacted before model processing.

| PII type | Redactions |
|---|---:|
| Email addresses | 55 |
| Phone numbers | 91 |
| Order IDs | 132 |
| **Total** | **278** |

The redaction verification confirmed that no detected PII remained in the processed ticket text.

Output: `outputs/c2_pii_redaction.csv`

## C3 – Classification Prompts

Zero-shot and few-shot prompts were developed for four ticket categories:

- Billing
- Delivery
- Technical
- Fraud

The few-shot prompt included four labelled examples to guide classification.

## C4 – Resilient Model Calls

A retry mechanism was implemented to handle transient model-call failures.

Configuration and results:

| Metric | Result |
|---|---:|
| Maximum retries after initial attempt | 3 |
| Base delay | 0.05 seconds |
| Successful tickets | 156 |
| Failed tickets | 0 |
| Transient errors | 19 |
| Recovered transient errors | 19 |

Exponential backoff with jitter was used to reduce repeated immediate requests.

Output: `outputs/c4_resilient_calls.csv`

## C5 – Output Validation

Model responses were validated to ensure that classification outputs followed the expected structure.

| Status | Tickets |
|---|---:|
| Classified using JSON output | 135 |
| Classified using keyword fallback | 12 |
| Flagged invalid output | 9 |
| **Total** | **156** |

A total of 147 tickets were successfully classified, while 9 were flagged for invalid output.

Output: `outputs/c5_validated_answers.csv`

## C6 – Zero-Shot and Few-Shot Comparison

Zero-shot and few-shot classification were compared using the 156 eligible tickets.

| Metric | Zero-shot | Few-shot |
|---|---:|---:|
| Eligible tickets | 156 | 156 |
| Classified tickets | 147 | 147 |
| Correct classifications | 126 | 147 |
| Accuracy | 85.7% | 100% |
| Total tokens | 16,888 | 32,800 |
| Average tokens per classified ticket | 114.88 | 223.13 |

Few-shot classification achieved 100% accuracy on the classified tickets in this evaluation, compared with 85.7% for zero-shot classification. It used approximately 94% more tokens.

### Zero-shot confusion matrix

| Actual category | Billing | Delivery | Fraud | Technical |
|---|---:|---:|---:|---:|
| Billing | 38 | 0 | 0 | 0 |
| Delivery | 0 | 36 | 0 | 0 |
| Fraud | 11 | 0 | 23 | 0 |
| Technical | 10 | 0 | 0 | 29 |

Outputs:

- `outputs/c6_model_comparison.csv`
- `outputs/c6_zero_shot_confusion.csv`
- `outputs/c6_zero_shot_results.csv`
- `outputs/c6_few_shot_results.csv`

## C7 – Token Budget and Support Routing

A token-budget demonstration was performed with a budget of 6,000 tokens.

| Metric | Result |
|---|---:|
| Token budget | 6,000 |
| Tokens used | 6,062 |
| Budget exhausted | Yes |

The final ticket-processing workflow used a 100,000-token budget.

### Final ticket statuses

| Status | Tickets |
|---|---:|
| Classified JSON | 135 |
| Classified keyword | 12 |
| Invalid output | 9 |
| Skipped empty | 4 |
| Flagged long | 4 |
| **Total** | **164** |

Total tokens used: **32,800**.

### Support routing distribution

| Route | Tickets |
|---|---:|
| support_queue | 102 |
| security_team | 34 |
| human_review | 17 |
| premium_desk | 11 |
| **Total** | **164** |

All 164 tickets were included in the final triage output.

Outputs:

- `outputs/triage_budget_demo.csv`
- `outputs/triage_results.csv`

# Part D

## D1 – Policy Document Chunking

Five policy documents were processed and divided into smaller text chunks.

| Setting | Value |
|---|---:|
| Number of policy documents | 5 |
| Chunk size | 40 words |
| Overlap | 10 words |
| Total chunks | 15 |

The chunks were saved to `outputs/d1_policy_chunks.csv`.

**Script:** `d1_policy_chunking.py`

## D2 – TF-IDF Retrieval

TF-IDF vectorization and cosine similarity were used to retrieve relevant policy chunks.

Test query:

`refund policy late delivery`

### Top retrieval results

| Rank | Source | Similarity score |
|---:|---|---:|
| 1 | refund_policy.txt | 0.2719 |
| 2 | refund_policy.txt | 0.2514 |
| 3 | refund_policy.txt | 0.2454 |

All three retrieved results came from `refund_policy.txt`.

The retrieval function was implemented as `retrieve(query, k=3)`.

**Script:** `d2_tfidf_retrieval.py`

## D3 – Policy RAG Assistant

The RAG assistant combines policy retrieval with the supplied offline `mock_llm` model.

The `answer(question)` function:

1. Accepts a user question.
2. Retrieves the top three relevant policy chunks.
3. Passes the retrieved context to the mock language model.
4. Returns the generated answer and the sources used.

The assistant was tested with the question:

`What is the refund policy for late delivery?`

The returned response includes its supporting policy sources.

**Script:** `d3_rag_assistant.py`

## D4 – Chunk Boundary Evaluation

The retrieval and answer-generation workflow was evaluated using normal overlapping chunks and zero-overlap chunks.

### Evaluation results

| Evaluation | Normal overlap | Zero overlap |
|---|---:|---:|
| Total chunks | 15 | 13 |
| Document retrieval | 12/12 | 12/12 |
| Fact retrieval | 12/12 | 10/12 |
| Fallback cases | 2/2 | 2/2 |

With normal overlap, all 12 document and fact checks passed.

With zero overlap, document retrieval remained 12/12, but fact retrieval dropped to 10/12. Two fact misses occurred because sentence boundaries caused relevant information to be split across chunks.

This demonstrates the importance of chunk overlap when retrieving policy information.

Outputs:

- `outputs/d4_normal_evaluation.csv`
- `outputs/d4_zero_overlap_chunks.csv`
- `outputs/d4_zero_overlap_evaluation.csv`

**Scripts:**

- `d4_boundary_check.py`
- `d4_evaluation.py`

## D5 – Refund Tools

Five tools were implemented to support the refund workflow.

| Tool | Purpose |
|---|---|
| `get_order` | Retrieves order information |
| `search_policy` | Retrieves relevant policy information |
| `calculate_refund` | Calculates the eligible refund amount |
| `issue_refund` | Records an approved refund |
| `escalate_to_human` | Escalates cases requiring human review |

The tool specifications are maintained in `TOOLS_SPEC`, and the corresponding Python functions are mapped through `TOOL_MAP`.

Refund records are stored in `outputs/refund_ledger.jsonl`.

**Script:** `d5_refund_tools.py`

## D6 – ReAct Refund Agent

A ReAct agent was implemented to reason through customer refund requests and execute the required tools based on their responses.

Seven scenarios were tested.

### Seven-scenario results

| Scenario | Expected outcome | Actual outcome | LLM calls | Tokens | Tools executed |
|---|---|---|---:|---:|---:|
| S1 | REFUND | REFUND | 5 | 1,300 | 4 |
| S2 | REFUND | REFUND | 5 | 1,300 | 4 |
| S3 | ESCALATE | ESCALATE | 5 | 1,287 | 4 |
| S4 | DENIED | DENIED | 4 | 932 | 3 |
| S5 | DENIED | DENIED | 3 | 591 | 2 |
| S6 | NOT_FOUND | NOT_FOUND | 2 | 263 | 1 |
| S7 | FALLBACK | FALLBACK | 6 | 3,285 | 6 |

All seven scenarios produced their expected outcomes.

### Refund and escalation results

| Scenario | Result | Amount |
|---|---|---:|
| S1 | REFUND | ₹128.25 |
| S2 | REFUND | ₹135.00 |
| S3 | ESCALATE | ₹1,999.00 |

The agent uses the order status, relevant policy, and tool results to decide whether a refund is allowed, denied, or escalated.

Output: `outputs/agent_runs.jsonl`

**Script:** `d6_react_agent.py`

## D7 – Safe Stopping

Safe-stopping controls were implemented to prevent the agent from continuing indefinitely or exceeding execution limits.

The implementation includes:

- Maximum iteration limits.
- Token limits.
- Execution timeout.
- Fallback handling when a limit is reached.

The token count uses `response.usage.total_tokens`, and timeout handling uses `time.monotonic()`.

### Safe-stopping demonstrations

| Demonstration | Configuration | Final status | LLM calls | Tokens | Tools executed |
|---|---|---|---:|---:|---:|
| S1 token limit | 200-token limit | FALLBACK_TOKEN_LIMIT | 2 | 286 | 1 |
| S1 timeout | 0-second timeout | FALLBACK_TIMEOUT | 0 | 0 | 0 |
| S7 maximum iterations | 6 iterations | FALLBACK_MAX_ITERATIONS | 6 | 3,285 | 6 |

For the token-limit demonstration, the agent stopped before executing the pending policy-search tool. The timeout demonstration stopped before making a model call. The maximum-iteration demonstration returned a fallback after reaching the configured limit.

Output: `outputs/d7_safety_tests.jsonl`

**Script:** `d7_safe_stopping.py`

## D8 – Checkpoint and Resume

Checkpoint functionality was implemented to allow an agent workflow to recover after an interruption.

The implementation includes:

- `get_checkpoint_path`
- `save_checkpoint`
- `load_checkpoint`
- `run_agent`
- `continue_agent`
- `resume_agent`
- `run_checkpoint_demo`

### Crash-and-resume demonstration

Scenario S1 was interrupted after the initial order and policy checks.

The tools executed in order were:

1. `get_order`
2. `search_policy`
3. Simulated crash
4. Resume execution
5. `calculate_refund`
6. `issue_refund`

The workflow resumed from its saved checkpoint rather than repeating the completed tool executions.

### Final result

| Metric | Result |
|---|---:|
| Final status | REFUND |
| Refund amount | ₹128.25 |
| Model calls | 5 |
| Tokens used | 1,300 |
| Tools executed | 4 |
| Final step number | 4 |
| Duplicate tool executions | 0 |

The checkpoint and final result were saved in:

- `state/D8_S1_DEMO.json`
- `outputs/d8_checkpoint_results.json`

The demonstration completed successfully without duplicate tool execution.

**Script:** `d8_checkpoint_resume.py`

## D9 – ReAct vs Plan-and-Execute

The ReAct and Plan-and-Execute approaches were compared conceptually for the refund workflow.

ReAct makes decisions step by step using the latest tool results. In the tested scenarios, S1 used 5 model calls and 1,300 tokens, S5 used 3 calls and 591 tokens, and S6 used 2 calls and 263 tokens.

Plan-and-Execute would first generate a plan and then execute its steps, requiring replanning if an error or unexpected result occurred. Exact Plan-and-Execute token and call counts were not benchmarked.

For this refund workflow, ReAct is preferable because decisions depend on actual order status, policy retrieval, and tool responses. It can respond directly to outcomes such as cancelled orders or missing order IDs rather than continuing with an outdated plan.

# Limitations and Next Steps

## Limitations

1. **Synthetic dataset:** The project uses generated data. Results may differ when applied to real customer and transaction data.
2. **Offline mock language model:** The supplied `mock_llm.py` enables reproducible testing but does not represent the full capabilities or variability of a production LLM.
3. **TF-IDF retrieval:** Retrieval is based on lexical similarity. It may not identify semantically related information when the wording differs significantly.
4. **Chunk boundaries:** The zero-overlap evaluation showed that splitting relevant facts across chunks can reduce retrieval accuracy.
5. **Lapse prediction:** Model performance is evaluated on the available synthetic cohort and should not be assumed to generalize to real customers.
6. **Retention-list selection:** The premium customer selection uses a wider observation period and may introduce future-information leakage. The resulting list is illustrative.
7. **Few-shot token usage:** Few-shot classification improved the measured accuracy in this evaluation but required approximately 94% more tokens than zero-shot classification.
8. **Plan-and-Execute comparison:** The comparison is qualitative. No separate Plan-and-Execute implementation or quantitative benchmark was completed.
9. **Refund execution:** Refund tools and the ledger are local demonstrations. They are not connected to a live payment gateway or production order-management system.
10. **Local execution:** The project uses local files and a SQLite database. It does not include production deployment, distributed execution, or a live monitoring interface.

## Next Steps

- Evaluate the workflows using real or more representative customer and transaction datasets.
- Improve lapse prediction through additional feature engineering, time-based validation, and testing on independent data.
- Explore semantic retrieval and alternative chunking strategies to improve policy search.
- Evaluate the RAG assistant using a larger set of questions and policy-grounded answer checks.
- Integrate a production LLM through a controlled API while retaining input validation, PII redaction, retry handling, and token-budget controls.
- Add audit logging, role-based access, and approval controls before connecting refund tools to live systems.
- Deploy the workflows through an API or support dashboard and monitor model quality, response time, and operational performance.