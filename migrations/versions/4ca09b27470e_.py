"""Fixed slug-active index

Revision ID: 4ca09b27470e
Revises: 4e5c7075aa12
Create Date: 2016-11-09 14:22:35.851011

"""

# revision identifiers, used by Alembic.
revision = '4ca09b27470e'
down_revision = '4e5c7075aa12'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_index('idx_document_slug_active', table_name='documents')
    op.create_index('idx_document_slug_active', 'documents', ['slug', 'active'], unique=False)


def downgrade():
    op.drop_index('idx_document_slug_active', table_name='documents')
    op.create_index('idx_document_slug_active', 'documents', ['slug', 'active'], unique=1)
