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
            marks=pytest.mark.xfail(),
            id="error inserting payee",
        ),
    ],
)
def test_insert_payee(given, expected):
    # GIVEN the need to insert a payee entity into the database
    if expected:
        payee.insert_payee = mock.Mock(return_value=expected)
    # WHEN
    got = payee.insert_payee(given)
    # THEN a created status should be provided or an exception should be raised.
    assert got == expected
