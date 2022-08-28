"""Initialize database tables

Revision ID: 2a79831c1c7a
Revises: 
Create Date: 2022-08-27 16:23:15.094318

"""

import sqlalchemy
from alembic import op, context

from budgeter.db_model.budget import Budget
from budgeter.db_model.payee import Payee

# revision identifiers, used by Alembic.
revision = "2a79831c1c7a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    config = context.config
    engine = sqlalchemy.engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
    )
    with engine.connect() as conn:
        Budget.metadata.create_all(conn)
        Payee.metadata.create_all(conn)


def downgrade() -> None:
    op.drop_table(Budget.__tablename__)
    op.drop_table(Payee.__tablename__)
