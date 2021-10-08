"""empty message

Revision ID: cec8ccfee1fd
Revises: 3cbcb60b4c52
Create Date: 2021-10-07 12:42:01.023093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cec8ccfee1fd'
down_revision = '3cbcb60b4c52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('globaldimensionvalues', 'globalDimensionId',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('globaldimensionvalues', 'globalDimensionId',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
