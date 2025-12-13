"""
Robust JSON Parser with Logging and Debug Support

Fixes "Failed to parse cleaned JSON: Extra data" errors by:
1. Logging raw LLM output to file for debugging
2. Extracting ONLY the first complete JSON object (ignoring commentary)
3. Providing detailed error messages with context

Created: 2025-12-12 (Phase 3 - JSON Parsing Reliability)
"""
import json
import re
import logging
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def extract_first_json_object(text: str) -> Optional[str]:
    """
    Extract ONLY the first complete JSON object from text.
    
    Ignores:
    - Commentary before/after the JSON
    - Multiple JSON objects (only returns first)
    - JSON arrays with trailing text
    
    Args:
        text: Raw text that may contain JSON + commentary
        
    Returns:
        First complete JSON object as string, or None if not found
    """
    # Remove markdown code blocks first
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        # Try to extract from any code block
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            text = match.group(1)
    
    # Find first { and matching }
    start_idx = text.find("{")
    if start_idx == -1:
        return None
    
    brace_count = 0
    for i in range(start_idx, len(text)):
        if text[i] == "{":
            brace_count += 1
        elif text[i] == "}":
            brace_count -= 1
            if brace_count == 0:
                # Found matching closing brace
                return text[start_idx:i+1]
    
    return None


def log_raw_llm_output(raw_text: str, context: str = "unknown") -> Path:
    """
    Log raw LLM output to file for debugging.
    
    Args:
        raw_text: Raw model output
        context: Context string (e.g., "agent_name", "task_id")
        
    Returns:
        Path to the log file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"llm_raw_{context}_{timestamp}.txt"
    filepath = Path("/tmp") / filename
    
    try:
        filepath.write_text(raw_text, encoding="utf-8")
        logger.debug(f"Logged raw LLM output to: {filepath}")
    except Exception as e:
        logger.warning(f"Failed to log raw LLM output: {e}")
    
    return filepath


def parse_json_robust(
    raw_text: str, 
    context: str = "unknown",
    log_failures: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Robustly parse JSON from LLM output with logging and debugging.
    
    Strategy:
    1. Log raw output to /tmp for debugging
    2. Extract first complete JSON object only
    3. Parse and return, or None if failed
    
    Args:
        raw_text: Raw LLM output (may include JSON + commentary)
        context: Context for logging (e.g., agent name, task ID)
        log_failures: Whether to log raw output on parse failure
        
    Returns:
        Parsed JSON dict, or None if parsing failed
    """
    if not raw_text or not isinstance(raw_text, str):
        return None
    
    # Extract first JSON object
    json_str = extract_first_json_object(raw_text)
    
    if not json_str:
        if log_failures:
            log_path = log_raw_llm_output(raw_text, f"{context}_no_json_found")
            logger.warning(
                f"No JSON object found in output. Context: {context}. "
                f"Raw output logged to: {log_path}"
            )
        return None
    
    # Try to parse
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        if log_failures:
            log_path = log_raw_llm_output(raw_text, f"{context}_parse_failed")
            logger.error(
                f"JSON parse failed. Context: {context}. Error: {e}. "
                f"Raw output logged to: {log_path}"
            )
        return None


def parse_json_from_response(
    response: Any,
    context: str = "unknown",
    fallback_to_text: bool = True
) -> Dict[str, Any]:
    """
    Extract and parse JSON from various response object types.
    
    Handles:
    - Pydantic models (model_dump())
    - Dict responses
    - RunOutput objects (content attribute)
    - String responses
    
    Args:
        response: Agent response object
        context: Context for logging
        fallback_to_text: If True, return {"text": content} on parse failure
        
    Returns:
        Parsed dict or {"text": ...} fallback
    """
    # Handle Pydantic models
    if hasattr(response, 'model_dump'):
        return response.model_dump()
    elif hasattr(response, 'dict'):
        return response.dict()
    
    # Handle dict responses
    if isinstance(response, dict):
        return response
    
    # Extract content string
    content = None
    if hasattr(response, 'content'):
        content = response.content
    elif hasattr(response, 'messages') and response.messages:
        last_msg = response.messages[-1]
        content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    else:
        content = str(response)
    
    # Try robust JSON parsing
    if content and isinstance(content, str):
        parsed = parse_json_robust(content, context=context, log_failures=True)
        if parsed:
            return parsed
    
    # Fallback
    if fallback_to_text:
        return {"text": content if content else str(response)}
    else:
        return {}
