"""
End-to-End Evaluation of Email Assistant

This script evaluates the complete workflow:
1. Triage classification
2. Response generation
3. Tool usage
4. Response quality
"""

import os
import sys

sys.path.insert(0, "src")

from langsmith import Client
from langsmith import testing as t
import matplotlib.pyplot as plt
from datetime import datetime

from email_assistant.eval.email_dataset import (
    email_inputs,
    email_names,
    expected_tool_calls,
    triage_outputs_list,
)
from email_assistant.email_assistant import email_assistant

# Initialize LangSmith client
client = Client()

# Dataset name
dataset_name = "Email Assistant: End-to-End Evaluation"

# Create dataset if it doesn't exist
if not client.has_dataset(dataset_name=dataset_name):
    print(f"Creating dataset: {dataset_name}")

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Complete evaluation of email assistant workflow including triage, response, and tool usage",
    )

    # Create examples
    examples = []
    for i, email_input in enumerate(email_inputs):
        examples.append(
            {
                "inputs": {"email_input": email_input},
                "outputs": {
                    "expected_triage": triage_outputs_list[i],
                    "expected_tools": expected_tool_calls[i],
                    "email_name": email_names[i],
                },
            }
        )

    client.create_examples(dataset_id=dataset.id, examples=examples)
    print(f"Created {len(examples)} examples")


def target_email_assistant_full(inputs: dict) -> dict:
    """
    Run the full email assistant workflow and extract results.

    Args:
        inputs: Dictionary with email_input

    Returns:
        Dictionary with classification, tools_called, and response
    """
    try:
        # Run the assistant
        response = email_assistant.invoke({"email_input": inputs["email_input"]})

        # Extract results
        result = {
            "classification": response.get("classification_decision", "unknown"),
            "tools_called": response.get("tools_called", []),
            "response": response.get("draft_response", ""),
            "success": True,
        }

        return result

    except Exception as e:
        print(f"Error in full workflow: {e}")
        return {
            "classification": "error",
            "tools_called": [],
            "response": "",
            "success": False,
            "error": str(e),
        }


# Evaluator 1: Triage Classification
def evaluate_triage(outputs: dict, reference_outputs: dict) -> dict:
    """Check if triage classification is correct."""
    if not outputs.get("success"):
        return {"key": "triage_accuracy", "score": 0.0}

    actual = outputs.get("classification", "").lower()
    expected = reference_outputs.get("expected_triage", "").lower()

    score = 1.0 if actual == expected else 0.0

    return {
        "key": "triage_accuracy",
        "score": score,
        "comment": f"Expected: {expected}, Got: {actual}",
    }


# Evaluator 2: Tool Usage
def evaluate_tools(outputs: dict, reference_outputs: dict) -> dict:
    """Check if correct tools were called."""
    if not outputs.get("success"):
        return {"key": "tool_accuracy", "score": 0.0}

    actual_tools = set(outputs.get("tools_called", []))
    expected_tools = set(reference_outputs.get("expected_tools", []))

    # If no tools expected and none called, perfect
    if len(expected_tools) == 0 and len(actual_tools) == 0:
        score = 1.0
    # If tools expected but none called, or vice versa
    elif len(expected_tools) == 0 or len(actual_tools) == 0:
        score = 0.0
    else:
        # Calculate overlap
        correct = len(actual_tools.intersection(expected_tools))
        total = len(expected_tools)
        score = correct / total if total > 0 else 0.0

    return {
        "key": "tool_accuracy",
        "score": score,
        "comment": f"Expected: {expected_tools}, Got: {actual_tools}",
    }


# Evaluator 3: Response Generated
def evaluate_response_exists(outputs: dict, reference_outputs: dict) -> dict:
    """Check if a response was generated when needed."""
    if not outputs.get("success"):
        return {"key": "response_exists", "score": 0.0}

    expected_triage = reference_outputs.get("expected_triage", "").lower()
    response = outputs.get("response", "")

    # If should respond, check if response exists
    if expected_triage == "respond":
        score = 1.0 if len(response.strip()) > 0 else 0.0
    else:
        # If shouldn't respond, check that no response or minimal
        score = 1.0

    return {"key": "response_exists", "score": score}


# Evaluator 4: Error Rate
def evaluate_no_errors(outputs: dict, reference_outputs: dict) -> dict:
    """Check if the workflow completed without errors."""
    score = 1.0 if outputs.get("success", False) else 0.0

    return {
        "key": "no_errors",
        "score": score,
        "comment": outputs.get("error", "No errors") if score == 0.0 else "Success",
    }


# Run evaluation
print("\n" + "=" * 60)
print("Running End-to-End Evaluation")
print("=" * 60 + "\n")

experiment_results = client.evaluate(
    target_email_assistant_full,
    data=dataset_name,
    evaluators=[
        evaluate_triage,
        evaluate_tools,
        evaluate_response_exists,
        evaluate_no_errors,
    ],
    experiment_prefix="Email Assistant End-to-End",
    max_concurrency=2,
)

# Convert to DataFrame
df = experiment_results.to_pandas()

