"""create_taric_tables

Revision ID: 05cebb933691
Revises:
Create Date: 2026-03-13 07:11:29.437902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05cebb933691'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("roman_numeral", sa.String(10), unique=True, nullable=False),
        sa.Column("title_es", sa.Text(), nullable=False),
        sa.Column("title_en", sa.Text()),
        sa.Column("notes", sa.Text()),
    )

    op.create_table(
        "chapters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(2), unique=True, nullable=False),
        sa.Column("description_es", sa.Text(), nullable=False),
        sa.Column("description_en", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("section_id", sa.Integer(), sa.ForeignKey("sections.id"), nullable=False),
    )
    op.create_index("ix_chapters_code", "chapters", ["code"])

    op.create_table(
        "headings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(4), unique=True, nullable=False),
        sa.Column("description_es", sa.Text(), nullable=False),
        sa.Column("description_en", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("chapter_id", sa.Integer(), sa.ForeignKey("chapters.id"), nullable=False),
    )
    op.create_index("ix_headings_code", "headings", ["code"])

    op.create_table(
        "subheadings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(6), unique=True, nullable=False),
        sa.Column("description_es", sa.Text(), nullable=False),
        sa.Column("description_en", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("duty_rate", sa.String(50)),
        sa.Column("heading_id", sa.Integer(), sa.ForeignKey("headings.id"), nullable=False),
    )
    op.create_index("ix_subheadings_code", "subheadings", ["code"])

    op.create_table(
        "taric_codes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(10), unique=True, nullable=False),
        sa.Column("description_es", sa.Text(), nullable=False),
        sa.Column("description_en", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("duty_rate", sa.String(50)),
        sa.Column("supplementary_unit", sa.String(20)),
        sa.Column("subheading_id", sa.Integer(), sa.ForeignKey("subheadings.id"), nullable=False),
    )
    op.create_index("ix_taric_codes_code", "taric_codes", ["code"])


def downgrade() -> None:
    op.drop_table("taric_codes")
    op.drop_table("subheadings")
    op.drop_table("headings")
    op.drop_table("chapters")
    op.drop_table("sections")
