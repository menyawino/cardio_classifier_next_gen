from alembic import op
import sqlalchemy as sa

revision = '20250821_0002'
down_revision = '20250821_0001'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String, nullable=False),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.add_column('variants', sa.Column('created_by', sa.Integer, nullable=True))
    op.create_index('ix_variants_created_by', 'variants', ['created_by'])

    op.create_table(
        'classification_events',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('variant_id', sa.Integer, nullable=False),
        sa.Column('user_id', sa.Integer, nullable=True),
        sa.Column('classification', sa.String, nullable=False),
        sa.Column('evidence', sa.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('ix_classification_events_variant_id', 'classification_events', ['variant_id'])
    op.create_index('ix_classification_events_user_id', 'classification_events', ['user_id'])


def downgrade():
    op.drop_index('ix_classification_events_user_id', table_name='classification_events')
    op.drop_index('ix_classification_events_variant_id', table_name='classification_events')
    op.drop_table('classification_events')
    op.drop_index('ix_variants_created_by', table_name='variants')
    op.drop_column('variants', 'created_by')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
