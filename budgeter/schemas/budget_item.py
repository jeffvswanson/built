"""
Defines the request schema for a budget item.
"""
import pytz
from marshmallow import Schema, fields, validate, pre_load


class BudgetItem(Schema):
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
        format="iso", default_timezone=pytz.UTC, required=True, allow_none=False
    )

    @pre_load
    def find_payee_ids(self, data, **kwargs):
        """
        find_payee_ids attempts to match the provided payor/payee names with an existing
        value in the payee database table. If the name(s) cannot be found, then the
        payor/payee names get added to the payee database table.
        """
        payor_id, payee_id = None, None
        payor = data.pop("payor")
        # if payor in payee table:
        #     get and assign payor ID
        # else:
        #     update payee table with payor name
        #     data["payor_id"] = payee.UUID
        payee = data.pop("payee")
        # if payee in payee table:
        #     get and assign payor ID
        # else:
        #     update payee table with payee name
        #     data["payee_id"] = payee.UUID
        return data
