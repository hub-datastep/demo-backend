"""fix classifier config brand param

Revision ID: 93cde6304c50
Revises: 0ab7ec220551
Create Date: 2024-09-06 13:39:07.086603

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "93cde6304c50"
down_revision: Union[str, None] = "2e5da2e577b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "classifier_config", sa.Column("is_use_params", sa.Boolean(), nullable=True)
    )
    op.add_column(
        "classifier_config",
        sa.Column("is_use_brand_recognition", sa.Boolean(), nullable=True),
    )
    op.alter_column(
        "classifier_config",
        "is_use_keywords_detection",
        existing_type=sa.BOOLEAN(),
        nullable=True,
    )
    op.drop_column("classifier_config", "use_params")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "classifier_config",
        sa.Column("use_params", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    op.alter_column(
        "classifier_config",
        "is_use_keywords_detection",
        existing_type=sa.BOOLEAN(),
        nullable=False,
    )
    op.drop_column("classifier_config", "is_use_brand_recognition")
    op.drop_column("classifier_config", "is_use_params")
    # ### end Alembic commands ###
