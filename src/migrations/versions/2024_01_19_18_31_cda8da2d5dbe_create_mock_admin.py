"""create mock admin

Revision ID: cda8da2d5dbe
Revises: 72de143455bb
Create Date: 2024-01-19 18:31:42.258546

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cda8da2d5dbe"
down_revision: Union[str, None] = "72de143455bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        'INSERT INTO "user" ("username", "password") '
        "VALUES ('admin@admin.com', "
        "'$2b$12$7v.V506j22X7wXvItaFpweVZlYQVpgeXbgbFRMP28teYUSt3O4agG')"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DELETE FROM "user" WHERE "username"=\'admin@admin.com\'')
    # ### end Alembic commands ###
