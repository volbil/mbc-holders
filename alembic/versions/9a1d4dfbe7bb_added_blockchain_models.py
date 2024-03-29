"""Added blockchain models

Revision ID: 9a1d4dfbe7bb
Revises: 
Create Date: 2024-03-13 22:15:25.146648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9a1d4dfbe7bb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('service_blocks',
    sa.Column('prev_blockhash', sa.String(length=64), nullable=False),
    sa.Column('blockhash', sa.String(length=64), nullable=False),
    sa.Column('transactions', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('timestamp', sa.Integer(), nullable=False),
    sa.Column('height', sa.Integer(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_blocks_blockhash'), 'service_blocks', ['blockhash'], unique=False)
    op.create_index(op.f('ix_service_blocks_prev_blockhash'), 'service_blocks', ['prev_blockhash'], unique=False)
    op.create_table('service_inputs',
    sa.Column('blockhash', sa.String(length=64), nullable=False),
    sa.Column('txid', sa.String(length=64), nullable=False),
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_inputs_blockhash'), 'service_inputs', ['blockhash'], unique=False)
    op.create_index(op.f('ix_service_inputs_txid'), 'service_inputs', ['txid'], unique=False)
    op.create_table('service_outputs',
    sa.Column('blockhash', sa.String(length=64), nullable=False),
    sa.Column('shortcut', sa.String(length=70), nullable=False),
    sa.Column('address', sa.String(length=70), nullable=False),
    sa.Column('txid', sa.String(length=64), nullable=False),
    sa.Column('amount', sa.Numeric(precision=28, scale=8), nullable=False),
    sa.Column('spent', sa.Boolean(), nullable=False),
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_outputs_address'), 'service_outputs', ['address'], unique=False)
    op.create_index(op.f('ix_service_outputs_blockhash'), 'service_outputs', ['blockhash'], unique=False)
    op.create_index(op.f('ix_service_outputs_shortcut'), 'service_outputs', ['shortcut'], unique=False)
    op.create_index(op.f('ix_service_outputs_txid'), 'service_outputs', ['txid'], unique=False)
    op.create_table('service_transactions',
    sa.Column('blockhash', sa.String(length=64), nullable=False),
    sa.Column('txid', sa.String(length=64), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('timestamp', sa.Integer(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_service_transactions_blockhash'), 'service_transactions', ['blockhash'], unique=False)
    op.create_index(op.f('ix_service_transactions_txid'), 'service_transactions', ['txid'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_service_transactions_txid'), table_name='service_transactions')
    op.drop_index(op.f('ix_service_transactions_blockhash'), table_name='service_transactions')
    op.drop_table('service_transactions')
    op.drop_index(op.f('ix_service_outputs_txid'), table_name='service_outputs')
    op.drop_index(op.f('ix_service_outputs_shortcut'), table_name='service_outputs')
    op.drop_index(op.f('ix_service_outputs_blockhash'), table_name='service_outputs')
    op.drop_index(op.f('ix_service_outputs_address'), table_name='service_outputs')
    op.drop_table('service_outputs')
    op.drop_index(op.f('ix_service_inputs_txid'), table_name='service_inputs')
    op.drop_index(op.f('ix_service_inputs_blockhash'), table_name='service_inputs')
    op.drop_table('service_inputs')
    op.drop_index(op.f('ix_service_blocks_prev_blockhash'), table_name='service_blocks')
    op.drop_index(op.f('ix_service_blocks_blockhash'), table_name='service_blocks')
    op.drop_table('service_blocks')
    # ### end Alembic commands ###
