"""Test OpenRouter AI client integration."""

import os
import re
from ai_client import query_openrouter, OpenRouterError, DEFAULT_MODEL


def _extract_ai_query(transcript: str) -> str:
    """Extract AI query from transcript, removing AI-related prefixes."""
    text = transcript.strip()
    patterns_to_remove = [
        r"^ai\s*[:]*\s*",
        r"^ask\s+ai\s*[:]*\s*",
        r"^ask\s+the\s+ai\s*[:]*\s*",
    ]
    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip()


def _extract_type_payload(transcript: str) -> str:
    """Extract text to type from transcript, removing 'type' prefix if present."""
    text = transcript.strip()
    if text.lower().startswith("type "):
        return text[5:].strip()
    return text


def test_ai_query():
    """Test OpenRouter AI query."""
    print("Testing OpenRouter AI Client...")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Warning: OPENROUTER_API_KEY not set")
        print("Set it with: export OPENROUTER_API_KEY=your_key")
        print("Skipping AI query test")
        return

    test_queries = [
        "What is Python?",
        "Explain recursion in one sentence",
        "What is 2 + 2?",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            response = query_openrouter(query, model=DEFAULT_MODEL)
            print(f"Response: {response[:100]}...")
        except OpenRouterError as e:
            print(f"Error: {e}")


def test_query_extraction():
    """Test AI query extraction patterns."""
    test_cases = [
        ("AI what is Python", "what is Python"),
        ("ask AI explain quantum physics", "explain quantum physics"),
        ("Ask the AI what is love", "what is love"),
        ("ai: tell me a joke", "tell me a joke"),
        ("Hello world", "Hello world"),
    ]

    print("\nTesting AI query extraction...")
    for input_text, expected in test_cases:
        result = _extract_ai_query(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' → '{result}' (expected: '{expected}')")


def test_type_payload_extraction():
    """Test type payload extraction."""
    test_cases = [
        ("type hello", "hello"),
        ("type hello world", "hello world"),
        ("hello world", "hello world"),
        ("Type with capital", "with capital"),
    ]

    print("\nTesting type payload extraction...")
    for input_text, expected in test_cases:
        result = _extract_type_payload(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{input_text}' → '{result}' (expected: '{expected}')")


if __name__ == "__main__":
    print("=" * 60)
    print("OpenRouter AI Client Tests")
    print("=" * 60)

    test_query_extraction()
    test_type_payload_extraction()
    test_ai_query()

    print("\n" + "=" * 60)
    print("Tests Complete")
    print("=" * 60)
