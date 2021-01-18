#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__
"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import ohsome
import pandas as pd
import pytest


def test_timeout_error():
    """
    Test whether an OhsomeException is raised, if the ohsome API contains a JSONDecodeError
    :return:
    """
    bboxes = "13.7,50.9,13.75,50.95"
    time = "2019-12-10"
    fltr = "leisure=park and type:way"
    timeout = 5

    client = ohsome.OhsomeClient()
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.geometry.post(
            bboxes=bboxes, time=time, filter=fltr, timeout=timeout
        )
    assert (
        e_info.value.message
        == "The given query is too large in respect to the given timeout. Please use a smaller region and/or coarser time period."
    )


def test_elements_count():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    # Setup
    bboxes = [8.67066, 49.41423, 8.68177, 49.4204]
    time = "2010-01-01"
    fltr = "building=* and type:way"
    expected = 53

    # Run query
    client = ohsome.OhsomeClient()
    response = client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)
    result = response.as_dataframe()
    del client

    # Check result
    assert expected == result.value[0]


def test_elements_count_group_by_key():
    """
    Tests counting elements within a bounding box and grouping them by keys
    :return:
    """

    # GIVEN
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01/2011-01-01/P1Y"
    groupByKeys = ["building"]
    fltr = "building=* and type:way"

    timestamps = [
        "2010-01-01T00:00:00Z",
        "2011-01-01T00:00:00Z",
        "2010-01-01T00:00:00Z",
        "2011-01-01T00:00:00Z",
    ]
    counts = [483.0, 629.0, 53.0, 256.0]
    keys = ["remainder", "remainder", "building", "building"]
    expected = pd.DataFrame({"key": keys, "timestamp": timestamps, "value": counts})
    expected.set_index(["key", "timestamp"], inplace=True)

    # WHEN
    client = ohsome.OhsomeClient()
    client.elements.count.groupBy.key.post(
        bboxes=bboxes, groupByKeys=groupByKeys, time=time, filter=fltr
    )
    # results = response.as_dataframe()

    # THEN
    # assert expected["value"].equals(results["value"])
