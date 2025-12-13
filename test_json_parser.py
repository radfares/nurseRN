#!/usr/bin/env python3
"""
Test script for robust JSON parser.

Verifies that the parser correctly handles:
- Pure JSON
- JSON + commentary before/after
- Multiple JSON objects (should take first only)
- Malformed JSON
- No JSON at all
"""
import sys
sys.path.insert(0, '/Users/hdz/nurseRN')

from src.utils.json_parser import (
    extract_first_json_object,
    parse_json_robust,
    parse_json_from_response
)

def test_extract_first_json():
    """Test extracting first JSON object from various inputs."""
    
    # Test 1: Pure JSON
    text1 = '{"name": "test", "value": 42}'
    result1 = extract_first_json_object(text1)
    assert result1 == text1, f"Pure JSON failed: {result1}"
    print("✅ Test 1 passed: Pure JSON")
    
    # Test 2: JSON + commentary after
    text2 = '{"name": "test"} This is some extra commentary that should be ignored.'
    result2 = extract_first_json_object(text2)
    assert result2 == '{"name": "test"}', f"JSON + commentary failed: {result2}"
    print("✅ Test 2 passed: JSON + commentary after")
    
    # Test 3: Commentary before JSON
    text3 = 'Here is the result: {"status": "ok", "count": 5}'
    result3 = extract_first_json_object(text3)
    assert result3 == '{"status": "ok", "count": 5}', f"Commentary before JSON failed: {result3}"
    print("✅ Test 3 passed: Commentary before JSON")
    
    # Test 4: Multiple JSON objects (should return first only)
    text4 = '{"first": 1} {"second": 2}'
    result4 = extract_first_json_object(text4)
    assert result4 == '{"first": 1}', f"Multiple JSON failed: {result4}"
    print("✅ Test 4 passed: Multiple JSON objects (first only)")
    
    # Test 5: JSON in markdown code block
    text5 = '''```json
{
  "nested": {
    "value": "test"
  }
}
```'''
    result5 = extract_first_json_object(text5)
    assert '"nested"' in result5, f"Markdown code block failed: {result5}"
    print("✅ Test 5 passed: JSON in markdown code block")
    
    # Test 6: No JSON
    text6 = "This text has no JSON at all"
    result6 = extract_first_json_object(text6)
    assert result6 is None, f"No JSON failed: {result6}"
    print("✅ Test 6 passed: No JSON returns None")
    
    # Test 7: Nested objects
    text7 = '{"outer": {"inner": {"deep": "value"}}, "count": 10}'
    result7 = extract_first_json_object(text7)
    assert result7 == text7, f"Nested objects failed: {result7}"
    print("✅ Test 7 passed: Nested objects")

def test_parse_json_robust():
    """Test robust JSON parsing."""
    
    # Test 1: Valid JSON + commentary
    text1 = 'The answer is: {"result": "success", "data": [1, 2, 3]} Hope this helps!'
    result1 = parse_json_robust(text1, context="test1", log_failures=False)
    assert result1 == {"result": "success", "data": [1, 2, 3]}, f"Parse failed: {result1}"
    print("✅ Parse Test 1: Valid JSON + commentary")
    
    # Test 2: Invalid JSON
    text2 = "Not JSON at all"
    result2 = parse_json_robust(text2, context="test2", log_failures=False)
    assert result2 is None, f"Invalid JSON should return None: {result2}"
    print("✅ Parse Test 2: Invalid JSON returns None")
    
    # Test 3: Multiple JSON objects (first wins)
    text3 = '{"first": "a"} {"second": "b"}'
    result3 = parse_json_robust(text3, context="test3", log_failures=False)
    assert result3 == {"first": "a"}, f"Multiple JSON failed: {result3}"
    print("✅ Parse Test 3: Multiple JSON (first only)")

def test_parse_from_response():
    """Test parsing from response objects."""
    
    # Test 1: Dict response
    response1 = {"already": "dict"}
    result1 = parse_json_from_response(response1, context="test1")
    assert result1 == response1
    print("✅ Response Test 1: Dict passthrough")
    
    # Test 2: String with JSON
    class MockResponse:
        def __init__(self, content):
            self.content = content
    
    response2 = MockResponse('Result: {"parsed": true}')
    result2 = parse_json_from_response(response2, context="test2")
    assert result2 == {"parsed": True}, f"String parsing failed: {result2}"
    print("✅ Response Test 2: String with JSON")
    
    # Test 3: Fallback to text
    response3 = MockResponse('No JSON here')
    result3 = parse_json_from_response(response3, context="test3", fallback_to_text=True)
    assert "text" in result3, f"Fallback failed: {result3}"
    print("✅ Response Test 3: Fallback to text")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Robust JSON Parser")
    print("=" * 60)
    
    try:
        test_extract_first_json()
        print()
        test_parse_json_robust()
        print()
        test_parse_from_response()
        print()
        print("=" * 60)
        print("🎉 ALL TESTS PASSED")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
