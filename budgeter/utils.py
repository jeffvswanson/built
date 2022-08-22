"""
Utility functions to work with the Built budget API.
"""

from typing import Optional

from marshmallow import Schema, ValidationError
from werkzeug.exceptions import abort, BadRequest, UnprocessableEntity


def parse_json(*, json_data: Optional[dict], schema: Schema) -> dict:
    """
    parse_json loads the provided JSON data into the given schema.

    Parameters
    ----------
    json_data : Optional[dict]
        It's JSON data.
    schema : Schema
        A schema to apply against the provided JSON data.

    Returns
    -------
    dict
        The data in the appropriate schema format.
    """
    if not json_data:
        abort(BadRequest.code, "No input data provided.")
        
    try:
        data = schema.load(json_data)
    except ValidationError as exc:
        abort(UnprocessableEntity.code, exc.messages)

    return data
