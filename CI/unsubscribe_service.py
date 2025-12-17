"""
Unsubscribe/cancellation service
Handles automated cancellation attempts and confirmation monitoring
"""
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging
from urllib.parse import urlparse

import httpx
from playwright.async_api import async_playwright

from app.config import settings
from app.services.gmail_service import gmail_service
from app.utils.patterns import CANCELLATION_CONFIRMATION_PATTERNS

logger = logging.getLogger(__name__)


class UnsubscribeService:
    """Service for managing subscription cancellations"""
    
    def __init__(self):
        self.timeout = settings.UNSUBSCRIBE_TIMEOUT_SECONDS
        self.max_retries = settings.UNSUBSCRIBE_MAX_RETRIES
    
    async def initiate_cancellation(
        self,
        subscription_id: str,
        unsubscribe_url: str,
        user_access_token: str
    ) -> Dict:
        """
        Attempt to cancel subscription
        
        Returns:
            {
                "status": "success"|"manual_required"|"failed",
                "action_type": "automated"|"manual_link"|"manual_phone",
                "message": "...",
                "requires_user_action": bool,
                "instructions": "..." (if manual action needed)
            }
        """
        logger.info(f"Initiating cancellation for subscription {subscription_id}")
        
        # Analyze unsubscribe link type
        link_type = self._analyze_unsubscribe_link(unsubscribe_url)
        
        if link_type == "direct":
            # Simple HTTP GET cancellation
            result = await self._direct_cancellation(unsubscribe_url)
        
        elif link_type == "form":
            # Requires form submission
            result = await self._form_cancellation(unsubscribe_url)
        
        elif link_type == "login_required":
            # User must log in first
            result = {
                "status": "manual_required",
                "action_type": "manual_link",
                "message": "Login required to cancel",
                "requires_user_action": True,
                "instructions": f"Please visit {unsubscribe_url} and log in to cancel your subscription."
            }
        
        else:
            # Unknown or complex cancellation flow
            result = {
                "status": "manual_required",
                "action_type": "manual_link",
                "message": "Manual cancellation required",
                "requires_user_action": True,
                "instructions": f"Please visit {unsubscribe_url} to cancel your subscription."
            }
        
        return result
    
    def _analyze_unsubscribe_link(self, url: str) -> str:
        """
        Analyze unsubscribe link to determine cancellation type
        Returns: "direct", "form", "login_required", "unknown"
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        query = parsed.query.lower()
        
        # Direct cancellation indicators (usually token-based)
        if any(param in query for param in ['token=', 'id=', 'email=', 'unsubscribe=']):
            return "direct"
        
        # Login required indicators
        if any(keyword in path for keyword in ['login', 'signin', 'account']):
            return "login_required"
        
        # Form-based indicators
        if any(keyword in path for keyword in ['cancel', 'manage', 'settings']):
            return "form"
        
        return "unknown"
    
    async def _direct_cancellation(self, url: str) -> Dict:
        """
        Attempt direct cancellation via HTTP GET
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, follow_redirects=True)
                
                # Check response for success indicators
                success_keywords = [
                    'successfully unsubscribed',
                    'unsubscribe successful',
                    'you have been unsubscribed',
                    'subscription cancelled',
                    'cancellation confirmed'
                ]
                
                response_text = response.text.lower()
                is_success = any(kw in response_text for kw in success_keywords)
                
                if is_success or response.status_code == 200:
                    return {
                        "status": "success",
                        "action_type": "automated",
                        "message": "Cancellation link visited successfully",
                        "requires_user_action": False,
                        "http_status": response.status_code
                    }
                else:
                    return {
                        "status": "failed",
                        "action_type": "automated",
                        "message": f"Unexpected response from cancellation link (HTTP {response.status_code})",
                        "requires_user_action": True,
                        "http_status": response.status_code
                    }
        
        except Exception as e:
            logger.error(f"Direct cancellation failed: {e}")
            return {
                "status": "failed",
                "action_type": "automated",
                "message": f"Error accessing cancellation link: {str(e)}",
                "requires_user_action": True
            }
    
    async def _form_cancellation(self, url: str) -> Dict:
        """
        Attempt form-based cancellation using headless browser
        WARNING: This is complex and may not work for all sites
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Navigate to cancellation page
                await page.goto(url, timeout=self.timeout * 1000)
                
                # Look for cancel/confirm buttons
                cancel_button_selectors = [
                    'button:has-text("Cancel")',
                    'button:has-text("Unsubscribe")',
                    'button:has-text("Confirm")',
                    'input[type="submit"][value*="cancel"]',
                    'a:has-text("Cancel Subscription")'
                ]
                
                for selector in cancel_button_selectors:
                    try:
                        button = await page.wait_for_selector(selector, timeout=5000)
                        if button:
                            await button.click()
                            await page.wait_for_timeout(2000)  # Wait for response
                            
                            # Check if cancellation was successful
                            content = await page.content()
                            if any(kw in content.lower() for kw in [
                                'successfully cancelled',
                                'unsubscribed',
                                'cancellation confirmed'
                            ]):
                                await browser.close()
                                return {
                                    "status": "success",
                                    "action_type": "automated",
                                    "message": "Form-based cancellation completed",
                                    "requires_user_action": False
                                }
                    except:
                        continue
                
                await browser.close()
                
                # If we got here, couldn't find/click cancel button
                return {
                    "status": "manual_required",
                    "action_type": "manual_link",
                    "message": "Could not complete automated cancellation",
                    "requires_user_action": True,
                    "instructions": f"Please visit {url} and complete the cancellation manually."
                }
        
        except Exception as e:
            logger.error(f"Form cancellation failed: {e}")
            return {
                "status": "failed",
                "action_type": "automated",
                "message": f"Automated cancellation failed: {str(e)}",
                "requires_user_action": True
            }
    
    async def monitor_confirmation(
        self,
        service_domain: str,
        user_access_token: str,
        start_date: datetime,
        days_to_monitor: int = 7
    ) -> Optional[Dict]:
        """
        Monitor user's inbox for cancellation confirmation email
        
        Returns:
            Confirmation email details if found, None otherwise
        """
        logger.info(f"Monitoring for confirmation from {service_domain}")
        
        # Search for emails from service
        emails = await gmail_service.search_emails_by_sender(
            access_token=user_access_token,
            sender_domain=service_domain,
            after_date=start_date,
            max_results=20
        )
        
        # Check each email for confirmation language
        for email in emails:
            if self._is_cancellation_confirmation(email):
                return {
                    "confirmed": True,
                    "confirmation_email_id": email['id'],
                    "confirmation_date": email['date'],
                    "confirmation_subject": email['subject']
                }
        
        return None
    
    def _is_cancellation_confirmation(self, email: Dict) -> bool:
        """
        Check if email contains cancellation confirmation language
        """
        text = (
            email.get('subject', '') + ' ' +
            email.get('snippet', '') + ' ' +
            email.get('body_text', '')[:500]
        ).lower()
        
        import re
        for pattern in CANCELLATION_CONFIRMATION_PATTERNS:
            if re.search(pattern, text):
                return True
        
        return False
    
    async def get_manual_instructions(
        self,
        service_name: str,
        unsubscribe_url: str
    ) -> str:
        """
        Generate user-friendly manual cancellation instructions
        """
        instructions = f"""
To cancel your {service_name} subscription:

1. Visit: {unsubscribe_url}
2. Log in to your account if required
3. Look for "Cancel Subscription" or "Manage Subscription" options
4. Follow the on-screen instructions to complete cancellation

If you need help, you can:
- Contact {service_name} customer support
- Check their help center for cancellation guides
- Look for a "Contact Us" or "Support" link on their website

We'll continue monitoring your inbox for a confirmation email.
"""
        return instructions.strip()


# Global instance
unsubscribe_service = UnsubscribeService()
