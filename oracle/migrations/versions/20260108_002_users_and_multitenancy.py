"""Add users table with email verification and multi-tenancy support

Revision ID: 002_users_multitenancy
Revises: 001_initial_schema
Create Date: 2026-01-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_users_multitenancy'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Export Alembic revision identifiers
__all__ = ['revision', 'down_revision', 'branch_labels', 'depends_on', 'upgrade', 'downgrade']


def upgrade() -> None:
    """Create users table and add multi-tenancy columns."""
    
    # Create users table with email verification support
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),  # Nullable for OAuth users
        sa.Column('full_name', sa.String(200), nullable=True),
        
        # Email verification
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_verification_token', sa.String(255), nullable=True, index=True),
        sa.Column('email_verification_expires', sa.DateTime(timezone=True), nullable=True),
        
        # Password reset
        sa.Column('password_reset_token', sa.String(255), nullable=True, index=True),
        sa.Column('password_reset_expires', sa.DateTime(timezone=True), nullable=True),
        
        # OAuth support (for Google/Microsoft login)
        sa.Column('oauth_provider', sa.String(50), nullable=True),  # 'google', 'microsoft', 'github'
        sa.Column('oauth_provider_id', sa.String(255), nullable=True),  # External user ID
        
        # Account status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        
        # Roles and permissions
        sa.Column('roles', postgresql.JSONB(), nullable=False, server_default='["user"]'),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_password_change', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create unique constraint for OAuth provider + provider_id
    op.create_index(
        'idx_users_oauth_unique',
        'users',
        ['oauth_provider', 'oauth_provider_id'],
        unique=True,
        postgresql_where=sa.text("oauth_provider IS NOT NULL")
    )
    
    # Add user_id column to alerts table for data isolation
    op.add_column(
        'alerts',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    )
    
    # Add user_id column to threat_intelligence table
    op.add_column(
        'threat_intelligence',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    )
    
    # Create email verification tokens table for better security
    op.create_table(
        'verification_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('token', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('token_type', sa.String(50), nullable=False),  # 'email_verification', 'password_reset'
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    # Create user sessions table for tracking active sessions
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('session_token', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('refresh_token', sa.String(255), unique=True, nullable=True, index=True),
        sa.Column('device_info', sa.String(500), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    # Create audit log table for security actions
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('action', sa.String(100), nullable=False, index=True),
        sa.Column('resource_type', sa.String(100), nullable=True),
        sa.Column('resource_id', sa.String(255), nullable=True),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
    )
    
    # Create index for audit log queries
    op.create_index(
        'idx_audit_log_user_action',
        'audit_log',
        ['user_id', 'action', 'created_at']
    )


def downgrade() -> None:
    """Remove users table and multi-tenancy columns."""
    # Drop audit log
    op.drop_index('idx_audit_log_user_action', table_name='audit_log')
    op.drop_table('audit_log')
    
    # Drop user sessions
    op.drop_table('user_sessions')
    
    # Drop verification tokens
    op.drop_table('verification_tokens')
    
    # Remove user_id from threat_intelligence
    op.drop_column('threat_intelligence', 'user_id')
    
    # Remove user_id from alerts
    op.drop_column('alerts', 'user_id')
    
    # Drop users table
    op.drop_index('idx_users_oauth_unique', table_name='users')
    op.drop_table('users')
