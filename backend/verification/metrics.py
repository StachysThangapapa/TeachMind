"""
Verification Metrics Module for TeachMind.
Calculates performance and accuracy metrics for evaluated skills.
"""


def calculate_accuracy(correct: int, total: int) -> float:
    """
    Calculate accuracy given correct predictions and total cases.

    :param correct: Number of correct test case results.
    :param total: Total number of test cases.
    :return: Accuracy score between 0.0 and 1.0.
    """
    if total < 0 or correct < 0:
        raise ValueError("Correct count and total count must be non-negative.")
    if correct > total:
        raise ValueError("Correct count cannot exceed total count.")
    if total == 0:
        return 0.0

    return round(correct / total, 4)
