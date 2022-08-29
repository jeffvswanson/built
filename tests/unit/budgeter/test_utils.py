import pytest
from marshmallow import Schema, fields
from werkzeug.exceptions import BadRequest, UnprocessableEntity

import budgeter.utils as budgeter_utils


@pytest.fixture(scope="module")
def schema():
    class TestSchema(Schema):
        item = fields.Str()
        num = fields.Int()

    return TestSchema


@pytest.mark.parametrize(
    "data",
    [
        pytest.param({"item": "thing", "num": 13}, id="valid JSON"),
        pytest.param(
            None, marks=pytest.mark.xfail(raises=BadRequest), id="no JSON provided"
        ),
        pytest.param(
            "Not valid JSON",
            marks=pytest.mark.xfail(raises=UnprocessableEntity),
            id="JSON cannot be loaded",
        ),
    ],
)
def test_parse_json(data, schema):
    # GIVEN potential JSON data
    # WHEN
    got = budgeter_utils.parse_json(json_data=data, schema=schema())
    # THEN the appropriate object or error message should be raised.
    assert got == data
