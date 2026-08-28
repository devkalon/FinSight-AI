"""Initial normalized schema for FinSight AI

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-28

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # 2. Profiles
    op.create_table(
        'profiles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('preferred_currency', sa.String(length=10), nullable=False, default='INR'),
        sa.Column('monthly_income', sa.Numeric(precision=14, scale=2), nullable=False, default=0.00),
        sa.Column('risk_tolerance', sa.String(length=50), nullable=False, default='moderate'),
        sa.Column('country_code', sa.String(length=10), nullable=False, default='IN'),
        sa.Column('tax_regime', sa.String(length=50), nullable=False, default='new'),
        sa.Column('preferred_guru', sa.String(length=50), nullable=False, default='balanced'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 3. Categories
    op.create_table(
        'categories',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('group_type', sa.String(length=50), nullable=False, default='Need'),
        sa.Column('icon', sa.String(length=50), nullable=False, default='Tag'),
        sa.Column('color', sa.String(length=20), nullable=False, default='#6366F1'),
        sa.Column('is_custom', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 4. Merchants
    op.create_table(
        'merchants',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('normalized_name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('default_category_id', sa.String(length=36), sa.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('icon', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 5. Transaction Sources
    op.create_table(
        'transaction_sources',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False),
        sa.Column('account_identifier_masked', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 6. Transactions
    op.create_table(
        'transactions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_id', sa.String(length=36), sa.ForeignKey('transaction_sources.id', ondelete='SET NULL'), nullable=True),
        sa.Column('category_id', sa.String(length=36), sa.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('merchant_id', sa.String(length=36), sa.ForeignKey('merchants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, default='INR'),
        sa.Column('transaction_type', sa.String(length=20), nullable=False, default='debit'),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False, default='UPI'),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=False, default=1.0000),
        sa.Column('is_subscription', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('raw_extracted_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    op.create_index('ix_transactions_user_date', 'transactions', ['user_id', 'transaction_date'])

    # 7. Budgets & Budget Categories
    op.create_table(
        'budgets',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=False, default='monthly'),
        sa.Column('total_limit', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('alert_threshold_percentage', sa.Integer(), nullable=False, default=80),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    op.create_table(
        'budget_categories',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('budget_id', sa.String(length=36), sa.ForeignKey('budgets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category_id', sa.String(length=36), sa.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('allocated_limit', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 8. Financial Goals & Contributions
    op.create_table(
        'financial_goals',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False, default='Wealth Creation'),
        sa.Column('target_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('current_amount', sa.Numeric(precision=14, scale=2), nullable=False, default=0.00),
        sa.Column('currency', sa.String(length=10), nullable=False, default='INR'),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('expected_return_rate', sa.Numeric(precision=5, scale=2), nullable=False, default=12.00),
        sa.Column('status', sa.String(length=50), nullable=False, default='in_progress'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    op.create_table(
        'goal_contributions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('goal_id', sa.String(length=36), sa.ForeignKey('financial_goals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('transaction_id', sa.String(length=36), sa.ForeignKey('transactions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('contribution_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # 9. Documents & Chunks
    op.create_table(
        'financial_documents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False, default=0),
        sa.Column('storage_path', sa.Text(), nullable=False),
        sa.Column('processing_status', sa.String(length=50), nullable=False, default='processed'),
        sa.Column('parsed_metadata', sa.JSON(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('financial_documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # 10. Guru Profiles & Principles
    op.create_table(
        'guru_profiles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('guru_code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('core_mantra', sa.Text(), nullable=False),
        sa.Column('philosophy_description', sa.Text(), nullable=False),
        sa.Column('avatar_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    op.create_table(
        'guru_principles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('guru_id', sa.String(length=36), sa.ForeignKey('guru_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('principle_order', sa.Integer(), nullable=False, default=1),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # 11. Advice Sessions & Recommendations
    op.create_table(
        'advice_sessions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('guru_id', sa.String(length=36), sa.ForeignKey('guru_profiles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False, default='Financial Strategy Consultation'),
        sa.Column('session_type', sa.String(length=50), nullable=False, default='chat'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    op.create_table(
        'recommendations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('session_id', sa.String(length=36), sa.ForeignKey('advice_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('guru_id', sa.String(length=36), sa.ForeignKey('guru_profiles.id', ondelete='SET NULL'), nullable=True),
        sa.Column('category_id', sa.String(length=36), sa.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('topic', sa.String(length=255), nullable=False),
        sa.Column('recommendation_text', sa.Text(), nullable=False),
        sa.Column('action_items', sa.JSON(), nullable=True),
        sa.Column('estimated_savings_impact', sa.Numeric(precision=14, scale=2), nullable=False, default=0.00),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

    # 12. Subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('merchant_id', sa.String(length=36), sa.ForeignKey('merchants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('category_id', sa.String(length=36), sa.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('service_name', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, default='INR'),
        sa.Column('billing_cycle', sa.String(length=50), nullable=False, default='monthly'),
        sa.Column('next_billing_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 13. Anomalies
    op.create_table(
        'anomalies',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('transaction_id', sa.String(length=36), sa.ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('anomaly_type', sa.String(length=50), nullable=False, default='spend_spike'),
        sa.Column('severity', sa.String(length=20), nullable=False, default='medium'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('z_score', sa.Numeric(precision=6, scale=3), nullable=False, default=0.000),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )

    # 14. Financial Scores
    op.create_table(
        'financial_scores',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('composite_score', sa.Integer(), nullable=False),
        sa.Column('rating', sa.String(length=50), nullable=False),
        sa.Column('emergency_fund_score', sa.Integer(), nullable=False),
        sa.Column('savings_rate_score', sa.Integer(), nullable=False),
        sa.Column('budget_adherence_score', sa.Integer(), nullable=False),
        sa.Column('debt_and_burn_score', sa.Integer(), nullable=False),
        sa.Column('calculation_metadata', sa.JSON(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(), nullable=False)
    )

    # 15. Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=True),
        sa.Column('client_ip', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('financial_scores')
    op.drop_table('anomalies')
    op.drop_table('subscriptions')
    op.drop_table('recommendations')
    op.drop_table('advice_sessions')
    op.drop_table('guru_principles')
    op.drop_table('guru_profiles')
    op.drop_table('document_chunks')
    op.drop_table('financial_documents')
    op.drop_table('goal_contributions')
    op.drop_table('financial_goals')
    op.drop_table('budget_categories')
    op.drop_table('budgets')
    op.drop_table('transactions')
    op.drop_table('transaction_sources')
    op.drop_table('merchants')
    op.drop_table('categories')
    op.drop_table('profiles')
    op.drop_table('users')
