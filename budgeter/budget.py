"""
budget.py contains the routes and methods for Flask to interact with the budget database
table.
"""

import datetime
from http import HTTPStatus
from typing import Tuple

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
db = budgeter_db.get_db()


@bp.route("/")
def budget_view() -> Tuple[int, dict]:
    budget = db.execute(
        sqlalchemy.text(
            "SELECT"
            " item, dollars, cents, flow, p.payor_name, p.payee_name, transaction_date"
            " FROM budget b"
            " JOIN p.payor_name ON b.payor_id = p.id"
            " AND p.payee_name ON b.payee_id = p.id"
        )
    ).fetchall()
    return HTTPStatus.OK, {bp.name: budget}


@bp.route("/items/", methods=("GET", "POST"))
def create() -> Tuple[int, dict]:
    if request.method == "POST":
        data = utils.parse_json(json_data=request.get_json(), schema=BudgetItemSchema())

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
        db.commit()
        return HTTPStatus.CREATED, {
            "message": "Created new budget item.",
            "key": result.inserted_primary_key[0],
        }
    elif request.method == "GET":
        return budget_view()


def get_budget_item(id: int) -> Tuple[int, dict]:
    """
    get_budget_item retrieves a single row from a database representing a budget row.

    Parameters
    ----------
    id : int
        The primary key of the budget item row.

    Returns
    -------
    Tuple[int, dict]
        The HTTP status code and the query result for a single budget item.
    """
    item = db.execute(
        "SELECT"
        "item, dollars, cents, flow, p.payor_name, p.payee_name, transaction_date"
        " FROM budget b"
        " JOIN p.payor_name ON b.payor_id = p.id"
        " AND p.payee_name ON b.payee_id = p.id"
        " WHERE b.id = ?",
        (id,),
    ).fetchone()
    if item is None:
        abort(HTTPStatus.NOT_FOUND, f"Budget item id {id} does not exist.")
    return HTTPStatus.OK, item


@bp.route("/items/<int:id>", methods=("GET", "POST", "DELETE"))
def update(id: int):
    get_status_code, get_result = get_budget_item(id)
    if request.method == "GET":
        return get_status_code, get_result

    if request.method == "POST":
        data = utils.parse_json(json_data=request.get_json(), schema=BudgetItemSchema())
        dollars = data["dollars"] if data.get("dollars") is None else get_result.dollars
        cents = data["cents"] if data.get("cents") is None else get_result.cents
        flow = data["flow"] if data.get("flow") else get_result.flow
        payor_id = data["payor"] if data.get("payor") else get_result.payor_id
        payee_id = data["payee"] if data.get("payee") else get_result.payee_id
        modified_date = (
            data["transaction_date"]
            if data.get("transaction_date")
            else datetime.datetime.now(pytz.UTC).isoformat()
        )
        result = db.execute(
            "UPDATE budget SET "
            " item = ?, dollars = ?, cents = ?, flow = ?, payor_id = ?, "
            " payee_id = ?, modified_date = ? "
            " WHERE id = ?",
            (
                get_result.item,
                dollars,
                cents,
                flow,
                payor_id,
                payee_id,
                modified_date,
                id,
            ),
        )
        db.commit()
        return HTTPStatus.OK, result
    elif request.method == "DELETE":
        if get_result:
            query = sqlalchemy.delete(budget_table).where(budget_table.id == id)
            db.execute(query)
            db.commit()
            return HTTPStatus.NO_CONTENT, {}
