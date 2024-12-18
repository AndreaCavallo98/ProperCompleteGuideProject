"""fix

Revision ID: ae90c4997175
Revises: 2769e910db3c
Create Date: 2024-11-18 10:18:23.916442

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel # added


# revision identifiers, used by Alembic.
revision: str = 'ae90c4997175'
down_revision: Union[str, None] = '2769e910db3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'user',
        sa.Column('is_admin', sa.Boolean(), nullable=True)
    )
    op.execute('UPDATE "user" SET is_admin = false')
    op.alter_column('user', 'is_admin', nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'is_admin')
    # ### end Alembic commands ###
