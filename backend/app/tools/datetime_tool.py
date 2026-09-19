"""
DateTime Tool for TeachMind Agent.
Retrieves current date, time, and day of week.
"""

from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field
from backend.app.tools.base import BaseTool, PermissionType


class DateTimeInputSchema(BaseModel):
    query: str = Field(default="now", description="Time query")


class DateTimeTool(BaseTool):
    name = "datetime_tool"
    description = "Provides the current system date, time, and day of the week."
    permission_type = PermissionType.READ_ONLY
    requires_confirmation = False
    input_schema = DateTimeInputSchema

    def execute(self, **kwargs) -> Dict[str, Any]:
        now = datetime.now()
        return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "formatted": now.strftime("%A, %B %d, %Y at %I:%M %p")
        }
