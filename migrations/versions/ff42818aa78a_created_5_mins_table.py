"""created 5 mins table

Revision ID: ff42818aa78a
Revises: a606ef4069c0
Create Date: 2021-06-04 11:25:20.767369

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff42818aa78a'
down_revision = 'a606ef4069c0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('five_mins_coin_state',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('coin_name', sa.String(length=100), nullable=False),
    sa.Column('trigger_one_status', sa.Boolean(), nullable=True),
    sa.Column('trigger_two_status', sa.Boolean(), nullable=True),
    sa.Column('is_holding', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('coin_name'),
    sa.UniqueConstraint('coin_name')
    )
    op.create_index(op.f('ix_five_mins_coin_state_is_holding'), 'five_mins_coin_state', ['is_holding'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_five_mins_coin_state_is_holding'), table_name='five_mins_coin_state')
    op.drop_table('five_mins_coin_state')
    # ### end Alembic commands ###
