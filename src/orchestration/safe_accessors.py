"""
Safe Accessor Utilities for RunOutput Objects

This module provides defensive wrappers for accessing fields on RunOutput objects
to prevent crashes when fields are missing or None.

Part of Phase 0: Reliability and Security Foundations
"""

from typing import Any, Optional, List, Dict


def safe_get_content(run_output: Any, default: Optional[str] = None) -> Optional[str]:
    """
    Safely extract content from RunOutput.
    
    Args:
        run_output: The RunOutput object (or any object with a content attribute)
        default: Value to return if content is missing or None
    
    Returns:
        The content as a string, or default if not available
    
    Examples:
        >>> safe_get_content(run_output)
        "Here is the response..."
        >>> safe_get_content(None)
        None
        >>> safe_get_content(run_output, default="")
        ""
    """
    if run_output is None:
        return default
    
    content = getattr(run_output, "content", default)
    
    # If content exists but is None, return default
    if content is None:
        return default
    
    return str(content)


def safe_get_messages(run_output: Any, default: Optional[List] = None) -> List:
    """
    Safely extract messages from RunOutput.
    
    Args:
        run_output: The RunOutput object (or any object with a messages attribute)
        default: Value to return if messages is missing or None
    
    Returns:
        List of messages, or default (empty list if None specified)
    
    Examples:
        >>> safe_get_messages(run_output)
        [Message(...), Message(...)]
        >>> safe_get_messages(None)
        []
        >>> safe_get_messages(run_output, default=[])
        []
    """
    if default is None:
        default = []
    
    if run_output is None:
        return default
    
    messages = getattr(run_output, "messages", default)
    
    # If messages exists but is None or not a list, return default
    if messages is None or not isinstance(messages, list):
        return default
    
    return messages


def safe_get_tools(run_output: Any, default: Optional[List] = None) -> List:
    """
    Safely extract tools from RunOutput.
    
    Args:
        run_output: The RunOutput object (or any object with a tools attribute)
        default: Value to return if tools is missing or None
    
    Returns:
        List of tools, or default (empty list if None specified)
    
    Examples:
        >>> safe_get_tools(run_output)
        [Tool(...), Tool(...)]
        >>> safe_get_tools(None)
        []
    """
    if default is None:
        default = []
    
    if run_output is None:
        return default
    
    tools = getattr(run_output, "tools", default)
    
    # If tools exists but is None or not a list, return default
    if tools is None or not isinstance(tools, list):
        return default
    
    return tools


def safe_get_metadata(run_output: Any, default: Optional[Dict] = None) -> Dict:
    """
    Safely extract metadata from RunOutput.
    
    Args:
        run_output: The RunOutput object (or any object with a metadata attribute)
        default: Value to return if metadata is missing or None
    
    Returns:
        Metadata dictionary, or default (empty dict if None specified)
    
    Examples:
        >>> safe_get_metadata(run_output)
        {"model": "gpt-4o", "tokens": 150}
        >>> safe_get_metadata(None)
        {}
    """
    if default is None:
        default = {}
    
    if run_output is None:
        return default
    
    metadata = getattr(run_output, "metadata", default)
    
    # If metadata exists but is None or not a dict, return default
    if metadata is None or not isinstance(metadata, dict):
        return default
    
    return metadata


def safe_check_has_messages(run_output: Any) -> bool:
    """
    Check if RunOutput has non-empty messages.
    
    This is equivalent to the pattern:
    `if not hasattr(run_output, "messages") or not run_output.messages:`
    
    Args:
        run_output: The RunOutput object to check
    
    Returns:
        True if messages exist and are non-empty, False otherwise
    
    Examples:
        >>> safe_check_has_messages(run_output_with_messages)
        True
        >>> safe_check_has_messages(run_output_without_messages)
        False
        >>> safe_check_has_messages(None)
        False
    """
    if run_output is None:
        return False
    
    if not hasattr(run_output, "messages"):
        return False
    
    messages = run_output.messages
    if not messages:  # None, empty list, or falsy value
        return False
    
    return True
