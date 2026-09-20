"""
Base Tool Interface and Permission Types for TeachMind Agent.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Type
from pydantic import BaseModel


class PermissionType(str, Enum):
    READ_ONLY = "READ_ONLY"
    MUTATING = "MUTATING"
    HIGH_IMPACT = "HIGH_IMPACT"


class BaseTool(ABC):
    name: str
    description: str
    permission_type: PermissionType = PermissionType.READ_ONLY
    requires_confirmation: bool = False
    input_schema: Type[BaseModel]

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool logic safely."""
        pass
