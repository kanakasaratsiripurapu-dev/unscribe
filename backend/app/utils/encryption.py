"""
Token encryption utilities using Fernet (symmetric encryption)
"""
from cryptography.fernet import Fernet
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def get_encryption_key() -> bytes:
    """Get encryption key from settings or generate a new one"""
    key = settings.ENCRYPTION_KEY
    
    if not key:
        logger.warning("ENCRYPTION_KEY not set, generating new key (tokens will not persist across restarts)")
        key = Fernet.generate_key().decode()
    
    # If key is a string, encode it
    if isinstance(key, str):
        # If it's already a valid Fernet key, use it directly
        try:
            return key.encode() if len(key) == 44 else Fernet.generate_key()
        except:
            return Fernet.generate_key()
    
    return key


def encrypt_token(token: str) -> str:
    """
    Encrypt a token (e.g., Gmail refresh token) for storage
    """
    try:
        key = get_encryption_key()
        f = Fernet(key)
        encrypted = f.encrypt(token.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Token encryption failed: {e}")
        raise


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt a stored token
    """
    try:
        key = get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_token.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Token decryption failed: {e}")
        raise

