#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tests for utility functions """

import ohsome
import geopandas as gpd
import pandas as pd


def test_check_time_parameter():
    """
    Checks whether time provided as pandas.Series is converted correctly
    :return:
    """
    # Setup
    time = pd.date_range("2018-01-01", periods=3, freq="D")
    time.strftime("%Y-%m-%dT%H:%M:%S").tolist()
    bcircles = pd.DataFrame(
        {
            "id": [1, 2],
            "lon": [8.695, 8.696],
            "lat": [49.41, 49.41],
            "radius": [500, 500],
        }
    )
    fltr = "amenity=restaurant and type:way"

    # Run ohsome query
    client = ohsome.OhsomeClient()
    response = client.elements.count.post(
        bcircles=bcircles, time=time, filter=fltr
    )
    response.as_dataframe()
    del client


def test_format_bcircles():
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
    response = client.elements.count.groupBy.boundary.post(
        bcircles=bcircles, time=time, filter=fltr
    )
    result = response.as_dataframe()
    del client

    assert result["value"][0] == 1.0


def test_format_bpolys():
    """
    Test whether a GeoDataFrame obejct is formatted correctly for ohsome api.
    :return:
    """
    bpolys_geojson = [
        {
            "type": "Feature",
            "properties": {"id": 0},
            "geometry": {
                "coordinates": [
                    [
                        [
                            [13, 51],
                            [13, 51.1],
                            [13.1, 51.1],
                            [13.1, 51],
                            [13, 51],
                        ]
                    ],
                    [
                        [
                            [14, 51],
                            [14, 51.1],
                            [14.1, 51.1],
                            [14.1, 51],
                            [14, 51],
                        ]
                    ],
                ],
                "type": "MultiPolygon",
            },
        }
    ]
    bpolys = gpd.GeoDataFrame().from_features(bpolys_geojson)
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:node"
    expected = 18

    client = ohsome.OhsomeClient()
    response = client.elements.count.post(
        bpolys=bpolys, time=time, filter=fltr
    )
    result = response.as_dataframe()
    del client

    assert result["value"][0] == expected


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
