"""
Notes Tool for TeachMind Agent.
Allows saving and retrieving personal notes.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from backend.app.tools.base import BaseTool, PermissionType


class SaveNoteSchema(BaseModel):
    title: str = Field(description="Note title")
    content: str = Field(description="Note content")


class SaveNoteTool(BaseTool):
    name = "save_note"
    description = "Saves a personal text note or user reminder."
    permission_type = PermissionType.MUTATING
    requires_confirmation = False
    input_schema = SaveNoteSchema

    def execute(self, **kwargs) -> Dict[str, Any]:
        title = kwargs.get("title", "Untitled Note")
        content = kwargs.get("content", "")
        return {
            "status": "saved",
            "note": {
                "id": "note_554",
                "title": title,
                "content": content
            }
        }
