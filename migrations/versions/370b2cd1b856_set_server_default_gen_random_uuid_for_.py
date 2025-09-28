"""Set server_default=gen_random_uuid() for UUID PKs

Revision ID: 370b2cd1b856
Revises: ee2889bbb47c
Create Date: 2025-08-23 14:37:55.327964

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "370b2cd1b856"
down_revision: Union[str, Sequence[str], None] = "ee2889bbb47c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Upgrade schema."""
	# gen_random_uuid() живёт в pgcrypto
	op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

	op.alter_column(
		"categories",
		"category_id",
		server_default=sa.text("gen_random_uuid()"),
		existing_type=postgresql.UUID(as_uuid=True),
		existing_nullable=False,
	)
	op.alter_column(
		"transactions",
		"transaction_id",
		server_default=sa.text("gen_random_uuid()"),
		existing_type=postgresql.UUID(as_uuid=True),
		existing_nullable=False,
	)


def downgrade() -> None:
	"""Downgrade schema."""
	op.alter_column(
		"transactions",
		"transaction_id",
		server_default=None,
		existing_type=postgresql.UUID(as_uuid=True),
		existing_nullable=False,
	)
	op.alter_column(
		"categories",
		"category_id",
		server_default=None,
		existing_type=postgresql.UUID(as_uuid=True),
		existing_nullable=False,
	)
