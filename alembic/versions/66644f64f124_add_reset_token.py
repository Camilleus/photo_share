"""add reset_token

Revision ID: 66644f64f124
Revises: 52c6c098d9ba
Create Date: 2024-02-28 15:00:07.166501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66644f64f124'
down_revision: Union[str, None] = '52c6c098d9ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('reset_token', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'reset_token')
    # ### end Alembic commands ###