"""
Defines the request schema for a budget item.
"""
import datetime
from http import HTTPStatus

import pytz
from marshmallow import Schema, fields, validate, pre_load

import budgeter.payee


class BudgetItemSchema(Schema):
    id = fields.Int(dump_only=True)
    item = fields.Str(required=True, allow_none=False)
    dollars = fields.Int(
        strict=True,
        default=0,
        validate=validate.Range(
            min=0, min_inclusive=True, error="Value must be an integer, 0 or greater."
        ),
    )
    cents = fields.Int(
        strict=True,
        default=0,
        validate=validate.Range(
            min=0,
            max=99,
            min_inclusive=True,
            max_inclusive=True,
            error="Value must be an integer between 0 and 99.",
        ),
    )
    flow = fields.Str(
        default="-",
        validate=validate.OneOf(
            choices=["+", "-"],
            labels=["Inflow", "Outflow"],
            error="Only inflow, '+', or outflow, '-', permitted.",
        ),
    )

    payor = fields.Str(required=True, allow_none=False)
    payee = fields.Str(required=True, allow_none=False)
    transaction_date = fields.AwareDateTime(
        format="iso",
        default_timezone=pytz.UTC,
        allow_none=False,
        dump_default=datetime.datetime.now(pytz.UTC).isoformat(),
    )

    @pre_load
    def find_payee_ids(self, data, **kwargs) -> dict:
        """
        find_payee_ids attempts to match the provided payor/payee names with an existing
        value in the payee database table. If the name(s) cannot be found, then the
        payor/payee names get added to the payee database table.

        Returns
        -------
        dict
            Dictionary containing the attribute names of BudgetItemSchema as keys with
            its attribute values as the values.
        """

        if payor := data.get("payor"):
            result = budgeter.payee.get_by_name(name=payor)
            if result["status"] == HTTPStatus.NOT_FOUND:
                resp = budgeter.payee.insert_payee(name=payor, e_mail=None, phone=None)
                if resp["status"] != HTTPStatus.CREATED:
                    return {
                        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                        "result": {"message": "Unable to create payor"},
                    }
                data["payor"] = resp["result"]["id"]

        if payee := data.get("payee"):
            result = budgeter.payee.get_by_name(name=payee)
            if result["status"] == HTTPStatus.NOT_FOUND:
                resp = budgeter.payee.insert_payee(name=payee, e_mail=None, phone=None)
                if resp["status"] != HTTPStatus.CREATED:
                    return {
                        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                        "result": {"message": "Unable to create payee"},
                    }
                data["payee"] = resp["result"]["id"]
        return data
