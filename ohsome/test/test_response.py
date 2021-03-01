#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for ohsome API response"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import ohsome
import geopandas as gpd
import pandas as pd


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
    response = client.elements.count.post(
        timeout=500, bboxes=bboxes, time=time, filter=fltr
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert list(result.index.names) == ["timestamp"]


def test_elements_density():
    """
    Tests whether the result of elements.count.density is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10"
    fltr = "amenity=cafe and type:node"

    client = ohsome.OhsomeClient()
    response = client.elements.count.density.post(
        timeout=500, bboxes=bboxes, time=time, filter=fltr
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert list(result.index.names) == ["timestamp"]


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
    response = client.elements.count.groupByKey.post(
        timeout=500, bboxes=bboxes, time=time, filter=fltr, groupByKeys=groupByKeys
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 6
    assert list(result.index.names) == ["key", "timestamp"]


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
    response = client.elements.count.groupByTag.post(
        timeout=500, bboxes=bboxes, time=time, filter=fltr, groupByKey=groupByKey
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 58
    assert list(result.index.names) == ["tag", "timestamp"]


def test_multi_index_false():
    """
    Tests whether the response is formatted correctly as a pandas.DataFrame without a multiindex
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10,2019-12-11"
    fltr = "type:node"
    groupByKey = "amenity"

    client = ohsome.OhsomeClient()
    response = client.elements.count.groupByTag.post(
        timeout=500, bboxes=bboxes, time=time, filter=fltr, groupByKey=groupByKey
    )
    result = response.as_dataframe(multi_index=False)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 58
    assert isinstance(result.index, pd.RangeIndex)


def test_elements_count_groupby_type():
    """
    Tests whether the result of elements.count.groupBy.type is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10,2019-12-11"
    fltr = "amenity=* and (type:way or type:node)"

    client = ohsome.OhsomeClient()
    response = client.elements.count.groupByType.post(
        timeout=600, bboxes=bboxes, time=time, filter=fltr
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 6
    assert list(result.index.names) == ["type", "timestamp"]


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
    response = client.elements.count.groupByBoundary.post(
        timeout=500, bboxes=bboxes, time=time, filter=fltr
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.index.names) == ["boundary", "timestamp"]


def test_elements_count_groupby_boundary_groupby_tag():
    """
    Tests whether the result of elements.count.groupBy.boundary.groupBy.tag is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106|8.6887,49.41325,8.69462,49.4166"
    time = "2019-12-10"
    fltr = "amenity=cafe and type:node"
    groupByKey = "amenity"

    client = ohsome.OhsomeClient()
    response = client.elements.count.groupByBoundary.groupByTag.post(
        timeout=500, bboxes=bboxes, time=time, filter=fltr, groupByKey=groupByKey
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.index.names) == ["boundary", "tag", "timestamp"]


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
        timeout=500, bboxes=bboxes, time=time, filter=fltr, filter2=fltr2
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert list(result.index.names) == ["timestamp"]


def test_elements_count_ratio_groupby_boundary():
    """
    Tests whether the result of elements.count.ratio.groupBy.boundary is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "A:8.6933,49.40893,8.69797,49.41106|B:8.6887,49.41325,8.69462,49.4166"
    time = "2019-12-10, 2020-12-10"
    fltr = "amenity=* and type:node"
    fltr2 = "amenity=cafe and type:node"

    client = ohsome.OhsomeClient()
    response = client.elements.count.ratio.groupByBoundary.post(
        timeout=500, bboxes=bboxes, time=time, filter=fltr, filter2=fltr2
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 4
    assert list(result.index.names) == ["boundary", "timestamp"]


def test_elements_geometry():
    """
    Tests whether the result of elements.geometry is converted to a geopandas.GeoDataFrame
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2016-01-01"
    flter = "name=Krautturm and type:way"

    client = ohsome.OhsomeClient()
    response = client.elements.geometry.post(
        timeout=500, bboxes=bboxes, time=time, filter=flter
    )
    result = response.as_geodataframe()
    del client

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 1


def test_elementsFullHistory_geometry():
    """
    Tests whether the result of elementsFullHistory.centroid is converted to a geopandas.GeoDataFrame
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2008-01-01,2016-01-01"
    flter = "name=Krautturm and type:way"

    client = ohsome.OhsomeClient()
    response = client.elementsFullHistory.centroid.post(
        timeout=500, bboxes=bboxes, time=time, filter=flter
    )
    result = response.as_geodataframe()

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 5


def test_users_timestamp():
    """
    Tests whether the result of users.count is converted to a pandas.DataFrame
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2008-01-01/2016-01-01/P1Y"
    flter = "name=Krautturm and type:way"

    client = ohsome.OhsomeClient()
    response = client.users.count.post(
        timeout=500, bboxes=bboxes, time=time, filter=flter
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 8


def test_contributions_centroid():
    """
    Test whether the result of conributions.centroid is converted to a geopandas.GeoDataFrame
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2008-01-01,2016-01-01"
    filter = "name=Krautturm and type:way"

    client = ohsome.OhsomeClient()
    response = client.contributions.centroid.post(
        timeout=500, bboxes=bboxes, time=time, filter=filter
    )
    result = response.as_geodataframe()

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 5


def test_contributions_latest():
    """
    Test whether the result of conributions.latest.bbox is converted to a geopandas.GeoDataFrame
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2008-01-01,2016-01-01"
    filter = "name=Krautturm and type:way"

    client = ohsome.OhsomeClient()
    response = client.contributions.latest.bbox.post(
        timeout=500, bboxes=bboxes, time=time, filter=filter
    )
    result = response.as_geodataframe()

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 1
