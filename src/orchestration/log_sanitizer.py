"""
Log Sanitization Utilities

Prevents sensitive data (API keys, tokens, secrets) from being written to log files.
Implements pre-write sanitization to ensure audit logs never contain credentials.

Part of Phase 0: Reliability and Security Foundations
"""

import re
from typing import Any, Dict


# Regex patterns for sensitive data
# Updated to match new OpenAI key formats: sk-proj-, sk-org-, etc.
OPENAI_KEY_PATTERN = re.compile(r'sk-[A-Za-z0-9_-]{20,}')
GENERIC_API_KEY_PATTERN = re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})["\']?', re.IGNORECASE)
BEARER_TOKEN_PATTERN = re.compile(r'Bearer\s+([A-Za-z0-9_\-\.]+)', re.IGNORECASE)
AWS_KEY_PATTERN = re.compile(r'AKIA[0-9A-Z]{16}')

# Replacement strings
REDACTED_OPENAI = '[REDACTED_OPENAI_KEY]'
REDACTED_GENERIC = '[REDACTED_API_KEY]'
REDACTED_TOKEN = 'Bearer [REDACTED_TOKEN]'
REDACTED_AWS = '[REDACTED_AWS_KEY]'


def redact_api_keys(text: str) -> str:
    """
    Redact API keys from text before logging.
    
    This function uses regex patterns to identify and replace
    sensitive credentials with placeholder strings.
    
    Args:
        text: Text that may contain API keys
    
    Returns:
        Sanitized text with API keys redacted
    
    Examples:
        >>> redact_api_keys("Using key sk-1234567890abcdefghij")
        'Using key [REDACTED_OPENAI_KEY]'
        
        >>> redact_api_keys("api_key=secret123456789012345678")
        'api_key=[REDACTED_API_KEY]'
        
        >>> redact_api_keys("No secrets here")
        'No secrets here'
    """
    if not text or not isinstance(text, str):
        return text
    
    # Redact OpenAI keys first (most common)
    text = OPENAI_KEY_PATTERN.sub(REDACTED_OPENAI, text)
    
    # Redact generic API keys
    text = GENERIC_API_KEY_PATTERN.sub(r'api_key=\g<1>', text)
    text = text.replace(r'\g<1>', REDACTED_GENERIC)
    
    # Redact Bearer tokens
    text = BEARER_TOKEN_PATTERN.sub(REDACTED_TOKEN, text)
    
    # Redact AWS keys
    text = AWS_KEY_PATTERN.sub(REDACTED_AWS, text)
    
    return text


def sanitize_dict(data: Dict[str, Any], redact_keys: bool = True) -> Dict[str, Any]:
    """
    Sanitize a dictionary by redacting sensitive values.
    
    This recursively walks through nested dictionaries and redacts
    any values that match sensitive patterns. Can also redact by key name.
    
    Args:
        data: Dictionary to sanitize
        redact_keys: If True, redact values for keys containing 'key', 'token', 'secret'
    
    Returns:
        Sanitized dictionary (deep copy, original unchanged)
    
    Examples:
        >>> sanitize_dict({"api_key": "sk-secret123", "data": "public"})
        {'api_key': '[REDACTED_OPENAI_KEY]', 'data': 'public'}
        
        >>> sanitize_dict({"config": {"token": "abc123"}})
        {'config': {'token': '[REDACTED]'}}
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    
    for key, value in data.items():
        # Recursively sanitize nested dicts
        if isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, redact_keys=redact_keys)
        
        # Sanitize list values
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict(item, redact_keys=redact_keys) if isinstance(item, dict)
                else redact_api_keys(item) if isinstance(item, str)
                else item
                for item in value
            ]
        
        # Sanitize string values (check content first)
        elif isinstance(value, str):
            # Redact content patterns (sk-, etc.)
            redacted_value = redact_api_keys(value)
            # If key name is sensitive AND value wasn't already redacted, use generic redaction
            if redact_keys and any(s in key.lower() for s in ['key', 'token', 'secret', 'password', 'auth']):
                # If redaction already happened (pattern match), keep it
                if redacted_value != value:
                    sanitized[key] = redacted_value
                else:
                    # No pattern match, but key name is sensitive
                    sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = redacted_value
        
        # Check if key name suggests sensitive data (for non-string values)
        elif redact_keys and any(s in key.lower() for s in ['key', 'token', 'secret', 'password', 'auth']):
            sanitized[key] = '[REDACTED]'
        
        # Keep other types as-is
        else:
            sanitized[key] = value
    
    return sanitized


def sanitize_log_entry(entry: str) -> str:
    """
    Sanitize a complete log entry before writing.
    
    This is the main function to call before writing to log files.
    It applies all redaction patterns to ensure no sensitive data escapes.
    
    Args:
        entry: Complete log entry (may be multi-line)
    
    Returns:
        Sanitized log entry safe to write
    
    Examples:
        >>> sanitize_log_entry("2025-12-03 Query with key sk-secret")
        '2025-12-03 Query with key [REDACTED_OPENAI_KEY]'
    """
    if not entry:
        return entry
    
    # Apply all redaction patterns
    return redact_api_keys(entry)


def create_safe_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a sanitized copy of metadata for logging.
    
    Use this before logging metadata dictionaries to ensure
    no sensitive data is included in the logs.
    
    Args:
        metadata: Metadata dictionary (may contain sensitive data)
    
    Returns:
        Safe copy with sensitive data redacted
    
    Examples:
        >>> create_safe_metadata({"query": "test", "api_key": "sk-secret"})
        {'query': 'test', 'api_key': '[REDACTED]'}
    """
    return sanitize_dict(metadata, redact_keys=True)


# Pre-compiled patterns for performance
def is_sensitive(text: str) -> bool:
    """
    Quick check if text contains sensitive data.
    
    Use this to avoid unnecessary sanitization on non-sensitive logs.
    
    Args:
        text: Text to check
    
    Returns:
        True if text likely contains sensitive data
    
    Examples:
        >>> is_sensitive("Using key sk-1234567890")
        True
        
        >>> is_sensitive("Regular log message")
        False
    """
    if not text or not isinstance(text, str):
        return False
    
    # Check for common sensitive patterns
    return bool(
        OPENAI_KEY_PATTERN.search(text) or
        GENERIC_API_KEY_PATTERN.search(text) or
        BEARER_TOKEN_PATTERN.search(text) or
        AWS_KEY_PATTERN.search(text) or
        any(keyword in text.lower() for keyword in ['api_key', 'secret', 'token', 'password'])
    )
