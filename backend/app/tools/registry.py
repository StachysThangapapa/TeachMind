"""
Central Secure Tool Registry for TeachMind Agent.
Prevents arbitrary execution, validates schema, and enforces confirmation boundaries.
"""

from typing import Dict, Any, Optional
from backend.app.tools.base import BaseTool, PermissionType
from backend.app.tools.delivery import GetTodayDeliveriesTool
from backend.app.tools.calendar import GetCalendarEventsTool, CreateCalendarEventTool


class ToolRegistry:
    """Registry managing allowed tools and permission enforcement."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        # Register default mock tools
        self.register_tool(GetTodayDeliveriesTool())
        self.register_tool(GetCalendarEventsTool())
        self.register_tool(CreateCalendarEventTool())

    def register_tool(self, tool: BaseTool) -> None:
        """Register a new tool instance."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Fetch registered tool by name."""
        return self._tools.get(name)

    def execute_tool(self, name: str, arguments: Dict[str, Any], user_confirmed: bool = False) -> Dict[str, Any]:
        """
        Execute tool safely after checking permissions.
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' is not registered in the tool allow-list.")

        # Check confirmation boundary for mutating/high-impact tools
        if tool.requires_confirmation and not user_confirmed:
            return {
                "status": "confirmation_required",
                "requires_confirmation": True,
                "tool_name": tool.name,
                "arguments": arguments,
                "message": f"Action '{tool.name}' requires user confirmation before execution."
            }

        # Validate arguments using tool's schema
        validated_args = tool.input_schema(**arguments).model_dump()
        result = tool.execute(**validated_args)
        return {
            "status": "success",
            "requires_confirmation": False,
            "tool_name": tool.name,
            "result": result
        }


tool_registry = ToolRegistry()
