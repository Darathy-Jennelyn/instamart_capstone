
import pandas as pd
import re
from mock_llm import est_tokens
import time
import random
import mock_llm
import json

# --------------------------------
# C1 - INPUT GUARDRAILS
# --------------------------------

MAX_INPUT_TOKENS = 400

# Read the original ticket data
df = pd.read_csv("data/raw/tickets.csv", keep_default_na=False)

# Estimate tokens for each ticket
df["estimated_tokens"] = df["text"].apply(est_tokens)

# Initially mark all tickets as eligible
df["status"] = "eligible"

# Check each ticket
for i, row in df.iterrows():

    if row["text"].strip() == "":
        df.loc[i, "status"] = "skipped_empty"

    elif row["estimated_tokens"] > MAX_INPUT_TOKENS:
        df.loc[i, "status"] = "flagged_long"


# Display C1 results
print("C1 - INPUT GUARDRAIL RESULTS")
print("----------------------------")

print("Total tickets:", len(df))
print("\nStatus counts:")
print(df["status"].value_counts())

print("\nTickets not eligible for model calls:")
print(
    df[df["status"] != "eligible"][
        ["ticket_id", "estimated_tokens", "status"]
    ].to_string(index=False)
)


# Save C1 output separately
df.to_csv("outputs/c1_input_guardrails.csv", index=False)

print("\nSaved: outputs/c1_input_guardrails.csv")


# --------------------------------
# C2 - PII REDACTION
# --------------------------------

# Required regular expressions
email_pattern = r"[\w.+-]+@[\w-]+\.[\w.]+"
phone_pattern = r"\b[6-9]\d{9}\b"
order_pattern = r"ORD-\d{6}"

# Counters for each PII type
email_count = 0
phone_count = 0
order_count = 0

# Store the redacted ticket text
redacted_texts = []

for text in df["text"]:

    # 1. Redact email addresses
    text, count = re.subn(email_pattern, "[EMAIL]", text)
    email_count += count

    # 2. Redact phone numbers
    text, count = re.subn(phone_pattern, "[PHONE]", text)
    phone_count += count

    # 3. Redact order IDs
    text, count = re.subn(order_pattern, "[ORDER_ID]", text)
    order_count += count

    redacted_texts.append(text)

# Add the redacted text as a separate column
df["redacted_text"] = redacted_texts


# Calculate total substitutions
total_redactions = email_count + phone_count + order_count


# --------------------------------
# C2 - VERIFY PII REMOVAL
# --------------------------------

remaining_emails = 0
remaining_phones = 0
remaining_orders = 0

for text in df["redacted_text"]:

    remaining_emails += len(re.findall(email_pattern, text))
    remaining_phones += len(re.findall(phone_pattern, text))
    remaining_orders += len(re.findall(order_pattern, text))


# Display C2 results
print("\nC2 - PII REDACTION RESULTS")
print("--------------------------")

print("Emails redacted:", email_count)
print("Phone numbers redacted:", phone_count)
print("Order IDs redacted:", order_count)
print("Total redactions:", total_redactions)

print("\nRemaining PII after redaction:")
print("Emails:", remaining_emails)
print("Phone numbers:", remaining_phones)
print("Order IDs:", remaining_orders)


# Save C2 output separately
df.to_csv("outputs/c2_pii_redaction.csv", index=False)

print("\nSaved: outputs/c2_pii_redaction.csv")

# ==============================
# C3 - TWO PROMPTS
# ==============================

# Zero-shot prompt
zero_shot_prompt = """
CLASSIFY the customer support ticket into exactly one of these categories:

1. billing - Payment, refund, charges or invoice-related issues.
2. delivery - Order delays, missing orders or delivery-related issues.
3. technical - App errors, login problems or technical issues.
4. fraud - Suspicious transactions, unauthorized orders or fraudulent activity.

Return JSON only in the following format:
{"category": "...", "reason": "..."}
"""


# Few-shot prompt
few_shot_prompt = """
CLASSIFY the customer support ticket into exactly one of these categories:

1. billing - Payment, refund, charges or invoice-related issues.
2. delivery - Order delays, missing orders or delivery-related issues.
3. technical - App errors, login problems or technical issues.
4. fraud - Suspicious transactions, unauthorized orders or fraudulent activity.

EXAMPLES:

Ticket: I was charged twice for my order.
Output: {"category": "billing", "reason": "The customer was charged twice."}

Ticket: My order has not arrived even though the delivery date has passed.
Output: {"category": "delivery", "reason": "The order is delayed."}

Ticket: Someone placed an order using my account without my permission.
Output: {"category": "fraud", "reason": "The customer reports an unauthorized order."}

Ticket: The application keeps crashing whenever I try to open it.
Output: {"category": "technical", "reason": "The application is crashing."}

Return JSON only in the following format:
{"category": "...", "reason": "..."}
"""


