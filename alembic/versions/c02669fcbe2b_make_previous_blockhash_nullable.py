"""Make previous blockhash nullable

Revision ID: c02669fcbe2b
Revises: 9a1d4dfbe7bb
Create Date: 2024-03-13 23:02:02.728180

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c02669fcbe2b'
down_revision: Union[str, None] = '9a1d4dfbe7bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('service_blocks', 'prev_blockhash',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('service_blocks', 'prev_blockhash',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    # ### end Alembic commands ###