"""remove timezone from timestamp

Revision ID: 65296dc56b43
Revises: 9fa09d705a9a
Create Date: 2026-02-16 03:54:53.987170

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65296dc56b43'
down_revision: Union[str, Sequence[str], None] = '9fa09d705a9a'
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