print("\nC3 - PROMPT VERIFICATION")
print("------------------------")

print("Zero-shot prompt created:", bool(zero_shot_prompt))
print("Few-shot prompt created:", bool(few_shot_prompt))

print("Zero-shot contains EXAMPLES:", "EXAMPLES:" in zero_shot_prompt)
print("Few-shot contains EXAMPLES:", "EXAMPLES:" in few_shot_prompt)

print("\nC3 - DETAILED PROMPT CHECKS")
print("---------------------------")

for name, prompt in [
    ("Zero-shot", zero_shot_prompt),
    ("Few-shot", few_shot_prompt)
]:
    print(f"\n{name}:")
    print("CLASSIFY:", "CLASSIFY" in prompt)

    print("All categories:", all(
        category in prompt
        for category in ["billing", "delivery", "technical", "fraud"]
    ))

    print("JSON format:",
          '{"category": "...", "reason": "..."}' in prompt)

    if name == "Zero-shot":
        print("No EXAMPLES:", "EXAMPLES:" not in prompt)
    else:
        print("Has EXAMPLES:", "EXAMPLES:" in prompt)

# ==============================
# C4 - RESILIENT CALLS
# ==============================

BASE_DELAY = 0.05
MAX_RETRIES = 3

retry_count = 0


def call_with_retry(ticket_id, messages):

    prompt_text = messages[-1]["content"]

    # Check that the prompt is not empty
    assert prompt_text.strip() != ""

    # Check that no PII is present in the prompt
    assert re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", prompt_text) is None
    assert re.search(r"\b[6-9]\d{9}\b", prompt_text) is None
    assert re.search(r"ORD-\d{6}", prompt_text) is None

    global retry_count

    retries_used = 0

    for n in range(MAX_RETRIES + 1):

        try:
            response = mock_llm.chat(messages)
            return response, retries_used

        except mock_llm.TransientLLMError:

            retry_count += 1
            retries_used += 1

            if n == MAX_RETRIES:
                print(f"{ticket_id} - Failed after 3 retries")
                raise

            wait_time = BASE_DELAY * (2 ** n) * random.uniform(0.9, 1.15)

            print(
                f"Retry - Ticket: {ticket_id}, "
                f"Retry number: {n}, "
                f"Wait time: {wait_time:.4f} seconds"
            )

            time.sleep(wait_time)


# ==============================
# C4 - PROCESS ELIGIBLE TICKETS
# ==============================

c4_results = []

failed_tickets = 0
retry_count = 0

print("\nC4 - RESILIENT CALL RESULTS")
print("---------------------------")

# Reset immediately before the complete run
mock_llm.reset()

for _, row in df.iterrows():

    # Do not send empty or long tickets to the model
    if row["status"] != "eligible":
        continue

    ticket_id = row["ticket_id"]

    messages = [
        {"role": "system", "content": zero_shot_prompt},
        {"role": "user", "content": row["redacted_text"]}
    ]

    try:
        assert row["status"] == "eligible"
        response, retries_used = call_with_retry(ticket_id, messages)

        c4_results.append({
            "ticket_id": ticket_id,
            "status": "success",
            "response": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "retries_used": retries_used
        })

    except mock_llm.TransientLLMError:

        failed_tickets += 1

        c4_results.append({
            "ticket_id": ticket_id,
            "status": "failed",
            "response": "",
            "tokens_used": 0,
            "retries_used": MAX_RETRIES
        })


# Convert results into a DataFrame
c4_df = pd.DataFrame(c4_results)

# Display C4 results
print("Eligible tickets:", len(c4_df))
print("Successful tickets:", (c4_df["status"] == "success").sum())
print("Failed tickets:", failed_tickets)
print("Transient errors:", retry_count)
print("Recovered errors:", retry_count - failed_tickets)

# Save C4 results
c4_df.to_csv("outputs/c4_resilient_calls.csv", index=False)

print("\nSaved: outputs/c4_resilient_calls.csv")


# ==========================================
# C5 - VALIDATE ANSWERS
# ==========================================

print("\nC5 - VALIDATE ANSWERS")
print("----------------------")

# Allowed categories
allowed_categories = ["billing", "delivery", "technical", "fraud"]

