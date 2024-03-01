"""empty message

Revision ID: 55a33e52d5a1
Revises:
Create Date: 2024-02-29 06:46:10.402054

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "55a33e52d5a1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "admin",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lead",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("pipeline", sa.String(length=256), nullable=True),
        sa.Column("status", sa.String(length=256), nullable=True),
        sa.Column("name", sa.String(length=256), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", sa.DateTime(), nullable=True),
        sa.Column("updated_by", sa.DateTime(), nullable=True),
        sa.Column("contact", sa.String(length=256), nullable=True),
        sa.Column("sale", sa.BigInteger(), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=True),
        sa.Column("speciality", sa.String(length=256), nullable=True),
        sa.Column("work_type", sa.String(length=256), nullable=True),
        sa.Column("koef", sa.Float(), nullable=True),
        sa.Column("pages", sa.Text(), nullable=True),
        sa.Column("thema", sa.Text(), nullable=True),
        sa.Column("uniqueness", sa.String(length=256), nullable=True),
        sa.Column("real_deadline", sa.String(length=256), nullable=True),
        sa.Column("deadline_for_author", sa.DateTime(), nullable=True),
        sa.Column("files", sa.String(length=256), nullable=True),
        sa.Column("fix_time", sa.BigInteger(), nullable=True),
        sa.Column("author_name", sa.String(length=256), nullable=True),
        sa.Column("author_id", sa.String(length=256), nullable=True),
        sa.Column("expenses", sa.BigInteger(), nullable=True),
        sa.Column("expenses_status", sa.BigInteger(), nullable=True),
        sa.Column("expenses_multy", sa.BigInteger(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("team_lead", sa.BigInteger(), nullable=True),
        sa.Column("priority", sa.BigInteger(), nullable=True),
        sa.Column("sec_author", sa.String(length=256), nullable=True),
        sa.Column("alert", sa.BigInteger(), nullable=True),
        sa.Column("sec_price", sa.BigInteger(), nullable=True),
        sa.Column("sity", sa.BigInteger(), nullable=True),
        sa.Column("university", sa.String(length=256), nullable=True),
        sa.Column("faculty", sa.BigInteger(), nullable=True),
        sa.Column("review", sa.String(length=256), nullable=True),
        sa.Column("costs_sum", sa.BigInteger(), nullable=True),
        sa.Column("correction_count", sa.BigInteger(), nullable=True),
        sa.Column("delivery_date", sa.BigInteger(), nullable=True),
        sa.Column("shtraf", sa.BigInteger(), nullable=True),
        sa.Column("date_done", sa.BigInteger(), nullable=True),
        sa.Column("plan", sa.String(length=256), nullable=True),
        sa.Column("task_current", sa.String(length=256), nullable=True),
        sa.Column("date_current", sa.BigInteger(), nullable=True),
        sa.Column("hotovo", sa.String(length=256), nullable=True),
        sa.Column("redone_date", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "speciality",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "author",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("custom_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=256), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("admin_id", sa.BigInteger(), nullable=True),
        sa.Column("plane_busyness", sa.Float(), nullable=True),
        sa.Column("busyness", sa.Float(), nullable=True),
        sa.Column("open_leads", sa.Integer(), nullable=True),
        sa.Column("auction", sa.Boolean(), nullable=True),
        sa.Column("card_number", sa.String(length=256), nullable=True),
        sa.Column("telegram_url", sa.String(length=256), nullable=True),
        sa.Column("specialities", sa.Text(), nullable=True),
        sa.Column("is_registered", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["admin_id"],
            ["admin.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_author_admin_id"), "author", ["admin_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_author_admin_id"), table_name="author")
    op.drop_table("author")
    op.drop_table("speciality")
    op.drop_table("lead")
    op.drop_table("admin")
    # ### end Alembic commands ###
