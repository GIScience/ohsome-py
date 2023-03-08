#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for ohsome API response"""
import warnings
import pytest

import geopandas as gpd
import pandas as pd


@pytest.mark.vcr
def test_elements_count(base_client):
    """
    Tests whether the result of elements.count is formatted correctly as a pandas.DataFrame. If this works
    .area, .length and .permiter should work as well.
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10"
    fltr = "amenity=cafe and type:node"

    client = base_client
    response = client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert list(result.index.names) == ["timestamp"]


@pytest.mark.vcr
def test_elements_density(base_client):
    """
    Tests whether the result of elements.count.density is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10"
    fltr = "amenity=cafe and type:node"

    client = base_client
    response = client.elements.count.density.post(bboxes=bboxes, time=time, filter=fltr)
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert list(result.index.names) == ["timestamp"]


@pytest.mark.vcr
def test_elements_count_groupby_key(base_client):
    """
    Tests whether the result of elements.count.groupBy.key is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10,2019-12-11"
    fltr = "type:node"
    groupByKeys = ["amenity", "shop"]

    client = base_client
    response = client.elements.count.groupByKey.post(
        bboxes=bboxes, time=time, filter=fltr, groupByKeys=groupByKeys
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 6
    assert list(result.index.names) == ["key", "timestamp"]


@pytest.mark.vcr
def test_not_implemented_query(base_client):
    """
    Tests whether a query which is not implemented in ohsome-py still works
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10,2019-12-11"
    fltr = "type:node"
    groupByKeys = ["amenity", "shop"]

    client = base_client
    response = client.elements.count.groupBy.key.post(
        bboxes=bboxes, time=time, filter=fltr, groupByKeys=groupByKeys
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 6
    assert list(result.index.names) == ["key", "timestamp"]


@pytest.mark.vcr
def test_elements_count_groupby_tag(base_client):
    """
    Tests whether the result of elements.count.groupBy.tag is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10,2019-12-11"
    fltr = "type:node"
    groupByKey = "amenity"

    client = base_client
    response = client.elements.count.groupByTag.post(
        bboxes=bboxes, time=time, filter=fltr, groupByKey=groupByKey
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 58
    assert list(result.index.names) == ["tag", "timestamp"]


@pytest.mark.vcr
def test_multi_index_false(base_client):
    """
    Tests whether the response is formatted correctly as a pandas.DataFrame without a multiindex
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10,2019-12-11"
    fltr = "type:node"
    groupByKey = "amenity"

    client = base_client
    response = client.elements.count.groupByTag.post(
        bboxes=bboxes, time=time, filter=fltr, groupByKey=groupByKey
    )
    result = response.as_dataframe(multi_index=False)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 58
    assert isinstance(result.index, pd.RangeIndex)


@pytest.mark.vcr
def test_elements_count_groupby_type(base_client):
    """
    Tests whether the result of elements.count.groupBy.type is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10,2019-12-11"
    fltr = "amenity=* and (type:way or type:node)"

    client = base_client
    response = client.elements.count.groupByType.post(
        bboxes=bboxes, time=time, filter=fltr
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 6
    assert list(result.index.names) == ["type", "timestamp"]


@pytest.mark.vcr
def test_elements_count_groupby_boundary(base_client):
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

    client = base_client
    response = client.elements.count.groupByBoundary.post(
        bboxes=bboxes, time=time, filter=fltr
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.index.names) == ["boundary", "timestamp"]


@pytest.mark.vcr
def test_elements_count_groupby_boundary_groupby_tag(base_client):
    """
    Tests whether the result of elements.count.groupBy.boundary.groupBy.tag is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106|8.6887,49.41325,8.69462,49.4166"
    time = "2019-12-10"
    fltr = "amenity=cafe and type:node"
    groupByKey = "amenity"

    client = base_client
    response = client.elements.count.groupByBoundary.groupByTag.post(
        bboxes=bboxes, time=time, filter=fltr, groupByKey=groupByKey
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.index.names) == ["boundary", "tag", "timestamp"]


@pytest.mark.vcr
def test_elements_count_ratio(base_client):
    """
    Tests whether the result of elements.count.ratio is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "8.6933,49.40893,8.69797,49.41106"
    time = "2019-12-10"
    fltr = "amenity=* and type:node"
    fltr2 = "amenity=cafe and type:node"

    client = base_client
    response = client.elements.count.ratio.post(
        bboxes=bboxes, time=time, filter=fltr, filter2=fltr2
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert list(result.index.names) == ["timestamp"]


@pytest.mark.vcr
def test_elements_count_ratio_groupby_boundary(base_client):
    """
    Tests whether the result of elements.count.ratio.groupBy.boundary is formatted correctly as a pandas.DataFrame
    :return:
    """
    bboxes = "A:8.6933,49.40893,8.69797,49.41106|B:8.6887,49.41325,8.69462,49.4166"
    time = "2019-12-10, 2020-07-23"
    fltr = "amenity=hotel and type:node"
    fltr2 = "amenity=cafe and type:node"

    client = base_client
    response = client.elements.count.ratio.groupByBoundary.post(
        bboxes=bboxes, time=time, filter=fltr, filter2=fltr2
    )
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 4
    assert list(result.index.names) == ["boundary", "timestamp"]


@pytest.mark.vcr
def test_elements_geometry(base_client):
    """
    Tests whether the result of elements.geometry is converted to a geopandas.GeoDataFrame
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2016-01-01"
    flter = "name=Krautturm and type:way"

    client = base_client
    response = client.elements.geometry.post(bboxes=bboxes, time=time, filter=flter)
    result = response.as_dataframe()
    del client

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 1


@pytest.mark.vcr
def test_elementsFullHistory_geometry(base_client):
    """
    Tests whether the result of elementsFullHistory.centroid is converted to a geopandas.GeoDataFrame
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2015-01-01,2016-01-01"
    flter = "name=Krautturm and type:way"

    client = base_client
    response = client.elementsFullHistory.centroid.post(
        bboxes=bboxes, time=time, filter=flter
    )
    result = response.as_dataframe()

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 2


@pytest.mark.vcr
def test_users_timestamp(base_client):
    """
    Tests whether the result of users.count is converted to a pandas.DataFrame
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2015-01-01/2016-01-01/P1Y"
    flter = "name=Krautturm and type:way"

    client = base_client
    response = client.users.count.post(bboxes=bboxes, time=time, filter=flter)
    result = response.as_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1


@pytest.mark.vcr
def test_contributions_centroid(base_client):
    """
    Test whether the result of conributions.centroid is converted to a geopandas.GeoDataFrame
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2015-01-01,2016-01-01"
    filter = "name=Krautturm and type:way"

    client = base_client
    response = client.contributions.centroid.post(
        bboxes=bboxes, time=time, filter=filter
    )
    result = response.as_dataframe()

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 1


@pytest.mark.vcr
def test_contributions_latest(base_client):
    """
    Test whether the result of conributions.latest.bbox is converted to a geopandas.GeoDataFrame
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2015-01-01,2016-01-01"
    filter = "name=Krautturm and type:way"

    client = base_client
    response = client.contributions.latest.bbox.post(
        bboxes=bboxes, time=time, filter=filter
    )
    result = response.as_dataframe()

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 1


@pytest.mark.vcr
def test_empty_geodataframe(base_client):
    """
    Tests whether an empty GeoDataFrame is created without a warning if no features are returned from ohsome
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2015-01-01,2016-01-01"
    filter = "name=Krautturm1 and type:way"

    client = base_client
    response = client.elements.bbox.post(bboxes=bboxes, time=time, filter=filter)
    with warnings.catch_warnings():
        warnings.simplefilter(action="error")
        result = response.as_dataframe()

    assert isinstance(result, gpd.GeoDataFrame)
    assert result.empty
