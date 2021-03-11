#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test OhsomeExceptions"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import pytest
import ohsome


def test_elements_count_exception(custom_client):
    """
    Tests whether a AssertionError is raised if the result cannot be converted to a geodataframe object
    :return:
    """
    # GIVEN
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01/2011-01-01/P1Y"
    fltr = "building=* and type:way"

    client = custom_client
    response = client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)

    with pytest.raises(AssertionError):
        response.as_geodataframe()


def test_timeout_error(custom_client):
    """
    Test whether an OhsomeException is raised, if the ohsome API contains a JSONDecodeError
    :return:
    """
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01/2011-01-01/P1Y"
    fltr = "building=* and type:way"
    timeout = 0

    client = custom_client
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.geometry.post(
            bboxes=bboxes, time=time, filter=fltr, timeout=timeout
        )
    assert (
        e_info.value.message
        == "The given query is too large in respect to the given timeout. Please use a smaller region and/or coarser time period."
    )


def test_catch_incomplete_response_error():
    """
    Tests whether a AssertionError is raised if the result cannot be converted to a geodataframe object
    :return:
    """
    # todo: find suitable test case
