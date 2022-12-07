"""Create expenses table

Revision ID: 011be5e3e399
Revises: 
Create Date: 2022-12-04 15:47:30.090953

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011be5e3e399'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'expense',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('original_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('amount_without_taxes', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('time', sa.DateTime(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('tags', sa.ARRAY(sa.String), nullable=False),
        sa.Column('original_json', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('expense')
