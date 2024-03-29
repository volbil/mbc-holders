"""Added movements to block model

Revision ID: 8263b99857cc
Revises: fd4e079083ae
Create Date: 2024-03-16 00:46:43.383707

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8263b99857cc'
down_revision: Union[str, None] = 'fd4e079083ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_blocks', sa.Column('movements', postgresql.JSONB(astext_type=sa.Text()), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('service_blocks', 'movements')
    # ### end Alembic commands ###
