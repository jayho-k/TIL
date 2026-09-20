"""Create chat run and message logs."""

from alembic import op
import sqlalchemy as sa

revision = "0001_chat_logs"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("thread_id", sa.String(128), nullable=False),
        sa.Column("transport", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("latency_ms", sa.BigInteger()),
        sa.Column("model", sa.String(255), nullable=False),
        sa.Column("input_chars", sa.BigInteger(), nullable=False),
        sa.Column("output_chars", sa.BigInteger()),
        sa.Column("error_code", sa.String(64)),
        sa.Column("error_message", sa.Text()),
    )
    op.create_index("ix_chat_runs_thread_id", "chat_runs", ["thread_id"])
    op.create_index("ix_chat_runs_status", "chat_runs", ["status"])
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("run_id", sa.Uuid(), sa.ForeignKey("chat_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("thread_id", sa.String(128), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_chat_messages_run_id", "chat_messages", ["run_id"])
    op.create_index("ix_chat_messages_thread_id", "chat_messages", ["thread_id"])
    op.create_index(
        "ix_chat_messages_thread_created", "chat_messages", ["thread_id", "created_at"]
    )


def downgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("chat_runs")
