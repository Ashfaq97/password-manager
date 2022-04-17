"""empty message

Revision ID: 07b4941a2436
Revises: 1f1718fe764c
Create Date: 2022-04-16 20:51:23.558731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07b4941a2436'
down_revision = '1f1718fe764c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Users', sa.Column('email', sa.Text(), nullable=True))
    op.add_column('Users', sa.Column('auth_code', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Users', 'auth_code')
    op.drop_column('Users', 'email')
    # ### end Alembic commands ###
