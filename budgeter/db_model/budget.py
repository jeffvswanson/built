"""
Table definition for MySQL budget table.
"""

import sqlalchemy.dialects.mysql as mysql
from sqlalchemy import Column
from budgeter.dbschema import Base, UUID_LENGTH


class Budget(Base):
    __tablename__ = "budget"

    id = Column(mysql.INTEGER(unsigned=True), primary_key=True, nullable=False, autoincrement="auto")
    item = Column(mysql.VARCHAR(length=200), nullable=False)
    dollars = Column(mysql.BIGINT(unsigned=True))
    cents = Column(mysql.TINYINT(unsigned=True))
    flow = Column(mysql.CHAR(length=1))
    payor_id = Column(mysql.VARCHAR(length=UUID_LENGTH), nullable=False)
    payee_id = Column(mysql.VARCHAR(length=UUID_LENGTH), nullable=False)
    transaction_date = Column(mysql.DATE, nullable=False)
    date_modified = Column(mysql.DATE)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"id={repr(self.id)}, "
            f"item={repr(self.item)}, "
            f"dollars={repr(self.dollars)}, "
            f"cents={repr(self.cents)}, "
            f"flow={repr(self.flow)}, "
            f"payor_id={repr(self.payor_id)}, "
            f"payee_id={repr(self.payee_id)}, "
            f"transaction_date={repr(self.transaction_date)}, "
            f"date_modified={repr(self.date_modified)}"
            ")"
        )
