"""Initialize database

Revision ID: cd4b84e6ddab
Revises:
Create Date: 2022-08-25 20:44:46.679060

"""
from ...budgeter import db as budgeter_db

# revision identifiers, used by Alembic.
revision = 'cd4b84e6ddab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    budgeter_db.init_db()


def downgrade() -> None:
    pass
