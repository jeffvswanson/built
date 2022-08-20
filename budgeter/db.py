"""
Manages the database instance for the Built Budget API.
"""

import sqlalchemy
from flask import Flask, g
from sqlalchemy.exc import NoResultFound

from budgeter.dbschema.budget import Budget
from budgeter.dbschema.payee import Payee


def get_db():
    if 'db' not in g:
        engine = sqlalchemy.create_engine('SQLALCHEMY_DATABASE_URI', future=True)
        with engine.connect() as conn:
            response = conn.execute(sqlalchemy.text("SELECT 'hello, budgeter'"))
            if not response:
                raise NoResultFound("The MySQL database could not connect.")

            g.db = conn
            return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    Budget.metadata.create_all(db)
    Payee.metadata.create_all(db)


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
