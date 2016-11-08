"""Migrations initialization

Revision ID: 1c71b9014d19
Revises: None
Create Date: 2016-11-08 10:44:44.138569

"""

# revision identifiers, used by Alembic.
revision = '1c71b9014d19'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('metadata',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parameters',
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('key')
    )
    op.create_table('users',
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('slug')
    )
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['author'], ['users.slug'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('documents')
    op.drop_table('users')
    op.drop_table('parameters')
    op.drop_table('metadata')
