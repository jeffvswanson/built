"""
Manages the database instance for the Built Budget API.
"""

import time

import sqlalchemy
from flask import Flask, g
from sqlalchemy.exc import NoResultFound

from budgeter.db_model.budget import Budget
from budgeter.db_model.payee import Payee


def get_db():
    if "db" not in g:
        engine = sqlalchemy.create_engine("SQLALCHEMY_DATABASE_URI", future=True)
        with engine.connect() as conn:
            connection_attempts = 0
            print("Attempting to connect to MySQL database...")
            while True:
                response = conn.execute(sqlalchemy.text("SELECT 'hello, budgeter'"))
                if response:
                    print("MySQL database connection established!")
                    break
                elif connection_attempts > 9:
                    raise NoResultFound(
                        "The MySQL database could not connect after "
                        f"{connection_attempts} connection attempts."
                    )
                else:
                    connection_attempts += 1
                    print(
                        "Connection attempt {connection_attempts}: "
                        "MySQL database connection could not be established. Waiting..."
                    )
                    time.sleep(1)

            g.db = conn
            return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    Budget.metadata.create_all(db)
    Payee.metadata.create_all(db)


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
