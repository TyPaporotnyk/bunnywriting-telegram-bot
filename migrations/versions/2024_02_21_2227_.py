"""empty message

Revision ID: 43563abd1b08
Revises: 
Create Date: 2024-02-21 22:27:03.249082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43563abd1b08'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admin',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('lead_status',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('speciality',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('author',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('full_name', sa.String(length=256), nullable=True),
    sa.Column('contact', sa.String(length=256), nullable=True),
    sa.Column('raiting', sa.Float(), nullable=True),
    sa.Column('busyness', sa.Float(), nullable=True),
    sa.Column('plane_busyness', sa.Float(), nullable=True),
    sa.Column('card_number', sa.String(length=256), nullable=True),
    sa.Column('crm_id', sa.BigInteger(), nullable=True),
    sa.Column('admin_id', sa.BigInteger(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['admin.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_author_admin_id'), 'author', ['admin_id'], unique=False)
    op.create_index(op.f('ix_author_crm_id'), 'author', ['crm_id'], unique=False)
    op.create_table('authors_specialties',
    sa.Column('author_id', sa.BigInteger(), nullable=True),
    sa.Column('speciality_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ),
    sa.ForeignKeyConstraint(['speciality_id'], ['speciality.id'], )
    )
    op.create_table('lead',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('status_id', sa.BigInteger(), nullable=True),
    sa.Column('author_id', sa.BigInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['author.id'], ),
    sa.ForeignKeyConstraint(['status_id'], ['lead_status.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lead_author_id'), 'lead', ['author_id'], unique=False)
    op.create_index(op.f('ix_lead_status_id'), 'lead', ['status_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_lead_status_id'), table_name='lead')
    op.drop_index(op.f('ix_lead_author_id'), table_name='lead')
    op.drop_table('lead')
    op.drop_table('authors_specialties')
    op.drop_index(op.f('ix_author_crm_id'), table_name='author')
    op.drop_index(op.f('ix_author_admin_id'), table_name='author')
    op.drop_table('author')
    op.drop_table('speciality')
    op.drop_table('lead_status')
    op.drop_table('admin')
    # ### end Alembic commands ###
