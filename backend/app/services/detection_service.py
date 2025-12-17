"""
Subscription detection and extraction service
Combines rule-based patterns with LLM extraction
"""
import re
import json
from typing import Dict, Optional, List, Any
from datetime import datetime
import logging

# Conditional imports for LLM providers
try:
    from openai import AsyncOpenAI  # type: ignore[import-not-found]
except ImportError:
    AsyncOpenAI = None  # type: ignore

try:
    from anthropic import AsyncAnthropic  # type: ignore[import-not-found]
except ImportError:
    AsyncAnthropic = None  # type: ignore

from app.config import settings
from app.utils.patterns import (
    PRICE_PATTERNS,
    BILLING_PERIOD_PATTERNS,
    DATE_PATTERNS,
    UNSUBSCRIBE_LINK_PATTERNS,
    SUBSCRIPTION_KEYWORDS
)
from app.utils.llm_prompt import build_extraction_prompt

logger = logging.getLogger(__name__)


class SubscriptionDetectionService:
    """Service for detecting and extracting subscription information"""
    
    def __init__(self):
        self.llm_provider = settings.LLM_PROVIDER
        self.openai_client = None
        self.anthropic_client = None
        self.model = settings.LLM_MODEL
        
        if self.llm_provider == "openai":
            if AsyncOpenAI is None:
                raise ImportError("openai package is not installed. Install it with: pip install openai")
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        elif self.llm_provider == "anthropic":
            if AsyncAnthropic is None:
                raise ImportError("anthropic package is not installed. Install it with: pip install anthropic")
            self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def detect_subscription(self, email_data: Dict) -> Optional[Dict]:
        """
        Main detection pipeline: Rules first, then LLM if needed
        
        Args:
            email_data: Extracted email content from Gmail
        
        Returns:
            Extracted subscription data or None if not a subscription
        """
        # Stage 1: Check if email is subscription-related
        if not self._is_subscription_email(email_data):
            logger.debug(f"Email {email_data['id']} not subscription-related (keyword check)")
            return None
        
        # Stage 2: Try rule-based extraction first (fast & cheap)
        rule_result = await self._rule_based_extraction(email_data)
        
        if rule_result and rule_result.get('confidence', 0) >= 0.7:
            logger.info(f"Email {email_data['id']} extracted via rules (confidence: {rule_result['confidence']})")
            rule_result['detected_by'] = 'rule_based'
            return rule_result
        
        # Stage 3: Use LLM for complex extraction
        logger.info(f"Email {email_data['id']} requires LLM extraction")
        llm_result = await self._llm_extraction(email_data)
        
        if llm_result and llm_result.get('confidence', 0) >= settings.DETECTION_CONFIDENCE_THRESHOLD:
            llm_result['detected_by'] = 'llm'
            return llm_result
        
        logger.debug(f"Email {email_data['id']} confidence too low ({llm_result.get('confidence', 0)})")
        return None
    
    def _is_subscription_email(self, email_data: Dict) -> bool:
        """
        Quick check: Does email contain subscription-related keywords?
        """
        text = (
            email_data.get('subject', '') + ' ' +
            email_data.get('snippet', '') + ' ' +
            email_data.get('body_text', '')[:500]  # First 500 chars
        ).lower()
        
        # Check for subscription keywords
        keyword_count = sum(1 for kw in SUBSCRIPTION_KEYWORDS if kw in text)
        
        # Need at least 2 keywords to be considered subscription-related
        return keyword_count >= 2
    
    async def _rule_based_extraction(self, email_data: Dict) -> Optional[Dict]:
        """
        Extract subscription data using regex patterns
        """
        text = email_data.get('body_text', '') or email_data.get('body_html', '')
        subject = email_data.get('subject', '')
        sender = email_data.get('from', '')
        
        # Extract fields
        price = self._extract_price(text)
        currency = self._extract_currency(text)
        billing_period = self._extract_billing_period(text)
        renewal_date = self._extract_date(text)
        unsubscribe_link = self._extract_unsubscribe_link(text + email_data.get('body_html', ''))
        service_name = self._extract_service_name(subject, sender, text)
        
        # Calculate confidence based on how many required fields were found
        required_fields = [price, billing_period, unsubscribe_link, service_name]
        found_fields = sum(1 for field in required_fields if field)
        confidence = found_fields / len(required_fields) if required_fields else 0
        
        # Need at least service name and price for valid detection
        if not service_name or not price:
            return None
        
        return {
            "service_name": service_name,
            "price": price,
            "currency": currency or "USD",
            "billing_period": billing_period or "monthly",
            "next_renewal_date": renewal_date,
            "unsubscribe_link": unsubscribe_link,
            "confidence": round(confidence, 2),
            "source_email_id": email_data['id'],
            "detection_method": "rule_based"
        }
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price using regex patterns"""
        for pattern in PRICE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Extract numeric value
                    price_str = match.group(1).replace(',', '')
                    return float(price_str)
                except:
                    continue
        return None
    
    def _extract_currency(self, text: str) -> Optional[str]:
        """Extract currency code"""
        # Check for currency symbols/codes
        if '$' in text:
            return 'USD'
        elif '€' in text or 'EUR' in text:
            return 'EUR'
        elif '£' in text or 'GBP' in text:
            return 'GBP'
        return None
    
    def _extract_billing_period(self, text: str) -> Optional[str]:
        """Extract billing frequency"""
        text_lower = text.lower()
        
        for period, patterns in BILLING_PERIOD_PATTERNS.items():
            if any(re.search(pattern, text_lower) for pattern in patterns):
                return period
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract renewal date"""
        for pattern in DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                try:
                    # Try to parse various date formats
                    date_str = match.group(0)
                    # This is simplified - in production, use dateutil.parser
                    return date_str
                except:
                    continue
        return None
    
    def _extract_unsubscribe_link(self, text: str) -> Optional[str]:
        """Extract unsubscribe/cancel link"""
        for pattern in UNSUBSCRIBE_LINK_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def _extract_service_name(self, subject: str, sender: str, text: str) -> Optional[str]:
        """
        Extract service name from email
        Priority: subject > sender domain > body text
        """
        # Try to extract from subject
        subject_lower = subject.lower()
        common_services = [
            'netflix', 'spotify', 'hulu', 'disney', 'amazon prime',
            'dropbox', 'google', 'microsoft', 'adobe', 'apple',
            'youtube', 'linkedin', 'github', 'slack', 'zoom'
        ]
        
        for service in common_services:
            if service in subject_lower:
                return service.title()
        
        # Try to extract from sender domain
        if '@' in sender:
            domain = sender.split('@')[1].split('.')[0]
            return domain.title()
        
        # Fallback: Look for capitalized words in text (company names)
        words = re.findall(r'\b[A-Z][a-z]+\b', text[:200])
        if words:
            return words[0]
        
        return "Unknown Service"
    
    async def _llm_extraction(self, email_data: Dict) -> Optional[Dict]:
        """
        Use LLM (GPT-4 or Claude) to extract subscription data
        """
        # Build prompt
        email_text = f"""
Subject: {email_data['subject']}
From: {email_data['from']}

{email_data['body_text'][:2000]}
"""
        
        prompt = build_extraction_prompt(email_data['subject'], email_data['body_text'][:2000])
        
        try:
            if self.llm_provider == "openai":
                response = await self._call_openai(prompt)
            else:
                response = await self._call_anthropic(prompt)
            
            # Parse JSON response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            extracted_data = json.loads(response)
            
            # Validate extracted data
            if self._validate_extraction(extracted_data, email_data):
                extracted_data['source_email_id'] = email_data['id']
                extracted_data['detection_method'] = 'llm'
                return extracted_data
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")
        
        return None
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        if self.openai_client is None:
            raise RuntimeError("OpenAI client not initialized. Check that openai package is installed.")
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS
        )
        return response.choices[0].message.content.strip()
    
    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        if self.anthropic_client is None:
            raise RuntimeError("Anthropic client not initialized. Check that anthropic package is installed.")
        message = await self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    
    def _validate_extraction(self, extracted: Dict, email_data: Dict) -> bool:
        """
        Validate that extracted data is reasonable
        """
        # Required fields
        if not extracted.get('service_name'):
            return False
        
        if not extracted.get('price') or extracted['price'] <= 0:
            return False
        
        # Validate unsubscribe link exists in email
        unsub_link = extracted.get('unsubscribe_link', '')
        if unsub_link:
            email_html = email_data.get('body_html', '')
            email_text = email_data.get('body_text', '')
            
            # Check if link appears in email (prevent hallucinations)
            if unsub_link not in email_html and unsub_link not in email_text:
                logger.warning(f"Unsubscribe link not found in email: {unsub_link}")
                extracted['confidence'] = max(0, extracted.get('confidence', 0.5) - 0.3)
        
        # Validate domain match
        sender = email_data.get('from', '')
        if '@' in sender and unsub_link:
            sender_domain = sender.split('@')[1]
            if sender_domain not in unsub_link:
                logger.warning(f"Domain mismatch: {sender_domain} not in {unsub_link}")
                extracted['confidence'] = max(0, extracted.get('confidence', 0.5) - 0.2)
        
        return True


# Global instance
detection_service = SubscriptionDetectionService()

