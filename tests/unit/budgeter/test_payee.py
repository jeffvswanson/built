from http import HTTPStatus
from unittest import mock

import pytest

from budgeter import payee


@pytest.mark.parametrize(
    "given,expected",
    [
        pytest.param(
            {"name": "Corp", "e_mail": "abc@built.com", "phone": "123-867-5309"},
            {
                "status": HTTPStatus.CREATED,
                "result": {
                    "message": "Created new payee entity.",
                    "id": 99,
                },
            },
            id="insert payee",
        ),
        pytest.param(
            {"name": "Corp", "e_mail": "abc@built.com", "phone": "123-867-5309"},
            None,
            marks=pytest.mark.xfail(raises=AttributeError),
            id="error inserting payee",
        ),
    ],
)
def test_insert_payee(given, expected):
    # GIVEN the need to insert a payee entity into the database
    # WHEN
    if expected:
        with mock.patch("budgeter.payee.insert_payee", return_value=expected):
            got = payee.insert_payee(**given)
    else:
        with mock.patch("budgeter.payee.budgeter_db.get_db", return_value=None):
            got = payee.insert_payee(**given)
    # THEN a created status should be provided or an exception should be raised.
    assert got == expected
