"""
API Key Validation Utilities

Implements the Fail-Fast Pattern for API credential validation.
Validates API keys BEFORE making network requests to save resources
and prevent 401 errors from polluting audit logs.

Part of Phase 0: Reliability and Security Foundations
"""

from typing import Optional


class InvalidAPIKeyError(ValueError):
    """
    Raised when an API key fails validation.
    
    This is a specialized ValueError that provides clear,
    actionable error messages for API key issues.
    """
    pass


def validate_openai_key(key: Optional[str]) -> bool:
    """
    Validate OpenAI API key format.
    
    This performs a BASIC format check (not authentication).
    It prevents obviously invalid keys from reaching the network.
    
    Args:
        key: The API key to validate
    
    Returns:
        True if key passes format validation
    
    Raises:
        InvalidAPIKeyError: If key fails validation with specific reason
    
    Examples:
        >>> validate_openai_key("sk-1234567890abcdefghij")
        True
        
        >>> validate_openai_key(None)
        InvalidAPIKeyError: API key cannot be None
        
        >>> validate_openai_key("")
        InvalidAPIKeyError: API key cannot be empty
        
        >>> validate_openai_key("ak-invalid")
        InvalidAPIKeyError: OpenAI API key must start with 'sk-'
    """
    # Check for None
    if key is None:
        raise InvalidAPIKeyError(
            "API key cannot be None. "
            "Set OPENAI_API_KEY environment variable or provide key explicitly."
        )
    
    # Check for empty string
    if not key or not isinstance(key, str):
        raise InvalidAPIKeyError(
            "API key must be a non-empty string. "
            "Got: {!r}".format(key)
        )
    
    # Check prefix (OpenAI keys start with 'sk-')
    if not key.startswith("sk-"):
        raise InvalidAPIKeyError(
            "OpenAI API key must start with 'sk-'. "
            "Got key starting with: {!r}. "
            "Check your OPENAI_API_KEY environment variable.".format(key[:5])
        )
    
    # Check minimum length (OpenAI keys are much longer than 10 chars)
    if len(key) < 20:
        raise InvalidAPIKeyError(
            "OpenAI API key is too short (got {} characters, expected at least 20). "
            "This may be a truncated or test key.".format(len(key))
        )
    
    return True


def validate_or_fail(key: Optional[str], service: str = "OpenAI") -> None:
    """
    Validate API key and raise exception if invalid (Fail-Fast pattern).
    
    This is a convenience wrapper for use in agent initialization.
    It validates the key and raises an exception immediately if invalid,
    preventing any network calls from being attempted.
    
    Args:
        key: The API key to validate
        service: Name of the service (for error messages)
    
    Raises:
        InvalidAPIKeyError: If validation fails
    
    Examples:
        >>> validate_or_fail("sk-1234567890abcdefghij")
        # No exception, execution continues
        
        >>> validate_or_fail("invalid")
        InvalidAPIKeyError: OpenAI API key must start with 'sk-'...
    """
    try:
        validate_openai_key(key)
    except InvalidAPIKeyError as e:
        # Re-raise with service context
        raise InvalidAPIKeyError(
            f"{service} API key validation failed: {str(e)}"
        ) from e


# Future: Add validators for other services
# def validate_serpapi_key(key: str) -> bool:
#     """Validate SerpAPI key format"""
#     pass
#
# def validate_pubmed_key(key: str) -> bool:
#     """Validate PubMed API key format (if needed)"""
#     pass
