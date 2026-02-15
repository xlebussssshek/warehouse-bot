"""remove timezone from timestamp

Revision ID: 6839334009ea
Revises: 65296dc56b43
Create Date: 2026-02-16 03:58:16.146141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6839334009ea'
down_revision: Union[str, Sequence[str], None] = '65296dc56b43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Изменяем тип колонки, убирая timezone
    op.alter_column('transactions', 'timestamp',
                    existing_type=sa.DateTime(timezone=True),
                    type_=sa.DateTime(),
                    existing_nullable=True)

def downgrade():
    op.alter_column('transactions', 'timestamp',
                    existing_type=sa.DateTime(),
                    type_=sa.DateTime(timezone=True),
                    existing_nullable=True)
