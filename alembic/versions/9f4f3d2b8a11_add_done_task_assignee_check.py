"""add_done_task_assignee_check

Revision ID: 9f4f3d2b8a11
Revises: c46346d85dfc
Create Date: 2026-04-25 17:30:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9f4f3d2b8a11"
down_revision: Union[str, Sequence[str], None] = "c46346d85dfc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alembic operation methods are provided dynamically.
    # pylint: disable=no-member
    op.create_check_constraint(
        "check_done_task_requires_assignee",
        "task",
        "status <> 'done' OR assignee_id IS NOT NULL",
    )


def downgrade() -> None:
    # Alembic operation methods are provided dynamically.
    # pylint: disable=no-member
    op.drop_constraint(
        "check_done_task_requires_assignee",
        "task",
        type_="check",
    )
