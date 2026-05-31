"""add friends

Revision ID: 1988c131048f
Revises: 78acdfd43643
Create Date: 2026-05-31 15:32:20.272235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1988c131048f"
down_revision: Union[str, Sequence[str], None] = "78acdfd43643"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "friend_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("from_user_id", sa.Integer(), nullable=False),
        sa.Column("to_user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["from_user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["to_user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "from_user_id",
            "to_user_id",
            name="uq_friend_request_from_to",
        ),
    )

    op.create_index(
        op.f("ix_friend_requests_from_user_id"),
        "friend_requests",
        ["from_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_friend_requests_id"),
        "friend_requests",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_friend_requests_to_user_id"),
        "friend_requests",
        ["to_user_id"],
        unique=False,
    )

    op.create_table(
        "friends",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("friend_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["friend_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "friend_id",
            name="uq_friend_user_friend",
        ),
    )

    op.create_index(
        op.f("ix_friends_friend_id"),
        "friends",
        ["friend_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_friends_id"),
        "friends",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_friends_user_id"),
        "friends",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_friends_user_id"),
        table_name="friends",
    )
    op.drop_index(
        op.f("ix_friends_id"),
        table_name="friends",
    )
    op.drop_index(
        op.f("ix_friends_friend_id"),
        table_name="friends",
    )
    op.drop_table("friends")

    op.drop_index(
        op.f("ix_friend_requests_to_user_id"),
        table_name="friend_requests",
    )
    op.drop_index(
        op.f("ix_friend_requests_id"),
        table_name="friend_requests",
    )
    op.drop_index(
        op.f("ix_friend_requests_from_user_id"),
        table_name="friend_requests",
    )
    op.drop_table("friend_requests")