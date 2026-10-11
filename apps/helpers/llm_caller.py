from openai import OpenAI, APITimeoutError, Timeout
import os
from typing import Dict, Any, Tuple
from apps.helpers.decorators import retry
import json

from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', None)
OPENAI_MODEL = os.getenv('OPENAI_MODEL', None)

assert OPENAI_API_KEY, "Missing OpenAI api key"
assert OPENAI_BASE_URL, "Missing OpenAI base url"
assert OPENAI_MODEL, "Missing OpenAI model identifier"

DEFAULT_REQUEST_TIMEOUT = 60.0
DEFAULT_MAX_TOKENS = 2048

CLIENT = OpenAI(
    base_url=OPENAI_BASE_URL,
    api_key=OPENAI_API_KEY,
    timeout=DEFAULT_REQUEST_TIMEOUT
)

def parse_llm_json(raw_response):
    """Robustly parse JSON from LLM response, handling reasoning models (<think>...</think>) and markdown code blocks."""
    content = raw_response.strip()
    if "</think>" in content:
        content = content.split("</think>")[-1].strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        parts = content.split("```")
        for p in parts:
            p_strip = p.strip()
            if p_strip.startswith("{") and p_strip.endswith("}"):
                content = p_strip
                break
        else:
            content = parts[1] if len(parts) > 1 else parts[0]

    # Handle double curly braces wrapping if any
    content = content.strip()
    if content.startswith("{{") and content.endswith("}}"):
        content = content[1:-1].strip()

    start_idx = content.find("{")
    end_idx = content.rfind("}")
    if start_idx != -1 and end_idx != -1:
        content = content[start_idx: end_idx + 1]

    # If it was sliced and still has double braces at the ends
    if content.startswith("{{") and content.endswith("}}"):
        content = content[1:-1]

    return json.loads(content.strip())


@retry(max_attempts=3, exclude_exceptions=(APITimeoutError, Timeout, TimeoutError))
def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    timeout: float = DEFAULT_REQUEST_TIMEOUT,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    **kwargs
) -> Tuple[str, Dict[str, Any]]:
    create_kwargs = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "timeout": timeout,
        "max_tokens": max_tokens,
    }
    if "temperature" in kwargs:
        create_kwargs["temperature"] = kwargs.pop("temperature")
    if kwargs:
        create_kwargs["extra_body"] = kwargs

    response = CLIENT.chat.completions.create(**create_kwargs)

    return response.choices[0].message.content, parse_llm_json(response.choices[0].message.content)


def make_llm_caller(
    model: str,
    base_url: str = None,
    api_key: str = None,
    request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
    max_tokens: int = DEFAULT_MAX_TOKENS,
):
    """
    Builds a call_llm_json-compatible function bound to a specific model identifier.

    By default hits the configured OpenRouter client. Pass `base_url` (and optionally
    `api_key`) to instead target any other OpenAI-compatible endpoint, e.g. a local
    vLLM server (base_url="http://localhost:8000/v1", api_key can be left as a dummy
    value since vLLM does not enforce it).
    """
    client = CLIENT if base_url is None else OpenAI(
        base_url=base_url,
        api_key=api_key or "EMPTY",
        timeout=request_timeout,
    )

    @retry(max_attempts=3, exclude_exceptions=(APITimeoutError, Timeout, TimeoutError))
    def _call(system_prompt: str, user_prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        call_timeout = kwargs.pop("timeout", request_timeout)
        call_max_tokens = kwargs.pop("max_tokens", max_tokens)

        create_kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "timeout": call_timeout,
            "max_tokens": call_max_tokens,
        }
        if "temperature" in kwargs:
            create_kwargs["temperature"] = kwargs.pop("temperature")
        if kwargs:
            create_kwargs["extra_body"] = kwargs

        response = client.chat.completions.create(**create_kwargs)

        return response.choices[0].message.content, parse_llm_json(response.choices[0].message.content)

    return _call