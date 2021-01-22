#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test OhsomeExceptions
"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import pytest
import ohsome


def test_elements_count_exception():
    """
    Tests whether a AssertionError is raised if the result cannot be converted to a geodataframe object
    :return:
    """
    # GIVEN
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01/2011-01-01/P1Y"
    fltr = "building=* and type:way"

    client = ohsome.OhsomeClient()
    response = client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)

    with pytest.raises(AssertionError):
        response.as_geodataframe()


def test_handle_multiple_responses_throw_timeouterror():
    """
    Tests whether a OhsomeException is thrown if time out occurs
    :return:
    """
    # GIVEN
    bboxes = [8.67066, 49.41423, 8.68177, 49.4204]
    time = "2010-01-01/2011-01-01/P1Y"
    filter = "building=*"

    # WHEN
    client = ohsome.OhsomeClient()
    with pytest.raises(ohsome.OhsomeException):
        client.elements.count.post(bboxes=bboxes, time=time, filter=filter, timeout=1)
