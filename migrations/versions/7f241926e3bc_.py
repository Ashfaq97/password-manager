"""empty message

Revision ID: 7f241926e3bc
Revises: 6033e27b39f6
Create Date: 2022-05-06 11:52:43.995638

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f241926e3bc'
down_revision = '6033e27b39f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Users', sa.Column('locked', sa.Boolean(), nullable=True))
    op.add_column('Users', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('Users', sa.Column('locked_until', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Users', 'locked_until')
    op.drop_column('Users', 'last_login')
    op.drop_column('Users', 'locked')
    # ### end Alembic commands ###