# Function to validate each model response
def validate_response(response_text):

    category = None
    reason = None

    try:
        # Step 1: Try parsing response as JSON
        data = json.loads(response_text)

        # Get category and reason
        model_category = data.get("category")
        model_reason = data.get("reason")

        # Check whether category is allowed
        if model_category in allowed_categories:

            category = model_category
            reason = model_reason
            validation_status = "classified_json"

        else:
            validation_status = "flagged_invalid_output"

    except (json.JSONDecodeError, AttributeError, TypeError):

        # Step 2: Extract lowercase words
        words = re.findall(r"[a-z]+", response_text.lower())

        # Step 3: Find allowed category words
        found_categories = []

        for word in words:
            if word in allowed_categories:
                found_categories.append(word)

        # Step 4: Check whether exactly one category exists
        if len(found_categories) == 1:

            category = found_categories[0]
            reason = "Extracted using keyword matching"
            validation_status = "classified_keyword"

        else:
            validation_status = "flagged_invalid_output"

    return pd.Series({
        "category": category,
        "reason": reason,
        "validation_status": validation_status
    })


# Apply validation to C4 model responses
c5_df = c4_df.copy()

# Validate original model response
validation_results = c5_df["response"].apply(validate_response)

# Add validation columns
c5_df[["category", "reason", "validation_status"]] = validation_results


# ==========================================
# C5 - RESULTS
# ==========================================

print("\nValidation Status Counts")
print("------------------------")

print(c5_df["validation_status"].value_counts())

classified_json = (c5_df["validation_status"] == "classified_json").sum()

classified_keyword = (c5_df["validation_status"] == "classified_keyword").sum()

flagged_invalid = (c5_df["validation_status"] == "flagged_invalid_output").sum()

total_tickets = len(c5_df)

successfully_classified = classified_json + classified_keyword

print("\nC5 SUMMARY")
print("------------------------")

print("classified_json:", classified_json)
print("classified_keyword:", classified_keyword)
print("flagged_invalid_output:", flagged_invalid)
print("Total tickets:", total_tickets)
print("Successfully classified:", successfully_classified)


# Save results
c5_df.to_csv("outputs/c5_validated_answers.csv", index=False)

print("\nSaved: outputs/c5_validated_answers.csv")



# ==========================================
# C6 - COMPARE ZERO-SHOT AND FEW-SHOT
# ==========================================

print("\nC6 - COMPARE ZERO-SHOT AND FEW-SHOT")
print("------------------------------------")


# Function to run classification using a prompt
def run_prompt(prompt, prompt_name):

    results = []
    total_tokens = 0

    # Reset mock LLM before each experiment
    mock_llm.reset()

    # Select only eligible tickets
    eligible_tickets = df[df["status"] == "eligible"]

    for _, row in eligible_tickets.iterrows():

        ticket_id = row["ticket_id"]

        # Prepare messages using redacted ticket text
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": row["redacted_text"]}
        ]

        try:

            # Call model using C4 retry function
            # C4 returns two values
            assert row["status"] == "eligible"
            response, retries_used = call_with_retry(
                ticket_id, messages
            )

            # Extract model response
            response_text = response.choices[0].message.content

            # Get token usage
            tokens_used = response.usage.total_tokens
            total_tokens += tokens_used

            # Validate response using C5 function
            validation = validate_response(response_text)

            # Store results
            results.append({
                "ticket_id": ticket_id,
                "true_category": row["true_category"],
                "category": validation["category"],
                "validation_status": validation["validation_status"],
                "tokens_used": tokens_used
            })

        except mock_llm.TransientLLMError:

            # Record tickets that failed after all retries
            results.append({
                "ticket_id": ticket_id,
                "true_category": row["true_category"],
                "category": None,
                "validation_status": "failed",
                "tokens_used": 0
            })


    # Convert results into DataFrame
    results_df = pd.DataFrame(results)

    # Keep successfully classified tickets
    classified_df = results_df[
        results_df["validation_status"].isin(
            ["classified_json", "classified_keyword"]
        )
    ]

    # Calculate classification metrics
    classified_count = len(classified_df)

    correct_predictions = (
        classified_df["true_category"] ==
        classified_df["category"]
    ).sum()

    if classified_count > 0:

        accuracy = (
            correct_predictions / classified_count
        ) * 100

        tokens_per_ticket = (
            total_tokens / classified_count
        )

    else:

        accuracy = 0
        tokens_per_ticket = 0


    # Display experiment results
    print(f"\n{prompt_name} RESULTS")
    print("------------------------")

    print("Tickets classified:", classified_count)
    print("Correct predictions:", correct_predictions)
    print(f"Accuracy: {accuracy:.1f}%")
    print("Total tokens:", total_tokens)

    print(
        f"Tokens per classified ticket: "
        f"{tokens_per_ticket:.2f}"
    )

    return results_df, total_tokens


