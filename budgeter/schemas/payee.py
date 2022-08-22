"""
Defines the request schema for a payee/payor entity.
"""

from marshmallow import Schema, fields, validate


class PayeeSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True)
    e_mail = fields.Email(
        required=True, validate=validate.Email(error="Valid e-mail address required.")
    )
    # Some better validation could be done on a phone number, say a library, or
    # custom parser
    phone = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=15, error="Please provide a phone number"),
    )
