"""Added index to block height

Revision ID: 1640ab089b34
Revises: e97ca5f11ed3
Create Date: 2024-03-17 19:41:10.304699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1640ab089b34'
down_revision: Union[str, None] = 'e97ca5f11ed3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_service_blocks_height'), 'service_blocks', ['height'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_service_blocks_height'), table_name='service_blocks')
    # ### end Alembic commands ###
