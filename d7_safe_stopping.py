
import csv
import json
import os
import time

from mock_llm import chat
from d6_react_agent import AGENT
from d5_refund_tools import TOOLS_SPEC, TOOL_MAP


def run_agent(
    user_message,
    scenario_id,
    max_iterations=6,
    token_limit=6000,
    time_limit_seconds=10
):

    start_time = time.monotonic()

    messages = [
        {"role": "system", "content": AGENT},
        {"role": "user", "content": user_message}
    ]

    steps = []
    llm_calls = 0
    tokens_used = 0
    final_answer = ""

    # Helper function to generate a fallback response
    def fallback(status, reason):

        return {
            "status": status,
            "final_answer": (
                f"{status}: {reason} "
                "The case has been handed over to a human support agent."
            ),
            "steps": steps,
            "llm_calls": llm_calls,
            "tokens_used": tokens_used
        }

    # ReAct loop with safety limits
    for iteration in range(max_iterations):

        # Check timeout before calling the model
        if time.monotonic() - start_time >= time_limit_seconds:

            return fallback(
                "FALLBACK_TIMEOUT",
                "The agent exceeded its execution time limit."
            )

        # Call the model
        response = chat(messages, tools=TOOLS_SPEC)

        llm_calls += 1
        tokens_used += response.usage.total_tokens

        # Check timeout after the model call
        if time.monotonic() - start_time >= time_limit_seconds:

            return fallback(
                "FALLBACK_TIMEOUT",
                "The agent exceeded its execution time limit."
            )

        # Check token limit before executing any requested tool
        if tokens_used > token_limit:

            return fallback(
                "FALLBACK_TOKEN_LIMIT",
                "The agent exceeded its token usage limit."
            )

        message = response.choices[0].message

        # If no tool is requested, return the final answer
        if not message.tool_calls:

            final_answer = message.content or ""

            return {
                "status": final_answer.split(":")[0].strip(),
                "final_answer": final_answer,
                "steps": steps,
                "llm_calls": llm_calls,
                "tokens_used": tokens_used
            }

        # Append assistant tool-call message
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

        # Execute requested tools
        for tool_call in message.tool_calls:

            # Check timeout before each tool execution
            if time.monotonic() - start_time >= time_limit_seconds:

                return fallback(
                    "FALLBACK_TIMEOUT",
                    "The agent exceeded its execution time limit."
                )

            tool_name = tool_call.name
            arguments = tool_call.arguments

            if tool_name not in TOOL_MAP:

                observation = {
                    "error": f"Unknown tool: {tool_name}"
                }

            else:

                observation = TOOL_MAP[tool_name](**arguments)

            # Save completed tool execution
            steps.append({
                "tool": tool_name,
                "arguments": arguments,
                "observation": observation
            })

            # Append tool observation to conversation
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

            # Check timeout after tool execution
            if time.monotonic() - start_time >= time_limit_seconds:

                return fallback(
                    "FALLBACK_TIMEOUT",
                    "The agent exceeded its execution time limit."
                )

    # Reached maximum number of iterations
    return fallback(
        "FALLBACK_MAX_ITERATIONS",
        "The agent reached its maximum iteration limit."
    )


def load_scenarios():

    scenario_file = "data/raw/agent_scenarios.csv"

    with open(
        scenario_file,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        return {
            row["scenario_id"]: row
            for row in csv.DictReader(file)
        }


def run_d7_tests():

    scenarios = load_scenarios()

    test_cases = [
        {
            "test": "S1_TOKEN_LIMIT",
            "scenario_id": "S1",
            "token_limit": 200,
            "time_limit_seconds": 10
        },
        {
            "test": "S1_TIMEOUT",
            "scenario_id": "S1",
            "token_limit": 6000,
            "time_limit_seconds": 0
        },
        {
            "test": "S7_MAX_ITERATIONS",
            "scenario_id": "S7",
            "token_limit": 6000,
            "time_limit_seconds": 10
        }
    ]

    output_file = "outputs/d7_safety_tests.jsonl"

    os.makedirs("outputs", exist_ok=True)

    # Start a fresh output file for these three tests
    with open(output_file, "w", encoding="utf-8") as file:

        for test in test_cases:

            scenario = scenarios[test["scenario_id"]]

            print("\nRunning:", test["test"])

            result = run_agent(
                user_message=scenario["message"],
                scenario_id=test["scenario_id"],
                token_limit=test["token_limit"],
                time_limit_seconds=test["time_limit_seconds"]
            )

            record = {
                "test": test["test"],
                "scenario_id": test["scenario_id"],
                "status": result["status"],
                "final_answer": result["final_answer"],
                "llm_calls": result["llm_calls"],
                "tokens_used": result["tokens_used"],
                "steps": result["steps"]
            }

            file.write(
                json.dumps(record, default=str) + "\n"
            )

            print("Status:", result["status"])
            print("Final answer:", result["final_answer"])
            print("LLM calls:", result["llm_calls"])
            print("Tokens used:", result["tokens_used"])
            print("Completed tool steps:", len(result["steps"]))


if __name__ == "__main__":

    run_d7_tests()