# Calculate metrics
metrics = {
    "Triage Accuracy": (
        df["feedback.triage_accuracy"].mean()
        if "feedback.triage_accuracy" in df.columns
        else 0.0
    ),
    "Tool Accuracy": (
        df["feedback.tool_accuracy"].mean()
        if "feedback.tool_accuracy" in df.columns
        else 0.0
    ),
    "Response Exists": (
        df["feedback.response_exists"].mean()
        if "feedback.response_exists" in df.columns
        else 0.0
    ),
    "No Errors": (
        df["feedback.no_errors"].mean() if "feedback.no_errors" in df.columns else 0.0
    ),
}

# Create visualization
plt.figure(figsize=(12, 6))
metric_names = list(metrics.keys())
scores = list(metrics.values())

# Create bars
bars = plt.bar(
    metric_names, scores, color=["#5DA5DA", "#FAA43A", "#60BD68", "#B276B2"], width=0.6
)

# Add labels
plt.xlabel("Evaluation Metrics", fontsize=12)
plt.ylabel("Score (0-1)", fontsize=12)
plt.title(
    "Email Assistant End-to-End Evaluation Results", fontsize=14, fontweight="bold"
)

# Add score values on bars
for i, (bar, score) in enumerate(zip(bars, scores)):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        score + 0.02,
        f"{score:.2%}",
        ha="center",
        fontweight="bold",
        fontsize=10,
    )

# Set y-axis limit
plt.ylim(0, 1.1)

# Add grid
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Rotate x-axis labels if needed
plt.xticks(rotation=15, ha="right")

# Tight layout
plt.tight_layout()

# Save plot
os.makedirs("src/email_assistant/eval/results", exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
plot_path = f"src/email_assistant/eval/results/end_to_end_results_{timestamp}.png"
plt.savefig(plot_path, dpi=150, bbox_inches="tight")
plt.close()

# Extract latency metrics
if "latency" in df.columns:
    avg_latency = df["latency"].mean()
    max_latency = df["latency"].max()
    min_latency = df["latency"].min()
else:
    avg_latency = max_latency = min_latency = 0.0

# Extract token usage if available
if "total_tokens" in df.columns:
    total_tokens = df["total_tokens"].sum()
    avg_tokens = df["total_tokens"].mean()
else:
    total_tokens = avg_tokens = 0

# Count failures
total_runs = len(df)
failed_runs = len(df[df["error"].notna()]) if "error" in df.columns else 0
success_rate = ((total_runs - failed_runs) / total_runs * 100) if total_runs > 0 else 0

# Identify failed test cases
failed_cases = []
if "error" in df.columns:
    for idx, row in df[df["error"].notna()].iterrows():
        failed_cases.append(
            {
                "test": row.get("example_id", idx),
                "error": str(row["error"])[:100],  # Truncate long errors
            }
        )

# Print results
print("\n" + "=" * 60)
print("Evaluation Complete!")
print("=" * 60 + "\n")

print("📊 Accuracy Metrics:")
for metric, score in metrics.items():
    print(f"  {metric:20s}: {score:6.2%}")

print(f"\n⚡ Performance Metrics:")
print(f"  Average Latency      : {avg_latency:6.2f}s")
print(f"  Min Latency          : {min_latency:6.2f}s")
print(f"  Max Latency          : {max_latency:6.2f}s")
print(f"  Success Rate         : {success_rate:6.2f}%")

if total_tokens > 0:
    print(f"\n💰 Token Usage:")
    print(f"  Total Tokens         : {int(total_tokens):,}")
    print(f"  Avg Tokens/Email     : {int(avg_tokens):,}")
    cost_estimate = (total_tokens / 1000) * 0.01  # Rough estimate
    print(f"  Est. Cost (GPT-4)    : ${cost_estimate:.4f}")

if failed_cases:
    print(f"\n❌ Failed Test Cases ({len(failed_cases)}):")
    for i, case in enumerate(failed_cases[:5], 1):  # Show first 5
        print(f"  {i}. Test: {case['test']}")
        print(f"     Error: {case['error']}")
    if len(failed_cases) > 5:
        print(f"  ... and {len(failed_cases) - 5} more (see LangSmith for details)")
else:
    print(f"\n✅ No Failed Test Cases!")

print(f"\n📁 Visualization saved to: {plot_path}")
print(f"\n🌐 View detailed results in LangSmith:")
print(f"  → https://smith.langchain.com")
print(f"  → Project: {os.getenv('LANGCHAIN_PROJECT', 'email-assistant-eval')}")
print("\n" + "=" * 60 + "\n")

# Overall score
overall_score = sum(scores) / len(scores)
print(f"🎯 Overall Score: {overall_score:.2%}")

if overall_score >= 0.9:
    print("🎉 Excellent performance!")
elif overall_score >= 0.75:
    print("✅ Good performance, minor improvements possible")
elif overall_score >= 0.6:
    print("⚠️  Acceptable, but needs improvement")
else:
    print("❌ Needs significant improvement")

# Recommendations
print(f"\n💡 Recommendations:")
if avg_latency > 10:
    print("  • Latency is high - consider caching or smaller models")
if metrics.get("Triage Accuracy", 1.0) < 0.85:
    print("  • Improve triage prompt in src/email_assistant/prompts.py")
if metrics.get("Tool Accuracy", 1.0) < 0.90:
    print("  • Clarify tool descriptions in src/email_assistant/tools/")
if failed_runs > 0:
    print(f"  • Fix {failed_runs} errors - check traces in LangSmith")

print()
