from alembic import op
import sqlalchemy as sa

revision = '20250821_0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'variants',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('hgvs', sa.String, nullable=False),
        sa.Column('genome_build', sa.String, nullable=False),
        sa.Column('classification', sa.String, nullable=False),
        sa.Column('evidence', sa.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index('ix_variants_hgvs', 'variants', ['hgvs'])

def downgrade():
    op.drop_index('ix_variants_hgvs', table_name='variants')
    op.drop_table('variants')
