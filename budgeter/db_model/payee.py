"""
Table definition for MySQL payee table.
Payee can include payor or payee, I can't think of a better entity name.
"""

import sqlalchemy.dialects.mysql as mysql
from sqlalchemy import Column
from budgeter.db_model import Base, UUID_LENGTH


class Payee(Base):
    __tablename__ = "payee"

    id = Column(mysql.VARCHAR(length=UUID_LENGTH), primary_key=True, nullable=False, unique=True)
    name = Column(mysql.VARCHAR(length=200), nullable=False)
    e_mail = Column(mysql.VARCHAR(length=200), nullable=False)
    phone = Column(mysql.VARCHAR(length=15), nullable=False)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"id={repr(self.id)}, "
            f"name={repr(self.name)}, "
            f"e_mail={repr(self.e_mail)}, "
            f"phone={repr(self.phone)}"
            "\n)"
        )
