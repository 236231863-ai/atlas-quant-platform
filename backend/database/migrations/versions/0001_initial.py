"""Initial migration: create lottery_games, draw_records, strategy_runs.

Revision ID: 0001
Revises:
Create Date: 2026-07-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.sqlite import JSON

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lottery_games",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(20), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("region", sa.String(20), nullable=False, server_default="CN"),
        sa.Column("main_range", JSON, nullable=False),
        sa.Column("bonus_range", JSON, nullable=True),
        sa.Column("draw_schedule", sa.String(100), nullable=True),
        sa.Column("metadata", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "draw_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("lottery_code", sa.String(20), nullable=False, index=True),
        sa.Column("draw_number", sa.String(20), nullable=False),
        sa.Column("draw_date", sa.Date, nullable=False),
        sa.Column("main_numbers", JSON, nullable=False),
        sa.Column("bonus_numbers", JSON, nullable=True),
        sa.Column("pool_amount", sa.DECIMAL(15, 2), nullable=True),
        sa.Column("metadata", JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("game_id", sa.String(36), sa.ForeignKey("lottery_games.id"), nullable=True),
        sa.UniqueConstraint("lottery_code", "draw_number", name="uq_draw_per_lottery"),
    )
    op.create_index("idx_draw_lottery_date", "draw_records", ["lottery_code", "draw_date"])

    op.create_table(
        "strategy_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("lottery_code", sa.String(20), nullable=False, index=True),
        sa.Column("strategy_json", JSON, nullable=False),
        sa.Column("date_range_start", sa.Date, nullable=True),
        sa.Column("date_range_end", sa.Date, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("result_summary", JSON, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("strategy_runs")
    op.drop_index("idx_draw_lottery_date", table_name="draw_records")
    op.drop_table("draw_records")
    op.drop_table("lottery_games")
