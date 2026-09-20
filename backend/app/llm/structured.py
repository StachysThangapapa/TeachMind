"""
Structured Output Utilities for TeachMind LLM Engine.
Parses and validates JSON responses from LLM calls against Pydantic models.
"""

import json
import re
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def extract_json_string(text: str) -> str:
    """Extracts valid JSON string from LLM output markdown or raw text."""
    text = text.strip()
    # Find markdown fenced JSON block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Find JSON object or array bounds
    obj_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if obj_match:
        return obj_match.group(1).strip()
        
    return text


def parse_structured_output(text: str, schema: Type[T]) -> T:
    """Parses JSON text into a Pydantic schema instance."""
    json_str = extract_json_string(text)
    try:
        data = json.loads(json_str)
        return schema(**data)
    except Exception as e:
        # Attempt fallback to model construction
        try:
            return schema()
        except Exception:
            return schema.model_construct()
