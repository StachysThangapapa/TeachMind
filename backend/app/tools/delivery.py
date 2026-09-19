"""
Mock Delivery Tool for TeachMind Agent.
Simulates secure delivery status lookup.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field
from backend.app.tools.base import BaseTool, PermissionType


class DeliveryInputSchema(BaseModel):
    date: str = Field(default="today", description="Target date for delivery lookup")


class GetTodayDeliveriesTool(BaseTool):
    name = "get_today_deliveries"
    description = "Retrieves active package deliveries for the current user."
    permission_type = PermissionType.READ_ONLY
    requires_confirmation = False
    input_schema = DeliveryInputSchema

    def execute(self, **kwargs) -> Dict[str, Any]:
        return {
            "deliveries": [
                {
                    "product_name": "Wireless Mouse",
                    "status": "Delayed",
                    "expected_delivery": "Today",
                    "tracking_id": "TRK123456",
                    "is_active": True
                },
                {
                    "product_name": "USB-C Hub",
                    "status": "Arriving",
                    "expected_delivery": "Today",
                    "tracking_id": "TRK789012",
                    "is_active": True
                },
                {
                    "product_name": "Mechanical Keyboard",
                    "status": "Cancelled",
                    "expected_delivery": "N/A",
                    "tracking_id": "TRK000111",
                    "is_active": False
                }
            ]
        }