# ==========================================
# RUN ZERO-SHOT EXPERIMENT
# ==========================================

zero_shot_results, zero_shot_tokens = run_prompt(
    zero_shot_prompt,
    "ZERO-SHOT"
)


# ==========================================
# RUN FEW-SHOT EXPERIMENT
# ==========================================

few_shot_results, few_shot_tokens = run_prompt(
    few_shot_prompt,
    "FEW-SHOT"
)


# ==========================================
# MODEL COMPARISON TABLE
# ==========================================

def get_metrics(results_df, total_tokens):

    classified_df = results_df[
        results_df["validation_status"].isin(
            ["classified_json", "classified_keyword"]
        )
    ]

    classified_count = len(classified_df)

    correct = (
        classified_df["true_category"] ==
        classified_df["category"]
    ).sum()

    if classified_count > 0:

        accuracy = correct / classified_count * 100

        tokens_per_ticket = (
            total_tokens / classified_count
        )

    else:

        accuracy = 0
        tokens_per_ticket = 0

    return {
        "tickets_classified": classified_count,
        "correct_predictions": correct,
        "accuracy_pct": round(accuracy, 1),
        "total_tokens": total_tokens,
        "tokens_per_classified_ticket": round(
            tokens_per_ticket, 2
        )
    }


comparison_df = pd.DataFrame({
    "zero_shot": get_metrics(
        zero_shot_results, zero_shot_tokens
    ),

    "few_shot": get_metrics(
        few_shot_results, few_shot_tokens
    )

}).T


print("\nC6 MODEL COMPARISON")
print("-------------------")
print(comparison_df)


# ==========================================
# ZERO-SHOT CONFUSION TABLE
# ==========================================

zero_shot_classified = zero_shot_results[
    zero_shot_results["validation_status"].isin(
        ["classified_json", "classified_keyword"]
    )
]

confusion_table = pd.crosstab(
    zero_shot_classified["true_category"],
    zero_shot_classified["category"]
)


print("\nZERO-SHOT CONFUSION TABLE")
print("-------------------------")
print(confusion_table)


# ==========================================
# SAVE C6 OUTPUTS
# ==========================================

comparison_df.to_csv(
    "outputs/c6_model_comparison.csv"
)

confusion_table.to_csv(
    "outputs/c6_zero_shot_confusion.csv"
)

zero_shot_results.to_csv(
    "outputs/c6_zero_shot_results.csv",
    index=False
)

few_shot_results.to_csv(
    "outputs/c6_few_shot_results.csv",
    index=False
)


print("\nC6 OUTPUTS SAVED")
print("----------------")

print("outputs/c6_model_comparison.csv")
print("outputs/c6_zero_shot_confusion.csv")
print("outputs/c6_zero_shot_results.csv")
print("outputs/c6_few_shot_results.csv")



# C7.1 - TOKEN BUDGET DEMONSTRATION

def run_budget_demo(budget):

    mock_llm.reset()

    global retry_count
    retry_count = 0

    total_tokens = 0
    results = []

    for _, row in df.iterrows():

        ticket_id = row["ticket_id"]

        # Tickets that cannot be sent to the model
        if row["status"] != "eligible":
            results.append({
                "ticket_id": ticket_id,
                "status": row["status"],
                "category": "",
                "tokens_used": 0,
                "route": "human_review"
            })
            continue

        # Check the budget before making a model call
        if total_tokens >= budget:
            results.append({
                "ticket_id": ticket_id,
                "status": "budget_exhausted",
                "category": "",
                "tokens_used": 0,
                "route": "human_review"
            })
            continue

        messages = [
            {"role": "system", "content": zero_shot_prompt},
            {"role": "user", "content": row["redacted_text"]}
        ]

        try:
            assert row["status"] == "eligible"
            response, retries_used = call_with_retry(ticket_id, messages)

            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            total_tokens += tokens_used

            validation = validate_response(response_text)

            category = validation["category"]
            status = validation["validation_status"]

            if status == "flagged_invalid_output":
                route = "human_review"
            elif category == "fraud":
                route = "security_team"
            else:
                route = "support_queue"

            results.append({
                "ticket_id": ticket_id,
                "status": status,
                "category": category if pd.notna(category) else "",
                "tokens_used": tokens_used,
                "route": route
            })

        except mock_llm.TransientLLMError:
            results.append({
                "ticket_id": ticket_id,
                "status": "failed",
                "category": "",
                "tokens_used": 0,
                "route": "human_review"
            })

    result_df = pd.DataFrame(results)

    print("\nBudget:", budget)
    print("Total tickets:", len(result_df))
    print("Total tokens used:", total_tokens)
    print("Budget exhausted tickets:",
          (result_df["status"] == "budget_exhausted").sum())
    print("Human review tickets:",
          (result_df["route"] == "human_review").sum())

    return result_df


