"""Added shortcut to input

Revision ID: fd4e079083ae
Revises: c02669fcbe2b
Create Date: 2024-03-14 01:23:03.433082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd4e079083ae'
down_revision: Union[str, None] = 'c02669fcbe2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service_inputs', sa.Column('shortcut', sa.String(length=70), nullable=False))
    op.create_index(op.f('ix_service_inputs_shortcut'), 'service_inputs', ['shortcut'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_service_inputs_shortcut'), table_name='service_inputs')
    op.drop_column('service_inputs', 'shortcut')
    # ### end Alembic commands ###
