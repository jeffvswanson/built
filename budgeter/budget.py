"""
budget.py contains the routes and methods for Flask to interact with the budget database
table.
"""

from http import HTTPStatus

import sqlalchemy
from flask import Blueprint, request
from werkzeug.exceptions import abort

import budgeter.db as budgeter_db
import budgeter.utils as utils
from budgeter.db_model.budget import Budget
from budgeter.db_model.payee import Payee
from budgeter.schemas.budget_item import BudgetItemSchema

bp = Blueprint("budget", __name__)

budget_table = Budget()
payee_table = Payee()

@bp.route("/")
def index():
    db = budgeter_db.get_db()
    budget = db.execute(
        sqlalchemy.text(
            "SELECT"
            " item, dollars, cents, flow, p.payor_name, p.payee_name, transaction_date"
            " FROM budget b"
            " JOIN p.payor_name ON b.payor_id = p.id"
            " AND p.payee_name ON b.payee_id = p.id"
        )
    ).fetchall()
    return {bp.name: budget}


@bp.route("/items/", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        data = utils.parse_json(json_data=request.get_json(), schema=BudgetItemSchema())

        db = budgeter_db.get_db()
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


def get_budget_item(id: int):
    db = budgeter_db.get_db()
    item = (
        db.execute(
            "SELECT"
            "item, dollars, cents, flow, p.payor_name, p.payee_name, transaction_date"
            " FROM budget b"
            " JOIN p.payor_name ON b.payor_id = p.id"
            " AND p.payee_name ON b.payee_id = p.id"
            " WHERE b.id = ?",
            (id,),
        )
        .fetchone()
    )
    if item is None:
        abort(HTTPStatus.NOT_FOUND, f"Budget item id {id} does not exist.")
    return HTTPStatus.OK, item


@bp.route("/items/<int:id>", methods=("GET", "POST", "PATCH" "DELETE"))
def update(id: int):
    item = get_budget_item(id)
    if request.method == "POST":
        data = utils.parse_json(json_data=request.get_json(), schema=BudgetItemSchema())

        db = budgeter_db.get_db()
        result = db.execute(
            "UPDATE budget SET "
            " item = ?, dollars = ?, cents = ?, flow = ?, payor_id = ?, "
            " payee_id = ?, modified_date = ? "
            " WHERE id = ?",
            (item, data["dollars"], data["cents"], data["flow"], data["payor_id"], data["payee_id"], data["transaction_date"], id),
        )
        db.commit()
        return HTTPStatus.OK, result


# @bp.route("/<int:id>/", methods=("POST",))
# def delete(id: int):
#     get_budget_item(id)
#     db = budgeter_db.get_db()
#     db.execute("DELETE FROM budget WHERE id = ?", (id,))
#     db.commit()
#     return redirect(url_for("blog.index"))
