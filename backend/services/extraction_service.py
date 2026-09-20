"""Skill Extraction service component.

Extracts canonical Skill JSON from natural-language teaching text using
Cohere structured JSON output and schema enforcement.

This component is completely separate from Skill-Memory storage/retrieval.
It performs natural-language extraction ONLY and never touches PostgreSQL.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json
import re
from typing import Any, List, Union

import cohere
from pydantic import BaseModel, Field

from backend.config import settings
from backend.schemas.skill import (
    ExampleSchema,
    MetadataSchema,
    RuleSchema,
    SkillResponse,
    StepSchema,
)


class ExtractedSkillRaw(BaseModel):
    """Schema enforced on the LLM during natural language extraction."""

    name: str = Field(
        ...,
        description="Concise snake_case or slug name for the skill, e.g. coffee_preparation or monthly_report_processing",
    )
    description: str = Field(
        ...,
        description="Clear human-readable summary of what this workflow accomplishes",
    )
    triggers: List[str] = Field(
        default_factory=list,
        description="Semantic trigger phrases indicating when to run this skill",
    )
    steps: List[StepSchema] = Field(
        default_factory=list,
        description="Sequential ordered workflow steps with step number and instruction",
    )
    rules: List[RuleSchema] = Field(
        default_factory=list,
        description="Logical business rules, conditions, and constraints",
    )
    examples: List[ExampleSchema] = Field(
        default_factory=list,
        description="Demonstrations of input and expected behavior",
    )


def clean_json_string(raw_text: str) -> str:
    """Strip markdown code fences and extraneous text surrounding a JSON object."""
    text = raw_text.strip()
    # Match ```json ... ``` or ``` ... ```
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()

    # Isolate JSON object between outermost braces
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace : last_brace + 1]

    return text


def normalize_steps(raw_steps: List[Any], fallback_text: str) -> List[StepSchema]:
    """Normalize steps from various formats into validated StepSchema objects."""
    normalized: list[StepSchema] = []
    if not raw_steps:
        # If no steps were extracted, infer a default procedural step from the text
        return [StepSchema(step=1, instruction=fallback_text.strip())]

    for idx, s in enumerate(raw_steps, start=1):
        if isinstance(s, StepSchema):
            normalized.append(StepSchema(step=s.step if s.step > 0 else idx, instruction=s.instruction.strip()))
        elif isinstance(s, str):
            instruction = s.strip()
            if instruction:
                normalized.append(StepSchema(step=idx, instruction=instruction))
        elif isinstance(s, dict):
            instruction = str(s.get("instruction") or s.get("text") or s.get("step_description") or s.get("action") or "").strip()
            if not instruction:
                instruction = str(s)
            step_num = s.get("step")
            try:
                step_int = int(step_num) if step_num is not None else idx
            except (ValueError, TypeError):
                step_int = idx
            normalized.append(StepSchema(step=step_int if step_int > 0 else idx, instruction=instruction))

    return normalized if normalized else [StepSchema(step=1, instruction=fallback_text.strip())]


def normalize_rules(raw_rules: List[Any]) -> List[RuleSchema]:
    """Normalize rules from various formats into validated RuleSchema objects."""
    normalized: list[RuleSchema] = []
    for r in raw_rules:
        if isinstance(r, RuleSchema):
            normalized.append(r)
        elif isinstance(r, str):
            text = r.strip()
            if text:
                normalized.append(RuleSchema(condition="General constraint", action=text))
        elif isinstance(r, dict):
            condition = str(r.get("condition") or r.get("when") or r.get("rule") or "General constraint").strip()
            action = str(r.get("action") or r.get("then") or r.get("instruction") or r.get("value") or "").strip()
            if not action and condition:
                action = condition
                condition = "General constraint"
            if condition and action:
                normalized.append(RuleSchema(condition=condition, action=action))
    if not normalized:
        normalized.append(RuleSchema(condition="Standard execution", action="Execute workflow steps in designated sequence"))
    return normalized


def normalize_examples(raw_examples: List[Any]) -> List[ExampleSchema]:
    """Normalize examples from various formats into validated ExampleSchema objects."""
    normalized: list[ExampleSchema] = []
    for ex in raw_examples:
        if isinstance(ex, ExampleSchema):
            normalized.append(ex)
        elif isinstance(ex, str):
            text = ex.strip()
            if text:
                normalized.append(ExampleSchema(input=text, expected_behavior="Execute workflow as instructed"))
        elif isinstance(ex, dict):
            inp = str(ex.get("input") or ex.get("query") or ex.get("user_input") or "").strip()
            out = str(ex.get("expected_behavior") or ex.get("output") or ex.get("expected") or "Execute workflow").strip()
            if inp:
                normalized.append(ExampleSchema(input=inp, expected_behavior=out))
    if not normalized:
        normalized.append(ExampleSchema(input="Execute workflow", expected_behavior="Complete workflow steps successfully"))
    return normalized


class SkillExtractionProvider(ABC):
    """Abstract interface for natural-language skill extraction.

    Enables swapping the extraction model/provider without altering API endpoints.
    """

    @abstractmethod
    def extract_skill(self, text: str) -> SkillResponse:
        """Extract a validated canonical Skill JSON from natural language."""
        ...


class CohereSkillExtractionProvider(SkillExtractionProvider):
    """Cohere implementation using structured JSON output and schema enforcement."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self._client = cohere.ClientV2(
            api_key=api_key or settings.cohere_api_key,
            log_warning_experimental_features=False,
        )
        self._model = model or settings.extraction_model

    def extract_skill(self, text: str) -> SkillResponse:
        if not text or not text.strip():
            raise ValueError("Teaching text cannot be empty.")

        cleaned_input = text.strip()

        system_prompt = (
            "You are TeachMind's Skill Extraction Engine. Your job is to extract structured, "
            "canonical workflow skills from any natural-language user instruction, whether short or long, "
            "procedural or descriptive, casual or formal.\n\n"
            "Rules for extraction:\n"
            "1. Identify the user's intended reusable skill and generate a concise name (e.g. 'coffee_preparation', 'weekly_meeting_summary').\n"
            "2. Formulate a clear, accurate description summarizing what the skill achieves.\n"
            "3. Extract semantic triggers (phrases a user might speak or type when requesting this task in the future).\n"
            "4. Convert instructions into sequential ordered steps with 1-based step numbers and clear instructions.\n"
            "5. Extract explicit conditions, rules, constraints, or preferences (condition and action). If none, leave empty.\n"
            "6. Extract or infer realistic example input/expected_behavior pairs if relevant. If none, leave empty.\n"
            "7. Never invent facts unsupported by the user's text. Treat the user's text as the ground truth.\n"
            "8. Return valid JSON matching the requested schema."
        )

        user_prompt = f"Extract a canonical workflow skill from the following user instruction:\n\n{cleaned_input}"

        try:
            response = self._client.chat(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                    "type": "json_object",
                    "schema": ExtractedSkillRaw.model_json_schema(),
                },
            )
        except Exception as exc:
            raise RuntimeError(f"Cohere API call failed during skill extraction: {exc}") from exc

        if not response.message or not response.message.content:
            raise RuntimeError("Empty response received from Cohere extraction model.")

        raw_content = response.message.content[0].text
        cleaned_json = clean_json_string(raw_content)

        try:
            raw_data = json.loads(cleaned_json)
        except Exception as exc:
            raise ValueError(f"Failed to parse Cohere output as JSON: {exc}\nRaw text: {raw_content}") from exc

        # Format and assign a clean, unique skill_id
        raw_name = str(raw_data.get("name") or "learned_workflow").strip()
        clean_name = re.sub(r"[^a-zA-Z0-9_]+", "_", raw_name.lower()).strip("_")
        if not clean_name:
            clean_name = "learned_workflow"
        skill_id = clean_name if clean_name.startswith("skill_") else f"skill_{clean_name}"

        # Description
        description = str(raw_data.get("description") or cleaned_input).strip()

        # Triggers
        raw_triggers = raw_data.get("triggers")
        if isinstance(raw_triggers, list):
            triggers = [str(t).strip() for t in raw_triggers if str(t).strip()]
        elif isinstance(raw_triggers, str) and raw_triggers.strip():
            triggers = [raw_triggers.strip()]
        else:
            triggers = []

        if not triggers:
            triggers = [raw_name.replace("_", " "), cleaned_input[:60]]

        # Steps, rules, examples with normalization
        steps = normalize_steps(raw_data.get("steps", []), cleaned_input)
        rules = normalize_rules(raw_data.get("rules", []))
        examples = normalize_examples(raw_data.get("examples", []))

        now = datetime.now(timezone.utc)
        metadata = MetadataSchema(created_at=now, updated_at=now)

        # Assemble and validate canonical SkillResponse
        return SkillResponse(
            skill_id=skill_id,
            name=raw_name,
            description=description,
            triggers=triggers,
            steps=steps,
            rules=rules,
            examples=examples,
            version=1,
            verified=False,
            metadata=metadata,
        )
