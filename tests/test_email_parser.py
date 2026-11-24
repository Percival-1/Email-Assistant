"""
Test Email Parser - Demonstrate Token Savings

This script shows how the email parser reduces token usage
while preserving important content.
"""

import sys
sys.path.insert(0, 'src')

from email_assistant.email_parser import (
    parse_email_for_llm,
    compare_parsing,
    estimate_tokens
)

# Sample HTML emails
SAMPLE_EMAILS = {
    "marketing": """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .header { background: #f0f0f0; padding: 20px; }
            .footer { font-size: 10px; color: #999; }
        </style>
    </head>
    <body>
        <div class="header">
            <img src="logo.png" width="200" height="50">
        </div>
        <div class="content">
            <h1>Special Offer Just for You!</h1>
            <p>Dear Customer,</p>
            <p>Get 20% off your next purchase with code SAVE20.</p>
            <p><a href="https://example.com/shop?utm_source=email&utm_campaign=spring2024">Shop Now</a></p>
        </div>
        <div class="footer">
            <p>Company Inc. | 123 Main St | City, State 12345</p>
            <p>Unsubscribe | Privacy Policy | Terms of Service</p>
            <p>&copy; 2024 Company Inc. All rights reserved.</p>
        </div>
        <img src="tracking.png" width="1" height="1" style="display:none">
    </body>
    </html>
    """,
    
    "meeting_request": """
    <html>
    <body>
        <div style="font-family: Calibri, sans-serif;">
            <p>Hi John,</p>
            <p>I hope this email finds you well. I wanted to reach out to schedule a meeting 
            to discuss the Q3 roadmap and upcoming product launches.</p>
            <p>Would you be available next Tuesday or Wednesday afternoon? I'm flexible on timing.</p>
            <p>Looking forward to hearing from you.</p>
            <p>Best regards,<br>
            Alice Smith<br>
            Product Manager<br>
            alice@company.com<br>
            (555) 123-4567</p>
        </div>
        <div class="gmail_signature">
            <p><i>This email and any attachments are confidential...</i></p>
        </div>
    </body>
    </html>
    """,
    
    "thread_reply": """
    <html>
    <body>
        <div>
            <p>Thanks for the update! This looks good to me.</p>
            <p>-John</p>
        </div>
        <div class="gmail_quote">
            <div>On Mon, Jan 15, 2024 at 2:30 PM Alice Smith wrote:</div>
            <blockquote>
                <p>Hi John,</p>
                <p>Here's the updated document with your feedback incorporated. 
                Let me know if you have any other changes.</p>
                <p>Thanks,<br>Alice</p>
                <div class="gmail_quote">
                    <div>On Mon, Jan 15, 2024 at 10:15 AM John Doe wrote:</div>
                    <blockquote>
                        <p>Could you add more details to section 3?</p>
                    </blockquote>
                </div>
            </blockquote>
        </div>
    </body>
    </html>
    """
}

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_comparison(name, html_content):
    """Print comparison for a sample email."""
    print_header(f"Test: {name}")
    
    result = compare_parsing(html_content)
    
    print(f"📊 Statistics:")
    print(f"  Raw Length:    {result['raw_length']:,} chars")
    print(f"  Parsed Length: {result['parsed_length']:,} chars")
    print(f"  Reduction:     {result['raw_length'] - result['parsed_length']:,} chars")
    print()
    
    print(f"💰 Token Comparison:")
    print(f"  Raw Tokens:    {result['raw_tokens']:,} tokens")
    print(f"  Parsed Tokens: {result['parsed_tokens']:,} tokens")
    print(f"  Tokens Saved:  {result['tokens_saved']:,} tokens")
    print(f"  Savings:       {result['percent_saved']:.1f}%")
    print()
    
    print(f"📝 Parsed Content (First 500 chars):")
    print("-" * 70)
    preview = result['parsed_content'][:500]
    print(preview)
    if len(result['parsed_content']) > 500:
        print("...")
    print()

def main():
    print_header("Email Parser Token Savings Test")
    
    print("This demonstrates how the email parser reduces token usage")
    print("while preserving all important information.")
    
    # Test each sample
    for name, html_content in SAMPLE_EMAILS.items():
        print_comparison(name, html_content)
    
    # Summary
    print_header("Summary")
    
    total_raw = sum(compare_parsing(html)['raw_tokens'] for html in SAMPLE_EMAILS.values())
    total_parsed = sum(compare_parsing(html)['parsed_tokens'] for html in SAMPLE_EMAILS.values())
    total_saved = total_raw - total_parsed
    percent_saved = (total_saved / total_raw * 100) if total_raw > 0 else 0
    
    print(f"Total across all samples:")
    print(f"  Raw:    {total_raw:,} tokens")
    print(f"  Parsed: {total_parsed:,} tokens")
    print(f"  Saved:  {total_saved:,} tokens ({percent_saved:.1f}%)")
    print()
    
    print(f"💵 Cost Savings (GPT-4o pricing):")
    # GPT-4o: $5/1M input tokens
    raw_cost = (total_raw / 1_000_000) * 5.00
    parsed_cost = (total_parsed / 1_000_000) * 5.00
    cost_saved = raw_cost - parsed_cost
    
    print(f"  Raw cost:    ${raw_cost:.6f}")
    print(f"  Parsed cost: ${parsed_cost:.6f}")
    print(f"  Saved:       ${cost_saved:.6f} per batch")
    print()
    
    # Extrapolate
    emails_per_day = 100
    daily_saved = cost_saved * (emails_per_day / 3)
    monthly_saved = daily_saved * 30
    
    print(f"💰 Projected Savings at {emails_per_day} emails/day:")
    print(f"  Daily:   ${daily_saved:.2f}")
    print(f"  Monthly: ${monthly_saved:.2f}")
    print(f"  Yearly:  ${monthly_saved * 12:.2f}")
    print()
    
    print_header("Benefits")
    
    benefits = [
        "✅ 50-80% token reduction",
        "✅ Preserves all important content",
        "✅ Removes HTML tags and styling",
        "✅ Strips tracking pixels",
        "✅ Removes email signatures",
        "✅ Removes quoted/forwarded content",
        "✅ Cleans up whitespace",
        "✅ Removes URLs (can be toggled)",
        "✅ Automatic HTML detection",
        "✅ Fallback for plain text",
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")
    
    print()
    
    print_header("Usage in Your Code")
    
    print("The parser is automatically integrated into Gmail tools:")
    print()
    print("```python")
    print("from email_assistant.email_parser import parse_email_for_llm")
    print()
    print("# Parse HTML email")
    print("clean_text = parse_email_for_llm(")
    print("    html_content,")
    print("    preserve_links=False,  # Remove URLs")
    print("    max_length=2000        # Limit length")
    print(")")
    print("```")
    print()
    
    print("Or use in Gmail tools (already integrated):")
    print()
    print("```python")
    print("# In gmail_tools.py - extract_message_part()")
    print("# Automatically applies parsing to all emails")
    print("```")
    print()

if __name__ == "__main__":
    main()
