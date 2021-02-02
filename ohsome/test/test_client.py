#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tests for ohsome client """

import ohsome
import geopandas as gpd
import pandas as pd
import pytest
import datetime as dt


def test_userdefined_url():
    """
    Test whether request can be sent to alternative url
    :return:
    """
    base_api_url = "https://docs.ohsome.org/ohsome-api/v0.9"
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:node"
    bcircles = [[8.695, 49.41, 200], [8.696, 49.41, 200]]

    client = ohsome.OhsomeClient(base_api_url=base_api_url)
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)
    assert client.base_api_url == base_api_url


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
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:node"
    client = ohsome.OhsomeClient()

    bcircles = [[8.695, 49.41, 200], [8.696, 49.41, 200]]
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)

    bcircles = {1: [8.695, 49.41, 200], 2: [8.696, 49.41, 200]}
    client.elements.count.groupBy.boundary.post(
        bcircles=bcircles, time=time, filter=fltr
    )

    bcircles = ["1:8.695, 49.41, 200", "2:8.696, 49.41, 200"]
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)

    bcircles = "1:8.695, 49.41, 200"
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)


def test_bcircles_groupby():
    """
    Test whether bcircles given as dictionary is correctly formatted
    :return:
    """
    radius = 100
    cities = {
        "T": [139.7594549, 35.6828387, radius],
        "V": [-123.1139529, 49.2608724, radius],
        "Berlin": [13.3888599, 52.5170365, radius],
    }
    cities = "1:139.7594549,35.6828387,100|2:13.3888599,52.5170365,100"
    time = pd.date_range("2010-01-01", periods=1, freq="Y")
    fltr = "leisure=park and type:way"

    client = ohsome.OhsomeClient()
    response = client.elements.count.groupBy.boundary.post(
        bcircles=cities, time=time, filter=fltr
    )
    data = response.as_dataframe()
    print(data)


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
    time = "2010-01-01"
    fltr = "amenity=restaurant and type:node"

    client = ohsome.OhsomeClient()

    bboxes = [
        [8.67066, 49.41423, 8.68177, 49.4204],
        [8.67066, 49.41423, 8.68177, 49.4204],
    ]
    client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)

    bboxes = {
        "1": [8.67066, 49.41423, 8.68177, 49.4204],
        "2": [8.67066, 49.41423, 8.68177, 49.4204],
    }
    client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)

    bboxes = [8.67066, 49.41423, 8.68177, 49.4204]
    client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)

    bboxes = [
        "8.67066, 49.41423, 8.68177, 49.4204",
        "8.67066, 49.41423, 8.68177, 49.4204",
    ]
    client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)

    bboxes = "8.67066, 49.41423, 8.68177, 49.4204"
    client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)
