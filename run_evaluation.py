"""
Quick Start Evaluation Script

Run this to evaluate your email assistant with LangSmith.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Color output for terminal
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")


def print_info(text):
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.END}")


def check_env_vars():
    """Check if required environment variables are set."""
    required_vars = {
        "LANGCHAIN_API_KEY": "LangSmith API key",
        "OPENAI_API_KEY": "OpenAI API key",
    }

    missing = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing.append(f"{var} ({description})")

    return missing


def main():
    print_header("Email Assistant LangSmith Evaluation")

    # Check environment
    print_info("Checking environment setup...")

    missing_vars = check_env_vars()
    if missing_vars:
        print_error("Missing required environment variables:")
        for var in missing_vars:
            print(f"  • {var}")
        print()
        print_info("Add these to your .env file or set them in your terminal:")
        print()
        print("  LANGCHAIN_API_KEY=your_key_here")
        print("  LANGCHAIN_TRACING_V2=true")
        print("  LANGCHAIN_PROJECT=email-assistant-eval")
        print("  OPENAI_API_KEY=your_key_here")
        print()
        sys.exit(1)

    print_success("Environment variables configured")

    # Set tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "email-assistant-eval"

    print_success(
        f"LangSmith tracing enabled (Project: {os.getenv('LANGCHAIN_PROJECT')})"
    )

    # Menu
    print()
    print("Select evaluation type:")
    print()
    print("  1. Triage Classification (Basic - Fast)")
    print("     Tests email classification accuracy")
    print()
    print("  2. End-to-End Workflow (Complete - Slower)")
    print("     Tests classification, tools, and responses")
    print()
    print("  3. Both (Recommended)")
    print()

    choice = input("Enter choice (1-3): ").strip()

    if choice not in ["1", "2", "3"]:
        print_error("Invalid choice")
        sys.exit(1)

    # Add src to path
    sys.path.insert(0, "src")

    # Run evaluations
    if choice in ["1", "3"]:
        print_header("Running Triage Evaluation")
        try:
            from email_assistant.eval import evaluate_triage

            print_success("Triage evaluation completed!")
        except Exception as e:
            print_error(f"Triage evaluation failed: {e}")
            import traceback

            traceback.print_exc()

    if choice in ["2", "3"]:
        print_header("Running End-to-End Evaluation")
        try:
            from email_assistant.eval import evaluate_end_to_end

            print_success("End-to-end evaluation completed!")
        except Exception as e:
            print_error(f"End-to-end evaluation failed: {e}")
            import traceback

            traceback.print_exc()

    # Summary
    print_header("Evaluation Complete!")

    print_info("Next steps:")
    print()
    print("  1. View detailed results in LangSmith:")
    print(f"     → https://smith.langchain.com")
    print()
    print("  2. Check generated charts:")
    print(f"     → src/email_assistant/eval/results/")
    print()
    print("  3. Improve prompts based on failures:")
    print(f"     → src/email_assistant/prompts.py")
    print()
    print("  4. Re-run evaluation to compare:")
    print(f"     → python run_evaluation.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Evaluation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
