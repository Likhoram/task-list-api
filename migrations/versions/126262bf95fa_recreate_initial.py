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
    """
    Make the initial schema idempotent:
    - On a fresh DB, create goal and task tables.
    - If task exists from a previous state, apply the completed_at type cast.
    """
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("goal"):
        op.create_table(
            "goal",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("title", sa.String(), nullable=True),
        )

    if not insp.has_table("task"):
        op.create_table(
            "task",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("title", sa.String(), nullable=True),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.Column("goal_id", sa.Integer(), sa.ForeignKey("goal.id"), nullable=True),
        )
    else:
        # If the table already exists, apply the type cast for completed_at
        with op.batch_alter_table("task", schema=None) as batch_op:
            batch_op.alter_column(
                "completed_at",
                existing_type=sa.VARCHAR(),
                type_=sa.DateTime(),
                existing_nullable=True,
                postgresql_using="completed_at::timestamp without time zone",
            )


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Safely reverse the column cast if table exists
    if insp.has_table("task"):
        with op.batch_alter_table("task", schema=None) as batch_op:
            batch_op.alter_column(
                "completed_at",
                existing_type=sa.DateTime(),
                type_=sa.VARCHAR(),
                existing_nullable=True,
                postgresql_using="completed_at::varchar",
            )

    # Drop tables (reverse of upgrade create)
    if insp.has_table("task"):
        op.drop_table("task")
    if insp.has_table("goal"):
        op.drop_table("goal")
