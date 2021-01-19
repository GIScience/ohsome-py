#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for ohsome API response """

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import ohsome
import pytest


def test_elements_count():
    """
    Tests whether the result of elements.count is formatted correctly as a pandas.DataFrame. If this works
    .area, .length and .permiter should work as well.
    :return:
    """

    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10"
    fltr = "amenity=cafe and type:node"

    client = ohsome.OhsomeClient()
    response = client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)
    data = response.as_dataframe()
    print(data)


def test_elements_density():
    """
    Tests whether the result of elements.count.density is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10"
    fltr = "amenity=cafe and type:node"

    client = ohsome.OhsomeClient()
    response = client.elements.count.density.post(bboxes=bboxes, time=time, filter=fltr)
    data = response.as_dataframe()
    print(data)


# todo: sort keys alphabetically?
def test_elements_count_groupby_key():
    """
    Tests whether the result of elements.count.groupBy.key is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10,2019-12-11"
    fltr = "type:node"
    groupByKeys = ["amenity", "shop"]

    client = ohsome.OhsomeClient()
    response = client.elements.count.groupBy.key.post(
        bboxes=bboxes, time=time, filter=fltr, groupByKeys=groupByKeys
    )
    data = response.as_dataframe()
    print(data)


def test_elements_count_groupby_tag():
    """
    Tests whether the result of elements.count.groupBy.tag is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10,2019-12-11"
    fltr = "type:node"
    groupByKey = "amenity"

    client = ohsome.OhsomeClient()
    response = client.elements.count.groupBy.tag.post(
        bboxes=bboxes, time=time, filter=fltr, groupByKey=groupByKey
    )
    data = response.as_dataframe()
    print(data)


def test_elements_count_groupby_type():
    """
    Tests whether the result of elements.count.groupBy.type is formatted correctly as a pandas.DataFrame
    :return:
    """

    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10,2019-12-11"
    fltr = "amenity=* and (type:way or type:node)"

    client = ohsome.OhsomeClient()
    response = client.elements.count.groupBy.type.post(
        bboxes=bboxes, time=time, filter=fltr
    )
    data = response.as_dataframe()
    print(data)


def test_elements_count_groupby_boundary():
    """
    Tests whether the result of elements.count.groupBy.boundary is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = {
        1: [8.6933, 49.40893, 8.69797, 49.41106],
        2: [8.6887, 49.41325, 8.69462, 49.4166],
    }
    time = "2019-12-10"
    fltr = "amenity=cafe and type:node"

    client = ohsome.OhsomeClient()
    response = client.elements.count.groupBy.boundary.post(
        bboxes=bboxes, time=time, filter=fltr
    )
    data = response.as_dataframe()
    print(data)


def test_elements_count_groupby_boundary_groupby_tag():
    """
    Tests whether the result of elements.count.groupBy.boundary is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106|8.6887,49.41325,8.69462,49.4166"
    time = "2019-12-10"
    fltr = "amenity=cafe and type:node"
    groupByKey = "amenity"

    client = ohsome.OhsomeClient()
    response = client.elements.count.groupBy.boundary.groupBy.tag.post(
        bboxes=bboxes, time=time, filter=fltr, groupByKey=groupByKey
    )
    data = response.as_dataframe()
    print(data)


def test_elements_count_ratio():
    """
    Tests whether the result of elements.count.ratio is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10"
    fltr = "amenity=* and type:node"
    fltr2 = "amenity=cafe and type:node"

    client = ohsome.OhsomeClient()
    response = client.elements.count.ratio.post(
        bboxes=bboxes, time=time, filter=fltr, filter2=fltr2
    )
    data = response.as_dataframe()
    print(data)


def test_elements_count_ratio_groupby_boundary():
    """
    Tests whether the result of elements.count.ratio is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "A:8.6933,49.40893,8.69797,49.41106|B:8.6887,49.41325,8.69462,49.4166"
    time = "2019-12-10, 2020-12-10"
    fltr = "amenity=* and type:node"
    fltr2 = "amenity=cafe and type:node"

    client = ohsome.OhsomeClient()
    response = client.elements.count.ratio.groupBy.boundary.post(
        bboxes=bboxes, time=time, filter=fltr, filter2=fltr2
    )
    data = response.as_dataframe()
    print(data)


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
