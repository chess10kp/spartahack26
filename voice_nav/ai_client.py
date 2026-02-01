"""OpenRouter AI client for querying language models."""

import base64
import logging
import os
from typing import Optional

from PIL import Image
import requests

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemma-2-9b-it"
VISION_MODEL = "google/gemini-2.0-flash-001"
CHEAP_MODELS = [
    "google/gemma-2-9b-it",
    "meta-llama/llama-3.1-8b-instruct",
    "google/gemma-2-27b-it",
]


class OpenRouterError(Exception):
    pass


def _image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 data URL."""
    import io
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


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


def query_openrouter_with_vision(
    query: str,
    screenshot: Image.Image,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """Send a query with screenshot to OpenRouter vision model.

    Args:
        query: User's question or query text
        screenshot: PIL Image of the current screen
        model: Model to use (defaults to VISION_MODEL)
        api_key: OpenRouter API key (defaults to env variable)

    Returns:
        AI response text suitable for typing into an input field

    Raises:
        OpenRouterError: If API request fails
    """
    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise OpenRouterError("Missing OPENROUTER_API_KEY")

    selected_model = model or VISION_MODEL
    image_url = _image_to_base64(screenshot)

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "voice-nav",
    }

    system_prompt = """You are an AI assistant helping a user fill in an input field on their screen.

The user is looking at an application (shown in the screenshot) and has an input field focused.
They've asked you a question or requested content to type into that field.

IMPORTANT GUIDELINES:
1. Look at the screenshot to understand the context - what application is open, what form/field the user is likely filling in
2. Generate a response that is DIRECTLY suitable to paste into the input field
3. Do NOT include explanations, preambles, or meta-commentary
4. Do NOT use markdown formatting, bullet points, or special characters unless the input field clearly expects them
5. Match the tone and format expected by the input field (e.g., formal for email, casual for chat, code for a code editor)
6. If the screenshot shows a search bar, provide search terms. If it's a message field, write the message. If it's a form field, provide appropriate form data.
7. Keep your response concise and directly usable - the user will type this verbatim

Respond with ONLY the text that should be typed into the input field."""

    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ],
    }

    try:
        logger.info(f"Querying OpenRouter vision model: {selected_model}")
        resp = requests.post(
            OPENROUTER_API_URL, headers=headers, json=payload, timeout=60
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
        logger.info(f"Received vision response: {len(content)} characters")
        return content.strip()
    except (KeyError, IndexError) as e:
        raise OpenRouterError(f"Unexpected response format: {e}")