# First attempt: 6000 tokens
budget = 6000
budget_df = run_budget_demo(budget)

# Reduce the budget if no ticket was exhausted
if (budget_df["status"] == "budget_exhausted").sum() == 0:
    print("\nNo tickets exhausted at 6000. Reducing budget to 5000.")
    budget = 5000
    budget_df = run_budget_demo(budget)

# Save the final budget demonstration
budget_df.to_csv("outputs/triage_budget_demo.csv", index=False)

print("\nBudget demonstration saved successfully.")
print("\nStatus counts:")
print(budget_df["status"].value_counts())

print("\nSample results:")
print(budget_df.head(10).to_string(index=False))


# C7.2 - FINAL FEW-SHOT RUN AND CUSTOMER ROUTING

# Set token budget
budget = 100000
total_tokens = 0
failed_tickets = 0

# Reset mock model
mock_llm.reset()
retry_count = 0

# Read customer segments
customer_segments = pd.read_csv("outputs/customer_segments.csv")

# Add segment information to ticket data
ticket_df = df.merge(
    customer_segments[["customer_id", "segment_name", "is_premium"]],
    on="customer_id",
    how="left"
)

results = []

# Process each ticket
for _, row in ticket_df.iterrows():

    category = ""
    tokens_used = 0
    status = row["status"]

    # Call model only for eligible tickets
    if status == "eligible":

        if total_tokens < budget:

            messages = [
                {"role": "system", "content": few_shot_prompt},
                {"role": "user", "content": row["redacted_text"]}
            ]

            try:
                assert row["status"] == "eligible"
                response, retries_used = call_with_retry(
                    row["ticket_id"], messages
                )

                response_text = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                total_tokens = total_tokens + tokens_used

                validation = validate_response(response_text)

                category = validation["category"]
                status = validation["validation_status"]

                if pd.isna(category):
                    category = ""

            except mock_llm.TransientLLMError:
                status = "failed"
                failed_tickets = failed_tickets + 1

        else:
            status = "budget_exhausted"

    # Check premium customer
    is_premium = str(row["is_premium"]).lower() == "true"

    # Apply routing rules
    if status in [
        "skipped_empty",
        "flagged_long",
        "flagged_invalid_output",
        "budget_exhausted",
        "failed"
    ]:
        route = "human_review"
        priority = "NORMAL"

    elif category == "fraud":
        route = "security_team"
        priority = "HIGH"

    elif is_premium:
        route = "premium_desk"
        priority = "HIGH"

    else:
        route = "support_queue"
        priority = "NORMAL"

    # Store ticket result
    results.append([
        row["ticket_id"],
        row["customer_id"],
        status,
        category,
        row["segment_name"] if pd.notna(row["segment_name"]) else "",
        priority,
        route,
        tokens_used
    ])


# Create final DataFrame
final_df = pd.DataFrame(results, columns=[
    "ticket_id",
    "customer_id",
    "status",
    "category",
    "segment_name",
    "priority",
    "route",
    "tokens_used"
])

# Save final output
final_df.to_csv("outputs/triage_results.csv", index=False)


# Display results
print("\nC7 FINAL TRIAGE RESULTS")
print("-----------------------")

print("Total tickets:", len(final_df))
print("Total tokens used:", total_tokens)
print("Token budget:", budget)
print("Failed tickets:", failed_tickets)
print("Transient errors:", retry_count)
print("Recovered errors:", retry_count - failed_tickets)

print("\nStatus counts:")
print(final_df["status"].value_counts())

print("\nRouting counts:")
print(final_df["route"].value_counts())

print("\nPriority counts:")
print(final_df["priority"].value_counts())

print("\nFinal columns:")
print(final_df.columns.tolist())

print("\nSample results:")
print(final_df.head(10).to_string(index=False))

print("\nSaved: outputs/triage_results.csv")
