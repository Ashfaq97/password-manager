"""empty message

Revision ID: 74245096ea03
Revises: 7f241926e3bc
Create Date: 2022-05-13 12:22:43.799352

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74245096ea03'
down_revision = '7f241926e3bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Infopage', sa.Column('owner', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Infopage', 'owner')
    # ### end Alembic commands ###
