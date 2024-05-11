"""add mode_id to chat_scheme

Revision ID: 3d5ea0aea7d4
Revises: 6f855d426c34
Create Date: 2024-05-11 23:45:29.635351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '3d5ea0aea7d4'
down_revision: Union[str, None] = '6f855d426c34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat', sa.Column('mode_id', sa.Integer(), nullable=True))
    op.create_foreign_key('foreignkey', 'chat', 'mode', ['mode_id'], ['id'])
    op.alter_column('classifier_version', 'description',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('classifier_version', 'description',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_constraint('foreignkey', 'chat', type_='foreignkey')
    op.drop_column('chat', 'mode_id')
    # ### end Alembic commands ###
