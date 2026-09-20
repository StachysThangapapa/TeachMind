"""
Intent Understanding Engine for TeachMind Agent.
Classifies user messages into structured intent categories.
"""

from backend.app.schemas.agent import ParsedIntent, IntentType
from backend.app.llm.provider import get_llm_provider


class IntentEngine:
    """Classifies requests into NORMAL_REQUEST, TEACH_REQUEST, CORRECTION, CONFIRMATION, etc."""

    def __init__(self):
        self.llm = get_llm_provider()

    def parse_intent(self, message: str) -> ParsedIntent:
        """
        Parses intent using LLM provider with fallback deterministic rules.
        """
        msg_lower = message.lower()

        # Rule-assisted deterministic override for high precision
        if "don't show" in msg_lower or "don't include" in msg_lower or "actually" in msg_lower or "unless i ask" in msg_lower:
            return ParsedIntent(
                type=IntentType.CORRECTION,
                intent="update_preference",
                entities={"target": "tracking_id", "condition": "explicit_request"},
                confidence=0.96
            )
        elif "when i ask" in msg_lower or "whenever" in msg_lower or "teach" in msg_lower:
            return ParsedIntent(
                type=IntentType.TEACH_REQUEST,
                intent="teach_skill",
                entities={"workflow": message},
                confidence=0.95
            )
        elif msg_lower.strip() in ["yes", "confirm", "do that", "proceed", "approve"]:
            return ParsedIntent(
                type=IntentType.CONFIRMATION,
                intent="confirm_action",
                entities={},
                confidence=0.98
            )
        elif "cancel" in msg_lower or "stop" in msg_lower:
            return ParsedIntent(
                type=IntentType.CANCELLATION,
                intent="cancel_action",
                entities={},
                confidence=0.95
            )

        # Use LLM provider structured generation
        return self.llm.generate_structured(prompt=message, schema=ParsedIntent)


intent_engine = IntentEngine()
