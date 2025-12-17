"""
Regex patterns for rule-based subscription detection
"""
import re

# Price patterns (various formats)
PRICE_PATTERNS = [
    r'\$(\d+\.\d{2})',  # $19.99
    r'\$(\d+)',  # $20
    r'USD\s*(\d+\.\d{2})',  # USD 19.99
    r'(\d+\.\d{2})\s*USD',  # 19.99 USD
    r'€(\d+\.\d{2})',  # €19.99
    r'£(\d+\.\d{2})',  # £19.99
    r'price:?\s*\$?(\d+\.\d{2})',  # Price: $19.99
    r'amount:?\s*\$?(\d+\.\d{2})',  # Amount: $19.99
    r'total:?\s*\$?(\d+\.\d{2})',  # Total: $19.99
    r'(\d+,\d{3}\.\d{2})',  # 1,299.99
]

# Billing period patterns
BILLING_PERIOD_PATTERNS = {
    'monthly': [
        r'per\s+month',
        r'/mo\b',
        r'monthly',
        r'billed\s+monthly',
        r'every\s+month',
        r'month[ly]*\s+subscription',
    ],
    'annually': [
        r'per\s+year',
        r'/yr\b',
        r'/year\b',
        r'annual[ly]*',
        r'yearly',
        r'billed\s+annual[ly]*',
        r'every\s+year',
        r'year[ly]*\s+subscription',
    ],
    'quarterly': [
        r'quarter[ly]*',
        r'every\s+3\s+months',
        r'per\s+quarter',
        r'billed\s+quarter[ly]*',
    ],
    'one-time': [
        r'one[- ]time',
        r'single\s+payment',
        r'lifetime\s+access',
    ]
}

# Date patterns (various formats)
DATE_PATTERNS = [
    r'\d{4}-\d{2}-\d{2}',  # 2025-12-15
    r'\d{2}/\d{2}/\d{4}',  # 12/15/2025
    r'\d{2}-\d{2}-\d{4}',  # 12-15-2025
    r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',  # January 15, 2025
    r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # 15 January 2025
]

# Unsubscribe link patterns
UNSUBSCRIBE_LINK_PATTERNS = [
    r'https?://[^\s<>"]+/(?:unsubscribe|cancel|opt-out|manage|unsub|stop)[^\s<>"]*',
    r'https?://[^\s<>"]+\?.*(?:unsubscribe|cancel|unsub)[^\s<>"]*',
    r'https?://[^\s<>"]+/account/(?:cancel|manage|settings)[^\s<>"]*',
    r'https?://[^\s<>"]+/subscription/(?:cancel|manage)[^\s<>"]*',
]

# Subscription-related keywords (for initial filtering)
SUBSCRIPTION_KEYWORDS = [
    'subscription',
    'subscribe',
    'subscribed',
    'billing',
    'billed',
    'renew',
    'renewal',
    'payment',
    'paid',
    'invoice',
    'receipt',
    'membership',
    'member',
    'auto-pay',
    'recurring',
    'monthly charge',
    'annual fee',
    'plan',
    'premium',
    'upgrade',
    'downgrade',
    'cancel',
    'unsubscribe',
]

# Common service name patterns
SERVICE_NAME_PATTERNS = {
    'streaming': [
        'netflix', 'hulu', 'disney', 'disney+', 'hbo', 'prime video',
        'spotify', 'apple music', 'youtube', 'youtube premium', 'paramount',
        'peacock', 'showtime', 'starz', 'discovery+', 'espn+',
    ],
    'saas': [
        'dropbox', 'google', 'microsoft', 'office 365', 'adobe',
        'creative cloud', 'slack', 'zoom', 'github', 'gitlab',
        'jira', 'confluence', 'notion', 'figma', 'canva',
        'mailchimp', 'hubspot', 'salesforce', 'quickbooks',
    ],
    'news': [
        'new york times', 'washington post', 'wall street journal',
        'medium', 'substack', 'the atlantic', 'economist',
    ],
    'fitness': [
        'peloton', 'headspace', 'calm', 'noom', 'myfitnesspal',
        'strava', 'whoop', 'fitbit premium',
    ],
    'gaming': [
        'playstation', 'xbox', 'nintendo', 'steam', 'epic games',
        'origin', 'ea play', 'ubisoft+', 'twitch',
    ],
    'productivity': [
        'evernote', 'todoist', '1password', 'lastpass', 'dashlane',
        'grammarly', 'otter.ai', 'calendly', 'loom',
    ],
    'shopping': [
        'amazon prime', 'walmart+', 'target circle', 'instacart',
        'doordash', 'uber eats', 'grubhub',
    ],
    'education': [
        'coursera', 'udemy', 'masterclass', 'skillshare', 'linkedin learning',
        'duolingo', 'rosetta stone',
    ],
}

