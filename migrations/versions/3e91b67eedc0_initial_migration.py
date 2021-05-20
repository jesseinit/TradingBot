"""Initial migration.

Revision ID: 3e91b67eedc0
Revises: 
Create Date: 2021-05-20 13:45:43.260992

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e91b67eedc0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('coin_state',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('coin_name', sa.String(length=100), nullable=False),
    sa.Column('trigger_one_status', sa.Boolean(), nullable=False),
    sa.Column('trigger_two_status', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('coin_name'),
    sa.UniqueConstraint('coin_name')
    )
    op.create_table('incoming_coin_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recieved_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('coin_name', sa.String(length=100), nullable=False),
    sa.Column('incoming_trigger', sa.String(length=10), nullable=False),
    sa.Column('trigger_status', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('incoming_coin_log')
    op.drop_table('coin_state')
    # ### end Alembic commands ###
