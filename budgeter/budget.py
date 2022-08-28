"""
budget.py contains the routes and methods for Flask to interact with the budget database
table.
"""

import datetime
from http import HTTPStatus

import pytz
import sqlalchemy
from flask import Blueprint, request
from werkzeug.exceptions import abort

import budgeter.db as budgeter_db
import budgeter.utils as utils
from budgeter.db_model.budget import Budget
from budgeter.db_model.payee import Payee
from budgeter.schemas.budget_item import BudgetItemSchema

bp = Blueprint("budget", __name__, url_prefix="/budget")

budget_table = Budget()
payee_table = Payee()


@bp.route("/")
def budget_view() -> dict:
    db = budgeter_db.get_db()
    with db.connect() as conn:
        budget = conn.execute(sqlalchemy.select(Budget)).fetchall()
        return {"status": HTTPStatus.OK, "result": {bp.name: budget}}


@bp.route("/items/", methods=("GET", "POST"))
def create() -> dict:
    if request.method == "POST":
        data = utils.parse_json(json_data=request.get_json(), schema=BudgetItemSchema())

        db = budgeter_db.get_db()
        with db.connect() as conn:
            # Keys better be there marshmallow, but can be adjusted to use .get() method
            query = sqlalchemy.insert(budget_table).values(
                item=data["item"],
                dollars=data["dollars"],
                cents=data["cents"],
                flow=data["flow"],
                payor=data["payor"],
                payee=data["payee"],
                transaction_date=data["transaction_date"],
            )
            result = db.execute(query)
            conn.commit()
            return {
                "status": HTTPStatus.CREATED,
                "result": {
                    "message": "Created new budget item.",
                    "key": result.inserted_primary_key[0],
                },
            }
    elif request.method == "GET":
        return budget_view()


def get_budget_item(id: int) -> dict:
    """
    get_budget_item retrieves a single row from a database representing a budget row.

    Parameters
    ----------
    id : int
        The primary key of the budget item row.

    Returns
    -------
    dict
        The HTTP status code and the query result for a single budget item.
    """
    db = budgeter_db.get_db()
    with db.connect() as conn:
        item = conn.execute(sqlalchemy.select(Budget).where(Budget.id == id)).fetchone()
        if item is None:
            abort(HTTPStatus.NOT_FOUND, f"Budget item id {id} does not exist.")
        return {"status": HTTPStatus.OK, "result": item}


@bp.route("/items/<int:id>", methods=("GET", "POST", "DELETE"))
def update(id: int):
    budget_item = get_budget_item(id)
    if request.method == "GET":
        return budget_item

    db = budgeter_db.get_db()
    if request.method == "POST":
        data = utils.parse_json(json_data=request.get_json(), schema=BudgetItemSchema())
        dollars = (
            data["dollars"]
            if data.get("dollars") is None
            else budget_item["result"].dollars
        )
        cents = (
            data["cents"] if data.get("cents") is None else budget_item["result"].cents
        )
        flow = data["flow"] if data.get("flow") else budget_item["result"].flow
        payor_id = (
            data["payor"] if data.get("payor") else budget_item["result"].payor_id
        )
        payee_id = (
            data["payee"] if data.get("payee") else budget_item["result"].payee_id
        )
        modified_date = (
            data["transaction_date"]
            if data.get("transaction_date")
            else datetime.datetime.now(pytz.UTC).isoformat()
        )
        with db.connect() as conn:
            result = conn.execute(
                "UPDATE budget SET "
                " item = ?, dollars = ?, cents = ?, flow = ?, payor_id = ?, "
                " payee_id = ?, modified_date = ? "
                " WHERE id = ?",
                (
                    budget_item["result"].item,
                    dollars,
                    cents,
                    flow,
                    payor_id,
                    payee_id,
                    modified_date,
                    id,
                ),
            )
            conn.commit()
        return {"status": HTTPStatus.OK, "result": result}
    elif request.method == "DELETE":
        if budget_item["result"]:
            with db.connect() as conn:
                query = sqlalchemy.delete(budget_table).where(budget_table.id == id)
                conn.execute(query)
                conn.commit()
                return {"status": HTTPStatus.NO_CONTENT, "result": {}}
