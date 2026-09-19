"""Seed the database with 5 sample skills from the Review 1 specification (§12).

Run after migrations:

    python -m scripts.seed_skills

The script is idempotent — it skips skills whose skill_id already exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from project root: python -m scripts.seed_skills
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import settings  # noqa: E402
from backend.db.database import SessionLocal  # noqa: E402
from backend.db.migrations import run_migrations  # noqa: E402
from backend.repositories.skill_repository import SkillRepository  # noqa: E402
from backend.services.embedding_service import CohereEmbeddingProvider  # noqa: E402
from backend.services.skill_service import SkillService  # noqa: E402
from backend.schemas.skill import SkillCreate, StepSchema, RuleSchema, ExampleSchema  # noqa: E402


SAMPLE_SKILLS: list[SkillCreate] = [
    SkillCreate(
        skill_id="skill_001",
        name="Process Monthly Report",
        description="Create a monthly Excel report from a sales CSV.",
        triggers=[
            "prepare monthly report",
            "create monthly sales report",
            "generate sales report",
        ],
        steps=[
            StepSchema(step=1, instruction="Use the provided sales CSV as the input."),
            StepSchema(step=2, instruction="Create an Excel report."),
            StepSchema(step=3, instruction="Add a summary sheet."),
            StepSchema(step=4, instruction="Add a chart."),
            StepSchema(step=5, instruction="Save the report in the user's Reports folder."),
        ],
        rules=[],
        examples=[
            ExampleSchema(
                input="Here is this month's sales data, make my report.",
                expected_behavior="An Excel file with summary sheet and chart is saved to Reports.",
            ),
        ],
        version=1,
        verified=True,
    ),
    SkillCreate(
        skill_id="skill_002",
        name="Format Excel Report",
        description="Apply standard formatting to an existing Excel report.",
        triggers=[
            "format the report",
            "clean up the spreadsheet",
            "apply formatting to Excel",
        ],
        steps=[
            StepSchema(step=1, instruction="Open the specified Excel report."),
            StepSchema(step=2, instruction="Format headers with bold text and background color."),
            StepSchema(step=3, instruction="Auto-adjust column widths."),
            StepSchema(step=4, instruction="Apply number formatting to numeric columns."),
            StepSchema(step=5, instruction="Save the formatted report."),
        ],
        rules=[
            RuleSchema(
                condition="Report has currency columns",
                action="Apply currency number format",
            ),
        ],
        examples=[],
        version=1,
        verified=True,
    ),
    SkillCreate(
        skill_id="skill_003",
        name="Customer Email Workflow",
        description="Read a customer message, classify it, and draft an appropriate response.",
        triggers=[
            "handle customer email",
            "respond to customer message",
            "draft customer reply",
        ],
        steps=[
            StepSchema(step=1, instruction="Read the incoming customer message."),
            StepSchema(step=2, instruction="Identify the request type (inquiry, complaint, order)."),
            StepSchema(step=3, instruction="Draft a response based on the request type."),
            StepSchema(step=4, instruction="Apply the user's standard email signature and tone rules."),
            StepSchema(step=5, instruction="Present the draft for review before sending."),
        ],
        rules=[
            RuleSchema(
                condition="Request type is complaint",
                action="Use empathetic tone and offer resolution",
            ),
            RuleSchema(
                condition="Request type is order",
                action="Include order confirmation details",
            ),
        ],
        examples=[
            ExampleSchema(
                input="A customer asks about their order status.",
                expected_behavior="A polite reply with order tracking information.",
            ),
        ],
        version=1,
        verified=True,
    ),
    SkillCreate(
        skill_id="skill_004",
        name="Organize Project Files",
        description="Sort project files into categorized folders with consistent naming.",
        triggers=[
            "organize my project files",
            "sort files into folders",
            "clean up project directory",
        ],
        steps=[
            StepSchema(step=1, instruction="Scan the target directory for all files."),
            StepSchema(step=2, instruction="Identify file types (documents, images, code, data)."),
            StepSchema(step=3, instruction="Create category folders if they do not exist."),
            StepSchema(step=4, instruction="Move each file to the appropriate folder."),
            StepSchema(step=5, instruction="Apply the user's naming convention to moved files."),
            StepSchema(step=6, instruction="Verify all files have been organized correctly."),
        ],
        rules=[
            RuleSchema(
                condition="File is a README or config",
                action="Keep in root directory",
            ),
        ],
        examples=[],
        version=1,
        verified=True,
    ),
    SkillCreate(
        skill_id="skill_005",
        name="Process Support Tickets",
        description="Read, classify, and categorize incoming support tickets.",
        triggers=[
            "process support tickets",
            "categorize tickets",
            "handle support requests",
        ],
        steps=[
            StepSchema(step=1, instruction="Read the incoming support ticket."),
            StepSchema(step=2, instruction="Classify the issue type (bug, feature request, question)."),
            StepSchema(step=3, instruction="Assign a priority level based on the classification."),
            StepSchema(step=4, instruction="Apply learned categorization tags."),
            StepSchema(step=5, instruction="Update the ticket with classification and priority."),
            StepSchema(step=6, instruction="Verify the result matches expected categorization."),
        ],
        rules=[
            RuleSchema(
                condition="Issue mentions data loss or security",
                action="Assign critical priority",
            ),
        ],
        examples=[
            ExampleSchema(
                input="User reports they cannot log in to the application.",
                expected_behavior="Classified as bug, medium priority, tagged 'authentication'.",
            ),
        ],
        version=1,
        verified=True,
    ),
]


def seed() -> None:
    """Insert sample skills, skipping any that already exist."""
    run_migrations()

    db = SessionLocal()
    try:
        repo = SkillRepository(db)
        provider = CohereEmbeddingProvider()
        service = SkillService(repo, provider)

        for skill_data in SAMPLE_SKILLS:
            existing = repo.get_by_id(skill_data.skill_id)
            if existing:
                print(f"  ⏭  {skill_data.skill_id} ({skill_data.name}) — already exists, skipping")
                continue
            service.store_skill(skill_data)
            print(f"  ✓  {skill_data.skill_id} ({skill_data.name}) — stored with embedding")

        print("\nSeed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
