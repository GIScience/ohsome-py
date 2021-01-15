#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tests for ohsome client """

import pandas as pd
import ohsome


def test_start_and_end_timestamp():
    """
    Get start timestamp
    :return:
    """
    # Run query
    print(ohsome.OhsomeClient().start_timestamp)
    print(ohsome.OhsomeClient().end_timestamp)


def test_api_version():
    """
    Get ohsome API version
    :return:
    """
    # Run query
    print(ohsome.OhsomeClient().api_version)


def test_elements_count():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    # Setup
    bboxes = [8.67066, 49.41423, 8.68177, 49.4204]
    time = "2010-01-01"
    filter = "building=*"
    expected = 53

    # Run query
    client = ohsome.OhsomeClient()
    response = client.elements.count.post(bboxes=bboxes, time=time, filter=filter)
    result = response.as_dataframe()
    del client

    # Check result
    assert expected == result.value[0]


def test_elements_geometry():
    """
    Tests whether the result of an elements/geometry query can be converted to a geodataframe
    :return:
    """
    # GIVEN
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01"
    filter = "landuse=grass and type:way"

    # WHEN
    client = ohsome.OhsomeClient()
    response = client.elements.geometry.post(bboxes=bboxes, time=time, filter=filter)
    result = response.as_geodataframe()
    del client

    # THEN
    assert len(result.geometry) == 9


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
