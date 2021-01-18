#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tests for utility functions """

import ohsome
import geopandas as gpd
import pandas as pd
import pytest
import datetime as dt


def test_check_time_parameter_list():
    """
    Checks whether time provided as list of strings is converted correctly
    :return:
    """
    # Setup
    time = pd.date_range("2018-01-01", periods=3, freq="D")
    time = tuple(time.strftime("%Y-%m-%dT%H:%M:%S").tolist())
    bcircles = gpd.read_file("./data/points.geojson")
    fltr = "amenity=restaurant and type:way"

    # Run ohsome query
    client = ohsome.OhsomeClient()
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)


def test_check_time_parameter_datetimeindex():
    """
    Checks whether time provided as pandas.DateTimeIndex is converted correctly
    :return:
    """
    # Setup
    time = pd.date_range("2018-01-01", periods=3, freq="D")
    bcircles = gpd.read_file("./data/points.geojson")
    fltr = "amenity=restaurant and type:way"

    # Run ohsome query
    client = ohsome.OhsomeClient()
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)


def test_check_time_parameter_series():
    """
    Checks whether time provided as pandas.DateTimeIndex is converted correctly
    :return:
    """
    # Setup
    time = pd.Series(["2018-01-01", "2018-01-02"])
    bcircles = gpd.read_file("./data/points.geojson")
    fltr = "amenity=restaurant and type:way"

    # Run ohsome query
    client = ohsome.OhsomeClient()
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)


def test_check_time_parameter_datetime():
    """
    Checks whether time provided as pandas.Series is converted correctly
    :return:
    """
    # Setup
    time = [
        dt.datetime.strptime("2018-01-01", "%Y-%m-%d"),
        dt.datetime.strptime("2018-01-02", "%Y-%m-%d"),
    ]
    bcircles = gpd.read_file("./data/points.geojson")
    fltr = "amenity=restaurant and type:way"

    # Run ohsome query
    client = ohsome.OhsomeClient()
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)


def test_format_bcircles_dataframe():
    """
    Test whether a DataFrame object given as 'bcircles' is formatted correctly.
    :return:
    """
    bcircles = pd.DataFrame(
        {
            "id": [1, 2],
            "lon": [8.695, 8.696],
            "lat": [49.41, 49.41],
            "radius": [500, 500],
        }
    )
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:way"

    # Run ohsome query
    client = ohsome.OhsomeClient()
    client.elements.count.groupBy.boundary.post(
        bcircles=bcircles, time=time, filter=fltr
    )


def test_format_bcircles_list():
    """
    Test whether a DataFrame object given as 'bcircles' is formatted correctly.
    :return:
    """
    bcircles = [[1, 8.695, 49.41, 200], [2, 8.696, 49.41, 200]]
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:node"

    # Run ohsome query
    client = ohsome.OhsomeClient()
    client.elements.count.groupBy.boundary.post(
        bcircles=bcircles, time=time, filter=fltr
    )


def test_format_bcircles_geodataframe():
    """
    Test whether a GeoDataFrame object given as 'bcircles' is formatted correctly.
    :return:
    """
    bcircles = gpd.read_file("./data/points.geojson")
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:way"

    # Run ohsome query
    client = ohsome.OhsomeClient()
    client.elements.count.groupBy.boundary.post(
        bcircles=bcircles, time=time, filter=fltr
    )


def test_format_bcircles_geodataframe_geometry_error():
    """
    Test whether a GeoDataFrame object given as 'bcircles' is formatted correctly.
    :return:
    """
    bcircles = gpd.read_file("./data/polygons.geojson")
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:way"

    # Run ohsome query
    client = ohsome.OhsomeClient()
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.count.groupBy.boundary.post(
            bcircles=bcircles, time=time, filter=fltr
        )
    assert (
        e_info.value.message
        == "The geometry of the 'bcircles' GeoDataFrame may only include 'Point' geometry types."
    )
    del client


def test_format_bpolys():
    """
    Test whether a GeoDataFrame obejct is formatted correctly for ohsome api.
    :return:
    """
    bpolys = gpd.read_file("./data/polygons.geojson")
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:node"

    client = ohsome.OhsomeClient()
    client.elements.count.post(bpolys=bpolys, time=time, filter=fltr)


def test_format_bboxes_dataframe():
    """
    Tests whether input parameter given as a pandas.DataFrame is formatted correctly to a string
    :return:
    """
    data = gpd.read_file("./data/polygons.geojson")
    bboxes = data.bounds
    time = "2010-01-01"
    fltr = "amenity=restaurant and type:node"

    client = ohsome.OhsomeClient()
    client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)


def test_format_bboxes_dataframe_missing_columns():
    """
    Tests whether input parameter given as a pandas.DataFrame is formatted correctly to a string
    :return:
    """
    data = gpd.read_file("./data/polygons.geojson")
    bboxes = data.bounds
    bboxes.drop(columns="minx", inplace=True)
    time = "2010-01-01"
    fltr = "amenity=restaurant and type:node"

    client = ohsome.OhsomeClient()
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)
    assert (
        e_info.value.message
        == "Column 'minx' is missing in the dataframe provided as 'bboxes'."
    )


def test_format_bboxes_geodataframe():
    """
    Tests whether input parameter given as a pandas.DataFrame is formatted correctly to a string
    :return:
    """
    data = gpd.read_file("./data/polygons.geojson")
    time = "2010-01-01/2011-01-01/P1Y"
    fltr = "amenity=restaurant and type:node"

    client = ohsome.OhsomeClient()
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.count.post(bboxes=data, time=time, filter=fltr)
    assert (
        e_info.value.message
        == "Use the 'bpolys' parameter to specify the boundaries using a geopandas.GeoDataFrame."
    )


def test_format_bboxes_list():
    """
    Tests whether parameter bboxes given as a list is formatted correctly
    :return:
    """
    bboxes = [
        [8.67066, 49.41423, 8.68177, 49.4204],
        [8.67066, 49.41423, 8.68177, 49.4204],
    ]
    time = "2010-01-01"
    fltr = "amenity=restaurant and type:node"

    client = ohsome.OhsomeClient()
    client.elements.count.groupBy.boundary.post(bboxes=bboxes, time=time, filter=fltr)

    bboxes = [8.67066, 49.41423, 8.68177, 49.4204]
    time = "2010-01-01/2011-01-01/P1Y"
    fltr = "amenity=restaurant and type:node"

    client = ohsome.OhsomeClient()
    client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)


def test_find_groupby_names_one_group():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    # GIVEN
    url = "https://api.ohsome.org/v0.9/elements/count/groupBy/boundary"
    # Expected
    expected = ["boundary"]
    # WHEN
    result = ohsome.find_groupby_names(url)

    # THEN
    assert expected == result


def test_find_groupby_names_two_groups():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    # GIVEN
    url = "https://api.ohsome.org/v0.9/elements/count/groupBy/boundary/groupBy/tag"
    # Expected
    expected = ["boundary", "tag"]
    # WHEN
    result = ohsome.find_groupby_names(url)

    # THEN
    assert expected == result
