from http import HTTPStatus
from unittest import mock

import pytest
from werkzeug.exceptions import NotFound

from budgeter import budget


@pytest.mark.skip
def test_budget_view():
    # GIVEN the need to retrieve all the items from the budget table
    # WHEN
    # THEN we should return all of the items
    ...


@pytest.mark.parametrize(
    "given,expected",
    [
        pytest.param(
            1,
            {"status": HTTPStatus.OK, "result": {"attribute": "valid"}},
            id="item exists in database",
        ),
        pytest.param(
            2,
            None,
            marks=pytest.mark.xfail(reason=NotFound),
            id="item does not exist in database",
        ),
    ],
)
def test_get_budget_item(given, expected):
    # GIVEN the need to retrieve a single item from the budget table
    if expected is not None:
        budget.get_budget_item = mock.Mock(return_value=expected)
    # WHEN
    got = budget.get_budget_item(id=given)
    # THEN we should either find the item or return an HTTP status of not found.
    assert got == expected
