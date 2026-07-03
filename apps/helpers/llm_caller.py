from openai import OpenAI
import os
from typing import Dict, Any, Tuple
from apps.helpers.decorators import retry
import json

from dotenv import load_dotenv
load_dotenv('/Users/dagoras/Documents/workspace/distant-supervision-ee/.env')


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', None)
OPENAI_MODEL = os.getenv('OPENAI_MODEL', None)

assert OPENAI_API_KEY, "Missing OpenAI api key"
assert OPENAI_BASE_URL, "Missing OpenAI base url"
assert OPENAI_MODEL, "Missing OpenAI model identifier"

CLIENT = OpenAI(
    base_url=OPENAI_BASE_URL,
    api_key=OPENAI_API_KEY
)

def parse_llm_json(raw_response):
    """Robustly parse JSON from LLM response, handling markdown code blocks."""
    content = raw_response.strip()
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


@retry(max_attempts=3)
def call_llm_json(system_prompt: str, user_prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
    response = CLIENT.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        extra_body=kwargs
    )

    return response.choices[0].message.content, parse_llm_json(response.choices[0].message.content)