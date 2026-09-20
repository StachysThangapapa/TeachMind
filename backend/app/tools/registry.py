"""
Central Secure Tool Registry for TeachMind Agent.
Maintains tool allow-list, exposes parameters for LLM dynamic selection, and enforces permission boundaries.
"""

from typing import Dict, Any, Optional, List
from backend.app.tools.base import BaseTool, PermissionType
from backend.app.tools.delivery import GetTodayDeliveriesTool
from backend.app.tools.calendar import GetCalendarEventsTool, CreateCalendarEventTool
from backend.app.tools.calculator import CalculatorTool
from backend.app.tools.datetime_tool import DateTimeTool
from backend.app.tools.tasks import GetPendingTasksTool
from backend.app.tools.notes import SaveNoteTool


class ToolRegistry:
    """Registry managing allowed tools and permission enforcement."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        # Register default tools
        self.register_tool(GetTodayDeliveriesTool())
        self.register_tool(GetCalendarEventsTool())
        self.register_tool(CreateCalendarEventTool())
        self.register_tool(CalculatorTool())
        self.register_tool(DateTimeTool())
        self.register_tool(GetPendingTasksTool())
        self.register_tool(SaveNoteTool())

    def register_tool(self, tool: BaseTool) -> None:
        """Register a new tool instance."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Fetch registered tool by name."""
        return self._tools.get(name)

    def list_tool_names(self) -> List[str]:
        """List registered tool names."""
        return list(self._tools.keys())

    def list_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Return descriptions of registered tools for LLM dynamic tool selection."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "permission_type": t.permission_type.value,
                "requires_confirmation": t.requires_confirmation,
                "input_schema": t.input_schema.model_json_schema()
            }
            for t in self._tools.values()
        ]

    def execute_tool(self, name: str, arguments: Dict[str, Any], user_confirmed: bool = False) -> Dict[str, Any]:
        """
        Execute tool safely after checking permissions and validating arguments.
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' is not registered in the tool allow-list.")

        # Check confirmation boundary
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
