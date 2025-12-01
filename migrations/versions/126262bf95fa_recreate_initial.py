"""recreate initial

Revision ID: 126262bf95fa
Revises: 
Create Date: 2025-11-06 11:18:46.135106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '126262bf95fa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "goal",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(), nullable=True),
    )

    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("goal_id", sa.Integer(), sa.ForeignKey("goal.id"), nullable=True),
    )


def downgrade():
    op.drop_table("task")
    op.drop_table("goal")