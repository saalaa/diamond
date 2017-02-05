"""empty message

Revision ID: 31d99ae9582a
Revises: b972a9695b11
Create Date: 2017-02-05 14:07:40.493352

"""

# revision identifiers, used by Alembic.
revision = '31d99ae9582a'
down_revision = 'b972a9695b11'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('documents', sa.Column('bytes_delta', sa.Integer(),
        nullable=False, server_default='0'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('documents', 'bytes_delta')
    # ### end Alembic commands ###