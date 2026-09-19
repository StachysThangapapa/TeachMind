"""
Structured Output Utilities for TeachMind LLM Engine.
Parses and validates JSON responses from LLM calls against Pydantic models.
"""

import json
import logging
import re
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


def extract_json_string(text: str) -> str:
    """Extracts valid JSON string from LLM output markdown or raw text."""
    if not text:
        return ""
    text = text.strip()
    
    # 1. Find markdown fenced JSON block (```json ... ``` or ``` ... ```)
    fenced_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fenced_match:
        text = fenced_match.group(1).strip()

    # 2. Find JSON object or array bounds
    obj_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if obj_match:
        return obj_match.group(1).strip()
        
    return text


def parse_structured_output(text: str, schema: Type[T]) -> T:
    """
    Parses JSON text into a Pydantic schema instance with robust validation.
    Raises ValueError or ValidationError if parsing fails without silent corruption.
    """
    json_str = extract_json_string(text)
    if not json_str:
        logger.warning("[Structured Parsing]: Empty JSON string extracted from LLM response.")
        try:
            return schema()
        except Exception:
            return schema.model_construct()

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"[Structured Parsing Error] JSONDecodeError: {e}. Raw extracted: {json_str[:200]}")
        raise ValueError(f"Malformed JSON returned by model: {e}") from e

    try:
        if isinstance(data, dict):
            return schema.model_validate(data)
        elif isinstance(data, list):
            return schema.model_validate(data)
        return schema.model_validate(data)
    except ValidationError as ve:
        logger.error(f"[Structured Validation Error] Pydantic validation failed for {schema.__name__}: {ve}")
        raise

