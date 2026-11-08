
import json
import os

from mock_llm import chat
from d6_react_agent import AGENT
from d5_refund_tools import TOOLS_SPEC, TOOL_MAP


CHECKPOINT_DIR = "state"


class SimulatedCrash(Exception):
    pass


def get_checkpoint_path(run_id):

    return os.path.join(CHECKPOINT_DIR, f"{run_id}.json")


def save_checkpoint(checkpoint):

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    path = get_checkpoint_path(checkpoint["run_id"])
    temp_path = path + ".tmp"

    with open(temp_path, "w", encoding="utf-8") as file:

        json.dump(checkpoint, file, indent=4, default=str)

    # Replace the old checkpoint safely
    os.replace(temp_path, path)


def load_checkpoint(run_id):

    path = get_checkpoint_path(run_id)

    with open(path, "r", encoding="utf-8") as file:

        return json.load(file)


def run_agent(
    user_message,
    scenario_id,
    run_id,
    max_iterations=6,
    crash_after_tools=None
):

    # Initialise a new checkpoint
    checkpoint = {
        "run_id": run_id,
        "scenario_id": scenario_id,
        "messages": [
            {"role": "system", "content": AGENT},
            {"role": "user", "content": user_message}
        ],
        "tokens_used": 0,
        "llm_calls": 0,
        "step_number": 0,
        "tools_executed": [],
        "steps": [],
        "status": "running"
    }

    save_checkpoint(checkpoint)

    return continue_agent(
        checkpoint,
        max_iterations,
        crash_after_tools
    )


def continue_agent(
    checkpoint,
    max_iterations=6,
    crash_after_tools=None
):

    messages = checkpoint["messages"]

    # Continue from the previously completed model calls
    while checkpoint["llm_calls"] < max_iterations:

        # Call the model with restored conversation history
        response = chat(messages, tools=TOOLS_SPEC)

        checkpoint["llm_calls"] += 1

        checkpoint["tokens_used"] += response.usage.total_tokens

        message = response.choices[0].message

        # No more tools required: final answer
        if not message.tool_calls:

            final_answer = message.content or ""

            checkpoint["final_answer"] = final_answer
            checkpoint["status"] = final_answer.split(":")[0].strip()

            save_checkpoint(checkpoint)

            return {
                "status": checkpoint["status"],
                "final_answer": final_answer,
                "steps": checkpoint["steps"],
                "llm_calls": checkpoint["llm_calls"],
                "tokens_used": checkpoint["tokens_used"],
                "tools_executed": checkpoint["tools_executed"]
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

            tool_name = tool_call.name
            arguments = tool_call.arguments

            if tool_name not in TOOL_MAP:

                observation = {
                    "error": f"Unknown tool: {tool_name}"
                }

            else:

                observation = TOOL_MAP[tool_name](**arguments)

            # Record completed execution
            step = {
                "tool": tool_name,
                "arguments": arguments,
                "observation": observation
            }

            checkpoint["steps"].append(step)

            checkpoint["tools_executed"].append(tool_name)

            checkpoint["step_number"] += 1

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

            # Save immediately after every tool observation
            save_checkpoint(checkpoint)

            print(
                "Checkpoint saved after tool:",
                tool_name,
                "| Step:",
                checkpoint["step_number"]
            )

            # Simulate crash only after checkpoint is saved
            if (
                crash_after_tools is not None
                and checkpoint["step_number"] == crash_after_tools
            ):

                raise SimulatedCrash(
                    "Simulated crash after tool execution "
                    f"{checkpoint['step_number']}"
                )

    checkpoint["status"] = "FALLBACK_MAX_ITERATIONS"
    checkpoint["final_answer"] = (
        "FALLBACK_MAX_ITERATIONS: Maximum model calls reached. "
        "The case has been handed over to a human support agent."
    )

    save_checkpoint(checkpoint)

    return {
        "status": checkpoint["status"],
        "final_answer": checkpoint["final_answer"],
        "steps": checkpoint["steps"],
        "llm_calls": checkpoint["llm_calls"],
        "tokens_used": checkpoint["tokens_used"],
        "tools_executed": checkpoint["tools_executed"]
    }


def resume_agent(run_id):

    print("\nLoading checkpoint:", run_id)

    checkpoint = load_checkpoint(run_id)

    if checkpoint["status"] != "running":

        raise ValueError("This checkpoint is not an active run.")

    print("Scenario:", checkpoint["scenario_id"])
    print("Completed steps:", checkpoint["step_number"])
    print("Previous tools:", checkpoint["tools_executed"])
    print("Previous model calls:", checkpoint["llm_calls"])
    print("Previous tokens:", checkpoint["tokens_used"])

    print("\nResuming agent execution...\n")

    return continue_agent(checkpoint)


def run_checkpoint_demo():

    run_id = "D8_S1_DEMO"

    checkpoint_path = get_checkpoint_path(run_id)

    # Prevent accidental duplicate refund execution
    if os.path.exists(checkpoint_path):

        existing = load_checkpoint(run_id)

        if existing["status"] == "REFUND":

            print(
                "This demonstration has already completed. "
                "Skipping to prevent duplicate refund execution."
            )

            print("Final answer:", existing["final_answer"])
            print("Tools:", existing["tools_executed"])

            return

        if existing["status"] == "running":

            print("Existing incomplete checkpoint found.")

            result = resume_agent(run_id)

            print("\nResumed result:", result)

            return

    # Read the original S1 scenario
    import csv

    with open(
        "data/raw/agent_scenarios.csv",
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        scenarios = list(csv.DictReader(file))

    scenario = next(
        row for row in scenarios
        if row["scenario_id"] == "S1"
    )

    print("Starting D8 checkpoint demonstration.")

    # Start execution and simulate crash after second tool
    try:

        run_agent(
            user_message=scenario["message"],
            scenario_id="S1",
            run_id=run_id,
            crash_after_tools=2
        )

    except SimulatedCrash as error:

        print("\nSIMULATED CRASH")
        print(error)

    # Resume using the saved checkpoint
    print("\nStarting resume process.")

    result = resume_agent(run_id)

    print("\nD8 - CHECKPOINT AND RESUME RESULTS")
    print("-" * 45)

    print("Status:", result["status"])
    print("Final answer:", result["final_answer"])
    print("LLM calls:", result["llm_calls"])
    print("Tokens used:", result["tokens_used"])

    print("\nTool execution history:")

    for index, tool in enumerate(
        result["tools_executed"],
        start=1
    ):

        print(index, tool)

    # Save final result
    os.makedirs("outputs", exist_ok=True)

    with open(
        "outputs/d8_checkpoint_results.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(result, file, indent=4, default=str)


if __name__ == "__main__":

    run_checkpoint_demo()
