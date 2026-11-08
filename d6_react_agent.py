
import json
import os

from mock_llm import chat
from d5_refund_tools import TOOLS_SPEC, TOOL_MAP


# System prompt for the refund agent
AGENT = """
You are an Instamart customer support refund agent.

Follow the refund policy carefully.
Use the available tools to retrieve order details,
search the refund policy, calculate refunds,
issue eligible refunds, and escalate cases when required.

Never invent order details or refund amounts.
Do not issue refunds for cancelled orders.
If an order cannot be found, report NOT_FOUND.
If a refund is not eligible, report DENIED.
If a case requires human review, report ESCALATE.

Always provide the final answer in this format:

STATUS: Explanation
"""


def run_agent(
    user_message,
    scenario_id,
    max_iterations=6,
    token_limit=6000,
    time_limit_seconds=10
):

    # Start the conversation
    messages = [
        {"role": "system", "content": AGENT},
        {"role": "user", "content": user_message}
    ]

    steps = []
    llm_calls = 0
    tokens_used = 0
    final_answer = ""

    # ReAct loop
    for iteration in range(max_iterations):

        # Call the mock language model
        response = chat(messages, tools=TOOLS_SPEC)

        llm_calls += 1
        tokens_used += response.usage.total_tokens

        message = response.choices[0].message

        # Check whether the model requested a tool
        if not message.tool_calls:

            final_answer = message.content or ""

            break

        # Append the assistant tool-call message
        assistant_message = {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": []
        }

        for tool_call in message.tool_calls:

            assistant_message["tool_calls"].append({
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.name,
                    "arguments": json.dumps(tool_call.arguments)
                }
            })

        messages.append(assistant_message)

        # Execute each requested tool
        for tool_call in message.tool_calls:

            tool_name = tool_call.name
            arguments = tool_call.arguments

            # Find and execute the requested tool
            if tool_name not in TOOL_MAP:
                observation = {
                    "error": f"Unknown tool: {tool_name}"
                }
            else:
                observation = TOOL_MAP[tool_name](**arguments)

            # Store the tool execution details
            steps.append({
                "tool": tool_name,
                "arguments": arguments,
                "observation": observation
            })

            # Append the tool observation to conversation
            messages.append({
                "role": "tool",
                "name": tool_name,
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    observation,
                    separators=(",", ":"),
                    default=str
                )
            })

    # Extract status from final answer
    if final_answer:
        status = final_answer.split(":")[0].strip()
    else:
        status = "FALLBACK"

    return {
        "status": status,
        "final_answer": final_answer,
        "steps": steps,
        "llm_calls": llm_calls,
        "tokens_used": tokens_used
    }


def run_all_scenarios():

    scenario_file = "data/raw/agent_scenarios.csv"
    output_file = "outputs/agent_runs.jsonl"

    os.makedirs("outputs", exist_ok=True)

    import csv

    results = []

    with open(scenario_file, "r", encoding="utf-8", newline="") as file:

        scenarios = csv.DictReader(file)

        for scenario in scenarios:

            scenario_id = scenario["scenario_id"]
            user_message = scenario["message"]

            print(f"\nRunning scenario: {scenario_id}")

            result = run_agent(
                user_message=user_message,
                scenario_id=scenario_id
            )

            # Prepare the output record
            record = {
                "scenario_id": scenario_id,
                "status": result["status"],
                "final_answer": result["final_answer"],
                "llm_calls": result["llm_calls"],
                "tokens_used": result["tokens_used"],
                "steps": result["steps"]
            }

            results.append(record)

            # Append one JSON record per scenario
            with open(output_file, "a", encoding="utf-8") as output:

                output.write(
                    json.dumps(record, default=str) + "\n"
                )

            print("Status:", result["status"])
            print("Final answer:", result["final_answer"])
            print("LLM calls:", result["llm_calls"])
            print("Tokens used:", result["tokens_used"])

    return results


if __name__ == "__main__":

    results = run_all_scenarios()

    print("\nD6 - REACT AGENT RESULTS")
    print("-" * 40)

    for result in results:

        print(
            result["scenario_id"],
            "|",
            result["status"],
            "| Calls:",
            result["llm_calls"],
            "| Tokens:",
            result["tokens_used"]
        )
