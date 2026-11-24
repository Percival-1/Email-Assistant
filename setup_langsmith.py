"""
LangSmith Setup Helper

Interactive script to help you configure LangSmith for evaluation.
"""

import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_info(text):
    print(f"ℹ  {text}")

def print_success(text):
    print(f"✓ {text}")

def main():
    print_header("LangSmith Setup for Email Assistant")
    
    print("This script will help you set up LangSmith for evaluation.\n")
    
    # Check if .env exists
    env_path = Path(".env")
    
    if env_path.exists():
        print_success(".env file found")
        with open(env_path, 'r') as f:
            env_content = f.read()
    else:
        print_info(".env file not found, will create new one")
        # Copy from .env.example if it exists
        example_path = Path(".env.example")
        if example_path.exists():
            with open(example_path, 'r') as f:
                env_content = f.read()
        else:
            env_content = ""
    
    # Check existing values
    has_langsmith = 'LANGCHAIN_API_KEY' in env_content
    has_openai = 'OPENAI_API_KEY' in env_content
    
    print()
    print("Configuration status:")
    print(f"  LangSmith API Key: {'✓ Configured' if has_langsmith else '✗ Missing'}")
    print(f"  OpenAI API Key:    {'✓ Configured' if has_openai else '✗ Missing'}")
    print()
    
    # Get LangSmith API key
    if not has_langsmith:
        print_header("Step 1: Get LangSmith API Key")
        print("1. Go to: https://smith.langchain.com")
        print("2. Sign in or create account")
        print("3. Go to Settings → API Keys")
        print("4. Create new API key")
        print()
        
        langsmith_key = input("Enter your LangSmith API key (or press Enter to skip): ").strip()
        
        if langsmith_key:
            # Add to env content
            if 'LANGCHAIN_API_KEY' in env_content:
                # Replace existing
                lines = env_content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('LANGCHAIN_API_KEY'):
                        lines[i] = f'LANGCHAIN_API_KEY={langsmith_key}'
                env_content = '\n'.join(lines)
            else:
                # Add new
                env_content += f"\n\n# LangSmith Configuration\nLANGCHAIN_API_KEY={langsmith_key}\n"
            
            # Add tracing settings if not present
            if 'LANGCHAIN_TRACING_V2' not in env_content:
                env_content += "LANGCHAIN_TRACING_V2=true\n"
            if 'LANGCHAIN_PROJECT' not in env_content:
                env_content += "LANGCHAIN_PROJECT=email-assistant-eval\n"
            
            print_success("LangSmith API key added")
        else:
            print_info("Skipped LangSmith setup")
    else:
        print_info("LangSmith already configured")
    
    # Get OpenAI API key
    if not has_openai:
        print_header("Step 2: Get OpenAI API Key")
        print("1. Go to: https://platform.openai.com/api-keys")
        print("2. Sign in or create account")
        print("3. Create new API key")
        print()
        
        openai_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
        
        if openai_key:
            # Add to env content
            if 'OPENAI_API_KEY' in env_content:
                lines = env_content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('OPENAI_API_KEY'):
                        lines[i] = f'OPENAI_API_KEY={openai_key}'
                env_content = '\n'.join(lines)
            else:
                env_content += f"\n# OpenAI Configuration\nOPENAI_API_KEY={openai_key}\n"
            
            print_success("OpenAI API key added")
        else:
            print_info("Skipped OpenAI setup")
    else:
        print_info("OpenAI already configured")
    
    # Save .env file
    print()
    save = input("Save configuration to .env file? (y/n): ").strip().lower()
    
    if save == 'y':
        with open(env_path, 'w') as f:
            f.write(env_content)
        print_success(f"Configuration saved to {env_path}")
    else:
        print_info("Configuration not saved")
    
    # Summary
    print_header("Setup Complete!")
    
    print("Next steps:")
    print()
    print("  1. Verify your .env file:")
    print(f"     → Edit {env_path}")
    print()
    print("  2. Run evaluation:")
    print(f"     → python run_evaluation.py")
    print()
    print("  3. View results:")
    print(f"     → https://smith.langchain.com")
    print()
    
    # Additional resources
    print("Resources:")
    print("  • Full guide: LANGSMITH_EVALUATION_GUIDE.md")
    print("  • LangSmith docs: https://docs.smith.langchain.com")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
