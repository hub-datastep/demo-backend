"""remove status column from file

Revision ID: 58cef6fde2f9
Revises: 7a5145a37216
Create Date: 2024-01-18 13:20:25.423623

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "58cef6fde2f9"
down_revision: Union[str, None] = "7a5145a37216"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "file",
        sa.Column(
            "original_filename", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
    )
    op.add_column(
        "file",
        sa.Column(
            "storage_filename", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
    )
    op.drop_column("file", "mark")
    op.drop_column("file", "url")
    op.drop_column("file", "name_ru")
    op.drop_column("file", "status")
    op.drop_column("file", "name_en")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "file", sa.Column("name_en", sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "file", sa.Column("status", sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "file", sa.Column("name_ru", sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "file", sa.Column("url", sa.VARCHAR(), autoincrement=False, nullable=False)
    )
    op.add_column(
        "file", sa.Column("mark", sa.BOOLEAN(), autoincrement=False, nullable=False)
    )
    op.drop_column("file", "storage_filename")
    op.drop_column("file", "original_filename")
    # ### end Alembic commands ###
