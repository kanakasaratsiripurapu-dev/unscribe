"""
Gmail API integration service
Handles OAuth flow, token management, and email fetching
"""
import base64
import asyncio
from typing import List, Dict, Optional, AsyncGenerator, Tuple
from datetime import datetime, timedelta
import logging

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httpx

from app.config import settings
from app.utils.encryption import encrypt_token, decrypt_token

logger = logging.getLogger(__name__)


class GmailService:
    """Service for interacting with Gmail API"""
    
    def __init__(self):
        self.scopes = settings.GMAIL_SCOPES
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    def create_oauth_flow(self) -> Tuple[str, str]:
        """
        Create OAuth flow and return authorization URL
        Returns: (auth_url, state)
        """
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.scopes,
            redirect_uri=self.redirect_uri
        )
        
        auth_url, state = flow.authorization_url(
            access_type='offline',  # Get refresh token
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        
        return auth_url, state
    
    async def exchange_code_for_tokens(self, code: str, state: str) -> Dict:
        """
        Exchange authorization code for access and refresh tokens
        Returns: {access_token, refresh_token, user_info}
        
        Uses direct HTTP request to Google's token endpoint for reliability.
        The redirect_uri must match EXACTLY what was used in the authorization URL.
        """
        logger.info(f"Token exchange - Redirect URI: '{self.redirect_uri}'")
        logger.info(f"Token exchange - Code length: {len(code)}")
        logger.info(f"Token exchange - Client ID: {self.client_id[:30]}...")
        
        # Use direct HTTP request - this is more reliable than Flow library
        # for stateless token exchanges
        return await self._exchange_code_direct(code)
    
    async def _exchange_code_direct(self, code: str) -> Dict:
        """Direct HTTP request to Google token endpoint"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Prepare token exchange request
            # redirect_uri MUST match exactly what was used in authorization URL
            token_request_data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,  # Critical: must match auth URL exactly
                "grant_type": "authorization_code",
            }
            
            logger.debug(f"Token request data keys: {list(token_request_data.keys())}")
            logger.debug(f"Redirect URI being sent: '{token_request_data['redirect_uri']}'")
            
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data=token_request_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Log full response for debugging
            logger.info(f"Token exchange response status: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Token exchange failed - Status: {response.status_code}")
                logger.error(f"Error response: {error_text}")
                logger.error(f"Request redirect_uri: '{self.redirect_uri}'")
                logger.error(f"Request client_id: {self.client_id}")
                
                try:
                    error_json = response.json()
                    error_description = error_json.get("error_description", "Unknown error")
                    error_code = error_json.get("error", "unknown")
                    error_msg = f"({error_code}) {error_description}"
                    
                    # Provide more helpful error messages
                    if "redirect_uri_mismatch" in error_description.lower() or error_code == "redirect_uri_mismatch":
                        error_msg += f". Ensure redirect URI '{self.redirect_uri}' matches exactly in Google Cloud Console."
                    elif "invalid_grant" in error_code.lower():
                        error_msg += ". This usually means the authorization code was already used or expired. Start a fresh OAuth flow."
                    
                    logger.error(f"Parsed error: {error_msg}")
                    raise ValueError(error_msg)
                except (ValueError, KeyError, Exception) as parse_error:
                    # If JSON parsing fails, use raw text
                    logger.error(f"Could not parse error as JSON: {parse_error}")
                    raise ValueError(f"Token exchange failed: {error_text}")
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            if not access_token:
                raise ValueError("No access token received in response")
            
            if not refresh_token:
                raise ValueError("No refresh token received. Make sure 'prompt=consent' is used in authorization URL to get a refresh token.")
            
            # Get user info
            user_info = await self._get_user_info(access_token)
            
            logger.info(f"Token exchange successful for user: {user_info.get('email')}")
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_info": user_info
            }
    
    async def _get_user_info(self, access_token: str) -> Dict:
        """Fetch user profile info from Google"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    def get_gmail_service(self, access_token: str):
        """Create Gmail API service client"""
        credentials = Credentials(token=access_token)
        return build('gmail', 'v1', credentials=credentials)
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        Refresh expired access token using refresh token
        Returns: new access token
        """
        # Decrypt refresh token if needed
        try:
            decrypted_token = decrypt_token(refresh_token)
        except:
            decrypted_token = refresh_token
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": decrypted_token,
                    "grant_type": "refresh_token"
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["access_token"]
    
    async def fetch_emails(
        self,
        access_token: str,
        query: str = None,
        max_results: int = 500,
        page_token: str = None
    ) -> Dict:
        """
        Fetch emails matching query with pagination
        
        Args:
            access_token: Google access token
            query: Gmail search query (e.g., "category:updates")
            max_results: Max emails per page
            page_token: Token for next page
        
        Returns:
            {
                "messages": [{"id": "...", "threadId": "..."}],
                "nextPageToken": "...",
                "resultSizeEstimate": 1000
            }
        """
        service = self.get_gmail_service(access_token)
        
        try:
            result = service.users().messages().list(
                userId='me',
                q=query or settings.EMAIL_SEARCH_QUERY,
                maxResults=max_results,
                pageToken=page_token
            ).execute()
            
            return result
        
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            raise
    
    async def get_email_details(
        self,
        access_token: str,
        message_id: str
    ) -> Dict:
        """
        Fetch full email details including body
        
        Returns:
            {
                "id": "...",
                "threadId": "...",
                "snippet": "...",
                "payload": {
                    "headers": [...],
                    "body": {"data": "base64_encoded"},
                    "parts": [...]
                },
                "internalDate": "..."
            }
        """
        service = self.get_gmail_service(access_token)
        
        try:
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'  # Get full message including body
            ).execute()
            
            return message
        
        except HttpError as error:
            logger.error(f"Error fetching email {message_id}: {error}")
            raise
    
    def extract_email_content(self, message: Dict) -> Dict:
        """
        Extract useful content from Gmail message object
        
        Returns:
            {
                "id": "...",
                "date": datetime,
                "from": "sender@example.com",
                "subject": "...",
                "snippet": "...",
                "body_text": "...",
                "body_html": "..."
            }
        """
        # Extract headers
        headers = {
            header['name']: header['value']
            for header in message['payload'].get('headers', [])
        }
        
        # Parse date
        date_str = headers.get('Date', '')
        try:
            from email.utils import parsedate_to_datetime
            date = parsedate_to_datetime(date_str)
        except:
            date = None
        
        # Extract body
        body_text = ""
        body_html = ""
        
        def get_body_from_parts(parts):
            """Recursively extract body from message parts"""
            text = ""
            html = ""
            
            for part in parts:
                mime_type = part.get('mimeType', '')
                
                if mime_type == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        text += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                
                elif mime_type == 'text/html':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        html += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                
                # Handle nested parts
                if 'parts' in part:
                    nested_text, nested_html = get_body_from_parts(part['parts'])
                    text += nested_text
                    html += nested_html
            
            return text, html
        
        # Check if body is directly in payload
        if 'body' in message['payload'] and message['payload']['body'].get('data'):
            body_text = base64.urlsafe_b64decode(
                message['payload']['body']['data']
            ).decode('utf-8', errors='ignore')
        
        # Or extract from parts
        elif 'parts' in message['payload']:
            body_text, body_html = get_body_from_parts(message['payload']['parts'])
        
        return {
            "id": message['id'],
            "thread_id": message.get('threadId'),
            "date": date,
            "from": headers.get('From', ''),
            "to": headers.get('To', ''),
            "subject": headers.get('Subject', ''),
            "snippet": message.get('snippet', ''),
            "body_text": body_text,
            "body_html": body_html,
            "labels": message.get('labelIds', [])
        }
    
    async def batch_fetch_emails(
        self,
        access_token: str,
        message_ids: List[str],
        batch_size: int = 100
    ) -> AsyncGenerator[Dict, None]:
        """
        Fetch multiple emails in batches for efficiency
        
        Yields: Extracted email content dicts
        """
        for i in range(0, len(message_ids), batch_size):
            batch = message_ids[i:i + batch_size]
            
            # Fetch emails in parallel
            tasks = [
                self.get_email_details(access_token, msg_id)
                for msg_id in batch
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error in batch fetch: {result}")
                    continue
                
                try:
                    extracted = self.extract_email_content(result)
                    yield extracted
                except Exception as e:
                    logger.error(f"Error extracting email content: {e}")
                    continue
            
            # Rate limiting: sleep between batches
            await asyncio.sleep(0.5)
    
    async def search_emails_by_sender(
        self,
        access_token: str,
        sender_domain: str,
        after_date: datetime = None,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search for emails from a specific sender (for confirmation emails)
        
        Args:
            sender_domain: e.g., "netflix.com"
            after_date: Only emails after this date
            max_results: Max emails to return
        """
        query = f"from:@{sender_domain}"
        
        if after_date:
            date_str = after_date.strftime('%Y/%m/%d')
            query += f" after:{date_str}"
        
        result = await self.fetch_emails(
            access_token=access_token,
            query=query,
            max_results=max_results
        )
        
        message_ids = [msg['id'] for msg in result.get('messages', [])]
        
        emails = []
        async for email in self.batch_fetch_emails(access_token, message_ids):
            emails.append(email)
        
        return emails


# Global instance
gmail_service = GmailService()

