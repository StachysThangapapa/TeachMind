"""
Calculator Tool for TeachMind Agent.
Safely evaluates mathematical expressions (e.g. "18% of 1250", "450 / 625").
"""

import math
import re
from typing import Dict, Any
from pydantic import BaseModel, Field
from backend.app.tools.base import BaseTool, PermissionType


class CalculatorInputSchema(BaseModel):
    expression: str = Field(description="Math expression or calculation prompt (e.g., '18% of 1250', '625 - 450')")


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Performs mathematical calculations and percentage computations."
    permission_type = PermissionType.READ_ONLY
    requires_confirmation = False
    input_schema = CalculatorInputSchema

    def execute(self, **kwargs) -> Dict[str, Any]:
        expr = kwargs.get("expression", "").strip().lower()
        
        # Parse percentage calculation (e.g. "18% of 1250")
        pct_match = re.search(r"([\d\.]+)\%\s*of\s*([\d\.]+)", expr)
        if pct_match:
            pct = float(pct_match.group(1))
            val = float(pct_match.group(2))
            res = (pct / 100.0) * val
            return {"expression": expr, "result": res, "formatted": f"{res:g}"}

        # Parse percentage increase/decrease (e.g. "from 450 to 625")
        inc_match = re.search(r"from\s*([\d\.]+)\s*to\s*([\d\.]+)", expr)
        if inc_match:
            v1 = float(inc_match.group(1))
            v2 = float(inc_match.group(2))
            diff = v2 - v1
            pct_inc = (diff / v1) * 100.0 if v1 != 0 else 0.0
            return {"expression": expr, "result": round(pct_inc, 2), "formatted": f"{pct_inc:.2f}%"}

        # Safe arithmetic evaluator
        try:
            clean_expr = re.sub(r"[^\d\+\-\*\/\(\)\.\s]", "", expr)
            if clean_expr:
                res = eval(clean_expr, {"__builtins__": None, "math": math})
                return {"expression": expr, "result": res, "formatted": str(res)}
        except Exception:
            pass

        return {"expression": expr, "result": 0, "formatted": "Calculation error"}
