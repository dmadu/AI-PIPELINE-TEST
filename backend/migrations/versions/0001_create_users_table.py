"""create users table

Revision ID: 0001_create_users
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_users'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_users'),
        sa.UniqueConstraint('username', name='uq_users_username'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index(
        'ix_users_username_lower',
        'users',
        [sa.text('lower(username)')],
        unique=False,
    )
    op.create_index(
        'ix_users_email_lower',
        'users',
        [sa.text('lower(email)')],
        unique=False,
    )


def downgrade():
    op.drop_index('ix_users_email_lower', table_name='users')
    op.drop_index('ix_users_username_lower', table_name='users')
    op.drop_table('users')
