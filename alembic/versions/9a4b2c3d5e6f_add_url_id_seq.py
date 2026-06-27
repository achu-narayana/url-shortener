"""add url_id_seq sequence

Revision ID: 9a4b2c3d5e6f
Revises: 8f3a1c2b4d5e
Create Date: 2026-06-27 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9a4b2c3d5e6f"
down_revision: Union[str, None] = "8f3a1c2b4d5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("CREATE SEQUENCE url_id_seq START WITH 1 INCREMENT BY 1"))


def downgrade() -> None:
    op.execute(sa.text("DROP SEQUENCE url_id_seq"))
