"""
Test for utils
"""

from datetime import datetime
from time import sleep

import pytest

from biredirect.utils import parse_date, print_prof_data, profile


@pytest.mark.parametrize("newdate", [
    datetime(2017, 10, 1),
    "01/10/2017"
])
def test_parse_date(newdate):
    expected = datetime(2017, 10, 1, 0, 0)
    parsed_date = parse_date(newdate)

    assert parsed_date == expected


def test_parse_date_fail():

    with pytest.raises(Exception):
        parse_date(7)


@profile
def sample_function():
    sleep(0.05)


def test_profile():
    sample_function()
    assert print_prof_data() == (
        "\nFunction sample_function executed in 0.05 seconds")
