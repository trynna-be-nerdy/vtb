"""Initial schema: all tables, indexes, and search_vector trigger

Revision ID: 001
Revises:
Create Date: 2026-05-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── sources ──────────────────────────────────────────────────────────────
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("base_url", sa.String(500), nullable=False),
        sa.Column("scraper_type", sa.String(50), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # ── seen_documents ────────────────────────────────────────────────────────
    op.create_table(
        "seen_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("url", sa.String(1000), unique=True, nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_seen_documents_url", "seen_documents", ["url"])

    # ── meetings ──────────────────────────────────────────────────────────────
    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("board_slug", sa.String(100), nullable=False),
        sa.Column("meeting_date", sa.Date(), nullable=False),
        sa.Column("source_url", sa.String(1000)),
        sa.Column("source_pdf_url", sa.String(1000)),
        sa.Column("meeting_overview", sa.Text()),
        sa.Column("top_decisions", ARRAY(sa.Text())),
        sa.Column("fiscal_total", sa.String(100)),
        sa.Column("next_meeting_notes", sa.Text()),
        sa.Column("total_items", sa.Integer(), server_default="0", nullable=False),
        sa.Column("fiscal_items", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "processing_status",
            sa.String(20),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_meetings_board_date", "meetings", ["board_slug", "meeting_date"])
    op.create_index("ix_meetings_date", "meetings", ["meeting_date"])
    op.create_index("ix_meetings_status", "meetings", ["processing_status"])

    # ── agenda_items ──────────────────────────────────────────────────────────
    op.create_table(
        "agenda_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "meeting_id",
            sa.Integer(),
            sa.ForeignKey("meetings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("decisions", ARRAY(sa.Text())),
        sa.Column("action_items", ARRAY(sa.Text())),
        sa.Column("key_figures", JSONB()),
        sa.Column("primary_category", sa.String(50), nullable=False),
        sa.Column("secondary_tags", ARRAY(sa.Text())),
        sa.Column("urgency", sa.String(20), server_default="routine", nullable=False),
        sa.Column("fiscal_impact", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("affects_schools", ARRAY(sa.Text())),
        sa.Column("source_pdf_url", sa.String(1000)),
        sa.Column("page_range", sa.String(50)),
        sa.Column("search_vector", TSVECTOR()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_agenda_items_meeting_id", "agenda_items", ["meeting_id"])
    op.create_index("ix_agenda_items_category", "agenda_items", ["primary_category"])
    op.create_index("ix_agenda_items_urgency", "agenda_items", ["urgency"])
    op.create_index("ix_agenda_items_fiscal", "agenda_items", ["fiscal_impact"])
    # GIN index for fast PostgreSQL full-text search
    op.create_index(
        "ix_agenda_items_search_vector",
        "agenda_items",
        ["search_vector"],
        postgresql_using="gin",
    )

    # ── supporting_documents ──────────────────────────────────────────────────
    op.create_table(
        "supporting_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "meeting_id",
            sa.Integer(),
            sa.ForeignKey("meetings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(500)),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("doc_type", sa.String(50)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # ── pipeline_runs ─────────────────────────────────────────────────────────
    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), server_default="running", nullable=False),
        sa.Column("documents_found", sa.Integer(), server_default="0", nullable=False),
        sa.Column("documents_processed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("items_created", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text()),
    )

    # ── search_vector trigger ─────────────────────────────────────────────────
    # asyncpg requires each statement in its own execute() call
    op.execute("""
        CREATE OR REPLACE FUNCTION update_agenda_search_vector()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            NEW.search_vector := to_tsvector(
                'english',
                coalesce(NEW.title, '')   || ' ' ||
                coalesce(NEW.summary, '') || ' ' ||
                coalesce(array_to_string(NEW.decisions, ' '), '')
            );
            RETURN NEW;
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER trg_agenda_search_vector
            BEFORE INSERT OR UPDATE ON agenda_items
            FOR EACH ROW EXECUTE FUNCTION update_agenda_search_vector()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_agenda_search_vector ON agenda_items;")
    op.execute("DROP FUNCTION IF EXISTS update_agenda_search_vector();")
    op.drop_table("pipeline_runs")
    op.drop_table("supporting_documents")
    op.drop_table("agenda_items")
    op.drop_table("meetings")
    op.drop_table("seen_documents")
    op.drop_table("sources")
