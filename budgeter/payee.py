"""
payee.py contains the routes and methods for Flask to interact with the budget database
table.
"""


from http import HTTPStatus
from typing import Tuple

import sqlalchemy
from flask import Blueprint, request
from werkzeug.exceptions import abort

import budgeter.db as budgeter_db
import budgeter.utils as utils
from budgeter.db_model.payee import Payee
from budgeter.schemas.payee import PayeeSchema

bp = Blueprint("payee", __name__, url_prefix="/payees")

payee_table = Payee()


@bp.route("/")
def payee_view() -> Tuple[int, dict]:
    db = budgeter_db.get_db()
    with db.connect() as conn:
        payees = conn.execute(sqlalchemy.select(payee_table)).fetchall()
        if payees is None:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, "Could not access the payee table")
        return HTTPStatus.OK, {bp.name: payees}


@bp.route("/ids/", methods=("GET", "POST"))
def create() -> Tuple[int, dict]:
    if request.method == "POST":
        data = utils.parse_json(json_data=request.get_json(), schema=PayeeSchema())

        db = budgeter_db.get_db()
        with db.connect() as conn:
            # Keys better be there marshmallow, but can be adjusted to use .get() method
            if not data.get("id"):
                data["id"] = "UUID()"
            query = sqlalchemy.insert(payee_table).values(
                id=data["id"],
                name=data["name"],
                e_mail=data["e_mail"],
                phone=data["phone"],
            )
            result = conn.execute(query)
            conn.commit()
            return HTTPStatus.CREATED, {
                "message": "Created new payee entity.",
                "id": result.id,
            }
    elif request.method == "GET":
        return payee_view()


def get_payee_by_id(*, uuid: str) -> Tuple[int, dict]:
    """
    get_payee_by_id retrieves a single row from a database representing a payee entity.

    Parameters
    ----------
    uuid : str
        The unique identifier representing a payee entity.

    Returns
    -------
    Tuple[int, dict]
        The HTTP status code and query result for a single payee entity.
    """
    db = budgeter_db.get_db()
    with db.connect() as conn:
        payee = conn.execute(sqlalchemy.select(payee_table).where(payee_table.id == uuid))
        if payee is None:
            abort(HTTPStatus.NOT_FOUND, f"Payee id {uuid} does not exist.")
        return HTTPStatus.OK, payee


@bp.route("/ids/<string:id>", methods=("GET", "POST", "DELETE"))
def update_by_id(id: str):
    get_status_code, get_result = get_payee_by_id(uuid=id)
    if request.method == "GET":
        return get_status_code, get_result

    db = budgeter_db.get_db()
    if request.method == "POST":
        data = utils.parse_json(json_data=request.get_json(), schema=PayeeSchema())
        name = data["name"] if data.get("name") else get_result.name
        e_mail = data["e_mail"] if data.get("e_mail") else get_result.e_mail
        phone = data["phone"] if data.get("phone") else get_result.phone
        with db.connect() as conn:
            result = conn.execute(
                "UPDATE payee SET " " name = ?, e_mail = ?, phone = ? " " WHERE id = ?",
                (name, e_mail, phone, id),
            )
            conn.commit()
        return HTTPStatus.OK, result
    elif request.method == "DELETE":
        if get_result:
            with db.connect() as conn:
                query = sqlalchemy.delete(payee_table).where(payee_table.id == id)
                conn.execute(query)
                conn.commit()
                return HTTPStatus.NO_CONTENT, {}


# Purposefully choosing to not allow other methods on this route to prevent working
# with name collisions. That is, an entity may have the same name, but different UUIDs
# due to differing points of contact.
@bp.route("/names/<string:name>")
def get_by_name(name: str):
    db = budgeter_db.get_db()
    with db.connect() as conn:
        payee = conn.execute(sqlalchemy.select(payee_table).where(payee_table.name == name))
        if payee is None:
            abort(HTTPStatus.NOT_FOUND, f"Payee name, '{name}' does not exist.")
        return HTTPStatus.OK, payee
