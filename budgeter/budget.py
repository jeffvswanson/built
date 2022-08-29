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
from budgeter.schemas.budget_item import BudgetItemSchema

bp = Blueprint("budget", __name__, url_prefix="/budget")


@bp.route("/")
def budget_view() -> dict:
    db = budgeter_db.get_db()
    with db.connect() as conn:
        budget = conn.execute(sqlalchemy.select(Budget)).fetchall()
        return {
            "status": HTTPStatus.OK,
            "result": [BudgetItemSchema().dump(row) for row in budget],
        }


@bp.route("/items/", methods=("GET", "POST"))
def create() -> dict:
    if request.method == "POST":
        data = utils.parse_json(json_data=request.get_json(), schema=BudgetItemSchema())

        db = budgeter_db.get_db()
        with db.connect() as conn:
            # Keys better be there marshmallow, but can be adjusted to use .get() method
            query = sqlalchemy.insert(Budget).values(
                item=data["item"],
                dollars=data["dollars"],
                cents=data["cents"],
                flow=data["flow"],
                payor_id=data["payor"],
                payee_id=data["payee"],
                transaction_date=data["transaction_date"],
            )
            result = conn.execute(query)
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
        return {"status": HTTPStatus.OK, "result": BudgetItemSchema().dump(item)}


@bp.route("/items/<int:id>", methods=("GET", "POST", "DELETE"))
def update(id: int):
    budget_item = get_budget_item(id)
    if request.method == "GET":
        return budget_item

    db = budgeter_db.get_db()
    if request.method == "POST":
        data = request.get_json()
        budget_item = budget_item["result"]
        id = budget_item.pop("id")  # Not part of the schema and we have it already.
        budget_item["item"] = data.get("item", budget_item["item"])
        budget_item["dollars"] = data.get("dollars", budget_item["dollars"])
        budget_item["cents"] = data.get("cents", budget_item["cents"])
        budget_item["flow"] = data.get("flow", budget_item["flow"])
        budget_item["payor_id"] = data.get("payor", budget_item["payor_id"])
        budget_item["payee_id"] = data.get("payee", budget_item["payee_id"])
        budget_item["transaction_date"] = data.get(
            "transaction_date", datetime.datetime.now(pytz.UTC).isoformat()
        )
        budget_item = utils.parse_json(json_data=budget_item, schema=BudgetItemSchema())
        with db.connect() as conn:
            result = conn.execute(
                sqlalchemy.update(Budget)
                .where(Budget.id == id)
                .values(
                    item=budget_item["item"],
                    dollars=budget_item["dollars"],
                    cents=budget_item["cents"],
                    flow=budget_item["flow"],
                    payor_id=budget_item["payor_id"],
                    payee_id=budget_item["payee_id"],
                    date_modified=budget_item["transaction_date"],
                )
            )
            conn.commit()
        return {
            "status": HTTPStatus.OK,
            "result": BudgetItemSchema().dump(result.last_updated_params()),
        }
    elif request.method == "DELETE":
        if budget_item["result"]:
            with db.connect() as conn:
                query = sqlalchemy.delete(Budget).where(Budget.id == id)
                conn.execute(query)
                conn.commit()
                return {"status": HTTPStatus.NO_CONTENT, "result": {}}
