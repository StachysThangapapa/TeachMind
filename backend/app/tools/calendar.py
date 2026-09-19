"""
Calendar Tools for TeachMind Agent.
Provides read-only calendar event retrieval and mutating event creation with confirmation boundaries.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.tools.base import BaseTool, PermissionType


class GetCalendarSchema(BaseModel):
    date: str = Field(default="today", description="Target date for calendar lookup")


class GetCalendarEventsTool(BaseTool):
    name = "get_calendar_events"
    description = "Retrieves upcoming calendar meetings and events for today."
    permission_type = PermissionType.READ_ONLY
    requires_confirmation = False
    input_schema = GetCalendarSchema

    def execute(self, **kwargs) -> Dict[str, Any]:
        return {
            "events": [
                {
                    "title": "TeachMind Architecture Review",
                    "time": "14:00 - 15:00",
                    "attendees": ["Team"]
                },
                {
                    "title": "Product Sync & Demo Preparation",
                    "time": "16:30 - 17:30",
                    "attendees": ["Mentors"]
                }
            ]
        }


class CreateCalendarEventSchema(BaseModel):
    title: str = Field(description="Title of event to create")
    time: str = Field(description="Time of event")
    date: str = Field(default="tomorrow", description="Date of event")


class CreateCalendarEventTool(BaseTool):
    name = "create_calendar_event"
    description = "Schedules a new event on the user's calendar."
    permission_type = PermissionType.MUTATING
    requires_confirmation = True
    input_schema = CreateCalendarEventSchema

    def execute(self, **kwargs) -> Dict[str, Any]:
        title = kwargs.get("title", "New Event")
        time = kwargs.get("time", "10:00")
        date = kwargs.get("date", "tomorrow")
        return {
            "status": "created",
            "event": {
                "id": "evt_9982",
                "title": title,
                "time": time,
                "date": date
            }
        }
