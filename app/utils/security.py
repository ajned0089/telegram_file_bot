"""
Security utilities for the bot.
"""
import os
import logging
import secrets
import string
import hashlib
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Generate a secret key for encryption if not exists
def get_or_create_encryption_key(key_file: str = "encryption.key") -> bytes:
    """Get or create encryption key."""
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        return key

# Create a Fernet instance with the key
ENCRYPTION_KEY = get_or_create_encryption_key()
FERNET = Fernet(ENCRYPTION_KEY)

def encrypt_file(file_path: str, password: Optional[str] = None) -> str:
    """Encrypt a file."""
    # Read file
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    # Encrypt file
    if password:
        # Derive key from password
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(file_data)
        
        # Prepend salt to encrypted data
        encrypted_data = salt + encrypted_data
    else:
        # Use default key
        encrypted_data = FERNET.encrypt(file_data)
    
    # Write encrypted file
    encrypted_path = f"{file_path}.enc"
    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)
    
    return encrypted_path

def decrypt_file(encrypted_path: str, output_path: str, password: Optional[str] = None) -> bool:
    """Decrypt a file."""
    try:
        # Read encrypted file
        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()
        
        # Decrypt file
        if password:
            # Extract salt from encrypted data
            salt = encrypted_data[:16]
            encrypted_data = encrypted_data[16:]
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
        else:
            # Use default key
            decrypted_data = FERNET.decrypt(encrypted_data)
        
        # Write decrypted file
        with open(output_path, "wb") as f:
            f.write(decrypted_data)
        
        return True
    except Exception as e:
        logging.error(f"Error decrypting file: {e}")
        return False

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_api_key() -> str:
    """Generate an API key."""
    return f"api_{generate_secure_token(32)}"

def validate_api_key(api_key: str, db_api_key: str) -> bool:
    """Validate an API key."""
    return secrets.compare_digest(api_key, db_api_key)

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename."""
    # Remove potentially dangerous characters
    forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in forbidden_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        name = name[:255 - len(ext)]
        filename = name + ext
    
    return filename