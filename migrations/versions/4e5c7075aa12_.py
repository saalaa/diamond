"""Added indexes

Revision ID: 4e5c7075aa12
Revises: 1c71b9014d19
Create Date: 2016-11-08 12:15:26.841347

"""

# revision identifiers, used by Alembic.
revision = '4e5c7075aa12'
down_revision = '1c71b9014d19'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index('idx_document_active', 'documents', ['active'], unique=False)
    op.create_index('idx_document_slug', 'documents', ['slug'], unique=False)
    op.create_index('idx_document_slug_active', 'documents', ['slug', 'active'], unique=True)
    op.create_index('idx_metadata_key_value', 'metadata', ['key', 'value'], unique=False)
    op.create_index('idx_metadata_slug', 'metadata', ['slug'], unique=False)
    op.create_index('idx_parameter_key', 'parameters', ['key'], unique=False)


def downgrade():
    op.drop_index('idx_parameter_key', table_name='parameters')
    op.drop_index('idx_metadata_slug', table_name='metadata')
    op.drop_index('idx_metadata_key_value', table_name='metadata')
    op.drop_index('idx_document_slug_active', table_name='documents')
    op.drop_index('idx_document_slug', table_name='documents')
    op.drop_index('idx_document_active', table_name='documents')
