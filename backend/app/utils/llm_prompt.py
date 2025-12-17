"""
Few-shot prompt for subscription extraction using GPT-4 or Claude
"""

EXTRACTION_PROMPT_TEMPLATE = """You are an expert at extracting subscription information from emails.

Given an email, extract the following fields as JSON:
- service_name: The name of the service/company (string, required)
- price: The subscription cost (float, required)
- currency: Currency code (string, default "USD")
- billing_period: One of "monthly", "annually", "quarterly", "one-time" (string, required)
- next_renewal_date: ISO 8601 format YYYY-MM-DD (string, optional)
- unsubscribe_link: Full URL to cancel/manage subscription (string, required)
- payment_method_last4: Last 4 digits of payment method (string, optional)
- subscription_tier: Plan name like "Premium", "Pro" (string, optional)
- confidence: Your confidence in this extraction, 0.0 to 1.0 (float, required)

Rules:
1. If a field cannot be found, use null (not an empty string)
2. Validate that unsubscribe_link is a complete, valid URL
3. If price is unclear or ambiguous, set confidence < 0.5
4. For renewal dates, infer from context if not explicitly stated
5. Normalize service names (e.g., "Spotify Premium" → "Spotify")

EXAMPLE 1:
Email:
---
Subject: Your Netflix subscription is confirmed
From: info@netflix.com

Hi John,

Your Netflix Premium subscription is now active.

Plan: Premium (4K + 4 screens)
Price: $19.99/month
Next billing date: January 15, 2026
Payment method: Visa ending in 4532

Manage your membership: https://www.netflix.com/account
Cancel anytime: https://www.netflix.com/cancelplan
---

Output:
{{
  "service_name": "Netflix",
  "price": 19.99,
  "currency": "USD",
  "billing_period": "monthly",
  "next_renewal_date": "2026-01-15",
  "unsubscribe_link": "https://www.netflix.com/cancelplan",
  "payment_method_last4": "4532",
  "subscription_tier": "Premium",
  "confidence": 0.95
}}

EXAMPLE 2:
Email:
---
Subject: Welcome to Dropbox Plus!
From: no-reply@dropbox.com

Thanks for upgrading to Dropbox Plus.

Your subscription:
- 2 TB of storage
- $11.99 per month
- Renews on the 20th of each month

View account: https://www.dropbox.com/account
Manage subscription: https://www.dropbox.com/account/manage
---

Output:
{{
  "service_name": "Dropbox",
  "price": 11.99,
  "currency": "USD",
  "billing_period": "monthly",
  "next_renewal_date": null,
  "unsubscribe_link": "https://www.dropbox.com/account/manage",
  "payment_method_last4": null,
  "subscription_tier": "Plus",
  "confidence": 0.90
}}

EXAMPLE 3:
Email:
---
Subject: Your annual membership renews soon
From: support@gymflow.com

Hi Sarah,

Your GymFlow Premium membership will auto-renew on March 1, 2026.

Annual fee: $299.00
Payment: MasterCard ****8765

To cancel or make changes, visit your account dashboard or call us at 1-800-555-0123.
Account link: https://gymflow.com/my-account
---

Output:
{{
  "service_name": "GymFlow",
  "price": 299.00,
  "currency": "USD",
  "billing_period": "annually",
  "next_renewal_date": "2026-03-01",
  "unsubscribe_link": "https://gymflow.com/my-account",
  "payment_method_last4": "8765",
  "subscription_tier": "Premium",
  "confidence": 0.88
}}

Now extract from this email:
---
{email_text}
---

Output only valid JSON, no additional text.
"""


def build_extraction_prompt(email_subject: str, email_body: str) -> str:
    """Build the complete extraction prompt with the target email"""
    email_text = f"Subject: {email_subject}\n\n{email_body}"
    return EXTRACTION_PROMPT_TEMPLATE.format(email_text=email_text)

