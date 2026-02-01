"""OpenRouter AI client for querying language models."""

import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemma-2-9b-it"
CHEAP_MODELS = [
    "google/gemma-2-9b-it",
    "meta-llama/llama-3.1-8b-instruct",
    "google/gemma-2-27b-it",
]


class OpenRouterError(Exception):
    pass


def query_openrouter(
    query: str,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """Send a query to OpenRouter API and return the response.

    Args:
        query: User's question or query text
        model: Model to use (defaults to DEFAULT_MODEL)
        api_key: OpenRouter API key (defaults to env variable)

    Returns:
        AI response text

    Raises:
        OpenRouterError: If API request fails
    """
    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise OpenRouterError("Missing OPENROUTER_API_KEY")

    selected_model = model or DEFAULT_MODEL

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "voice-nav",
    }

    payload = {
        "model": selected_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Provide concise, accurate responses.",
            },
            {"role": "user", "content": query},
        ],
    }

    try:
        logger.info(f"Querying OpenRouter with model: {selected_model}")
        resp = requests.post(
            OPENROUTER_API_URL, headers=headers, json=payload, timeout=30
        )
    except requests.RequestException as e:
        raise OpenRouterError(f"Request failed: {e}")

    if resp.status_code != 200:
        raise OpenRouterError(f"API error {resp.status_code}: {resp.text}")

    try:
        data = resp.json()
    except ValueError as e:
        raise OpenRouterError(f"Invalid JSON response: {e}")

    try:
        content = data["choices"][0]["message"]["content"]
        logger.info(f"Received response: {len(content)} characters")
        return content.strip()
    except (KeyError, IndexError) as e:
        raise OpenRouterError(f"Unexpected response format: {e}")
