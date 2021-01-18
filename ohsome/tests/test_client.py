#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tests for ohsome client """

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
