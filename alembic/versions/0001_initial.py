"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_external_id", "users", ["external_id"], unique=True)

    op.create_table(
        "connections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("external_account_id", sa.String(length=255), nullable=True),
        sa.Column("external_account_login", sa.String(length=255), nullable=True),
        sa.Column("encrypted_access_token", sa.LargeBinary(), nullable=False),
        sa.Column("encrypted_refresh_token", sa.LargeBinary(), nullable=True),
        sa.Column("scopes", sa.String(length=1024), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "provider", name="uq_connection_user_provider"),
    )
    op.create_index("ix_connections_user_id", "connections", ["user_id"])
    op.create_index("ix_connections_provider", "connections", ["provider"])

    op.create_table(
        "action_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "connection_id",
            sa.Integer(),
            sa.ForeignKey("connections.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action_name", sa.String(length=128), nullable=False),
        sa.Column(
            "args",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("result_summary", sa.String(length=1024), nullable=True),
        sa.Column("error", sa.String(length=2048), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_action_logs_user_id", "action_logs", ["user_id"])
    op.create_index("ix_action_logs_connection_id", "action_logs", ["connection_id"])
    op.create_index("ix_action_logs_action_name", "action_logs", ["action_name"])
    op.create_index("ix_action_logs_created_at", "action_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("action_logs")
    op.drop_table("connections")
    op.drop_table("users")