# Email subject patterns that indicate subscriptions
SUBSCRIPTION_SUBJECT_PATTERNS = [
    r'subscription\s+(?:confirmation|renewed|active)',
    r'welcome\s+to\s+(?:your|our)\s+(?:premium|plus|pro)',
    r'(?:monthly|annual)\s+(?:payment|invoice|receipt)',
    r'your\s+(?:trial|subscription)\s+(?:has\s+)?(?:ended|expired|renewed)',
    r'(?:billing|payment)\s+(?:confirmation|successful|receipt)',
    r'membership\s+(?:activated|renewed|confirmed)',
]

# Confirmation email patterns (for unsubscribe monitoring)
CANCELLATION_CONFIRMATION_PATTERNS = [
    r'subscription\s+(?:has\s+been\s+)?cancel[led]{2,3}',
    r'successfully\s+unsubscribed',
    r'membership\s+(?:has\s+)?ended',
    r'(?:no\s+longer|not)\s+(?:subscribed|active)',
    r'cancellation\s+(?:is\s+)?confirmed',
    r'subscription\s+terminated',
    r'account\s+closed',
    r'auto[- ]renew(?:al)?\s+(?:disabled|turned\s+off|cancelled)',
]

# Price change patterns
PRICE_CHANGE_PATTERNS = [
    r'price\s+(?:change|increase|update)',
    r'new\s+(?:price|rate)',
    r'subscription\s+(?:price\s+)?(?:increase|going\s+up)',
    r'rate\s+adjustment',
]


def get_service_category(service_name: str) -> str:
    """
    Determine service category from service name
    Returns: Category name or 'Other'
    """
    service_lower = service_name.lower()
    
    for category, services in SERVICE_NAME_PATTERNS.items():
        if any(svc in service_lower for svc in services):
            return category.title()
    
    return 'Other'


def normalize_service_name(raw_name: str) -> str:
    """
    Normalize service name for consistency
    Examples:
        "Netflix Premium" → "Netflix"
        "Spotify Premium Individual" → "Spotify"
        "Adobe Creative Cloud" → "Adobe Creative Cloud"
    """
    # Remove common suffixes
    suffixes = ['premium', 'plus', 'pro', 'basic', 'free', 'trial', 'individual', 'family']
    
    name = raw_name.strip()
    name_lower = name.lower()
    
    for suffix in suffixes:
        if name_lower.endswith(suffix):
            name = name[:len(name)-len(suffix)].strip()
    
    return name.title()


def extract_payment_method(text: str) -> str:
    """
    Extract payment method info (last 4 digits)
    Returns: Last 4 digits or empty string
    """
    patterns = [
        r'(?:card|visa|mastercard|amex|discover)\s+ending\s+in\s+(\d{4})',
        r'\*{4}\s*(\d{4})',
        r'xxxx\s*(\d{4})',
        r'•{4}\s*(\d{4})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return ""


# Service logo URLs (CDN mapping)
SERVICE_LOGOS = {
    'netflix': 'https://cdn.subscout.app/logos/netflix.png',
    'spotify': 'https://cdn.subscout.app/logos/spotify.png',
    'hulu': 'https://cdn.subscout.app/logos/hulu.png',
    'disney': 'https://cdn.subscout.app/logos/disney.png',
    'amazon prime': 'https://cdn.subscout.app/logos/amazon-prime.png',
    'dropbox': 'https://cdn.subscout.app/logos/dropbox.png',
    'adobe': 'https://cdn.subscout.app/logos/adobe.png',
    # Add more as needed...
}


def get_service_logo(service_name: str) -> str:
    """Get logo URL for service"""
    service_lower = service_name.lower()
    
    for key, url in SERVICE_LOGOS.items():
        if key in service_lower:
            return url
    
    # Default logo
    return 'https://cdn.subscout.app/logos/default.png'

