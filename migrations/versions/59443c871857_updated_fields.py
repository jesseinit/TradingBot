"""updated fields

Revision ID: 59443c871857
Revises: df2cbb6133ec
Create Date: 2021-05-21 00:12:22.470188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59443c871857'
down_revision = 'df2cbb6133ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coin_state', sa.Column('is_holding', sa.Boolean(), nullable=True))
    op.alter_column('coin_state', 'trigger_one_status',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('coin_state', 'trigger_two_status',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('coin_state', 'trigger_two_status',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('coin_state', 'trigger_one_status',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.drop_column('coin_state', 'is_holding')
    # ### end Alembic commands ###
