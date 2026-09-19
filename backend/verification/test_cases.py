"""
Test Case Loader for TeachMind Verification Framework.
Handles loading test scenarios from JSON files or data objects.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Union


class TestCaseLoader:
    """Utility class to load and validate verification test scenarios."""

    @staticmethod
    def load_from_file(filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Load a test scenario from a JSON file.

        :param filepath: Path to the JSON test scenario file.
        :return: Parsed scenario dictionary containing 'skill' and 'cases'.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Test scenario file not found: {filepath}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "cases" not in data:
            raise ValueError("Invalid test scenario format: missing 'cases' key.")

        return data

    @staticmethod
    def load_from_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and return a scenario dictionary.

        :param data: Dictionary representing scenario data.
        :return: Validated scenario dictionary.
        """
        if "cases" not in data or not isinstance(data["cases"], list):
            raise ValueError("Invalid scenario dictionary: 'cases' must be a list.")

        return data
