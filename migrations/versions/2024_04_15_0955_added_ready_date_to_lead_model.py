"""Added ready date to lead model

Revision ID: 8ec091a8eb0f
Revises: e6732d1cfa72
Create Date: 2024-04-15 09:55:05.125205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ec091a8eb0f'
down_revision: Union[str, None] = 'e6732d1cfa72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lead', sa.Column('ready_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('lead', 'ready_date')
    # ### end Alembic commands ###
