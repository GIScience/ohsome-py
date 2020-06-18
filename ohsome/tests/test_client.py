#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tests for ohsome client """

import pandas as pd
from nose.tools import raises
import geojson
import geopandas as gpd
import ohsome


@raises(ohsome.OhsomeException)
def test_handle_multiple_responses_throw_timeouterror():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    # GIVEN
    bboxes = [8.67066,49.41423,8.68177,49.4204]
    time = "2010-01-01/2011-01-01/P1Y"
    keys = ["building"]
    values = [""]

    # WHEN
    client = ohsome.OhsomeClient()
    response = client.elements.count.post(bboxes=bboxes, time=time, keys=keys, values=values, timeout=2)
    del client


def test_elements_count():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    # GIVEN
    bboxes = [8.67066,49.41423,8.68177,49.4204]
    time = "2010-01-01/2011-01-01/P1Y"
    keys = ["building"]
    values = [""]

    timestamps = ["2010-01-01T00:00:00Z", "2011-01-01T00:00:00Z"]
    counts = [53.0, 256.0]
    expected = pd.DataFrame({"timestamp": timestamps, "value": counts})

    # WHEN
    client = ohsome.OhsomeClient()
    response = client.elements.count.post(bboxes=bboxes, time=time, keys=keys, values=values)
    result = response.as_dataframe()
    del client

    # THEN
    assert expected.equals(result)

def test_elements_count_group_by_key():
    """
    Tests counting elements within a bounding box and grouping them by keys
    :return:
    """

    #GIVEN
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01/2011-01-01/P1Y"
    groupByKeys = ["building"]

    timestamps = ["2010-01-01T00:00:00Z", "2011-01-01T00:00:00Z", "2010-01-01T00:00:00Z", "2011-01-01T00:00:00Z"]
    counts = [482.0, 628.0, 53.0, 256.0]
    keys = ["remainder", "remainder", "building", "building"]
    expected = pd.DataFrame({"key": keys, "timestamp": timestamps, "value": counts})
    expected.set_index(["key", "timestamp"], inplace=True)

    # WHEN
    client = ohsome.OhsomeClient()
    response = client.elements.count.groupBy.key.post(bboxes=bboxes, groupByKeys=groupByKeys, time=time)
    results = response.as_dataframe()

    # THEN
    assert expected.equals(results)

def test_elemets_count_ratio():
    """
    Tests count ratio
    :return:
    """
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01"
    keys = ["building"]
    keys2 = ["addr:city"]
    values = [""]
    values2 = [""]

    expected = 365.0

    client = ohsome.OhsomeClient()
    response = client.elements.count.ratio.post(bboxes=bboxes, time=time, keys=keys, keys2=keys2,
                                                values=values, values2=values2)
    #results = response.as_dataframe()


@raises(AssertionError)
def test_elements_count_exception():
    """
    Tests whether a TypeError is raised if the result cannot be converted to a geodataframe object
    :return:
    """
    # GIVEN
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01/2011-01-01/P1Y"
    keys = ["building"]
    values = [""]

    # WHEN
    client = ohsome.OhsomeClient()
    response = client.elements.count.post(bboxes=bboxes, time=time, keys=keys, values=values)
    response.as_geodataframe()


def test_elements_geometry():
    """
    Tests whether the result of an elements/geometry query can be converted to a geodataframe
    :return:
    """
    # GIVEN
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01"
    keys = ["landuse"]
    values = ["grass"]

    # WHEN
    client = ohsome.OhsomeClient()
    response = client.elements.geometry.post(bboxes=bboxes, time=time, keys=keys, values=values)
    result = response.as_geodataframe()
    del client

    # THEN
    assert len(result.geometry) == 9


def test_format_coordinates():
    """
    Asserts that coordinates of a MultiPolygon are concerted correctly
    :return:
    """
    # GIVEN
    bpolys = geojson.FeatureCollection([{"type": "Feature",
                                         "geometry": {"coordinates": [[[[13,51], [13,51.1], [13.1,51.1], [13.1,51], [13,51]],
                                          [[13,51], [14,51.1], [14.1,51.1], [14.1,51], [14,51]]]],
                                                    "type": "MultiPolygon"}}])
    time = "2018-01-01"
    keys = ["landuse"]
    values = ["grass"]

    # WHEN
    client = ohsome.OhsomeClient()
    response = client.elements.geometry.post(bpolys=ohsome.format_coordinates(bpolys), time=time, keys=keys, values=values)
    result = response.as_geodataframe()
    del client

    # THEN
    assert len(result.geometry) == 74

def test_format_geodataframe():

    # GIVEN
    bpolys = geojson.FeatureCollection([{"type": "Feature",
                                         "properties": {"id": 0},
                                         "geometry": {"coordinates": [
                                             [[[13, 51], [13, 51.1], [13.1, 51.1], [13.1, 51], [13, 51]]],
                                             [[[14, 51], [14, 51.1], [14.1, 51.1], [14.1, 51], [14, 51]]]],
                                                      "type": "MultiPolygon"}}])

    bpolys_df = gpd.GeoDataFrame().from_features(bpolys)
    time = "2018-01-01"
    keys = ["amenity"]
    values = [""]
    format = "geojson"
    properties = ["tags", "metadata"]

    # WHEN
    client = ohsome.OhsomeClient()
    response = client.elements.count.groupBy.boundary.post(bpolys=bpolys_df, time=time, keys=keys, values=values,
                                                           format=format, properties=properties)
    result = response.as_geodataframe()
    del client

    # THEN
    assert result["value"][0] == 538

def test_parallel_user():

    # GIVEN
    bpolys = geojson.FeatureCollection([{"type": "Feature",
                                         "properties": {"id": 0},
                                         "geometry": {"coordinates": [
                                             [[[13, 51], [13, 51.1], [13.1, 51.1], [13.1, 51], [13, 51]]],
                                             [[[14, 51], [14, 51.1], [14.1, 51.1], [14.1, 51], [14, 51]]]],
                                                      "type": "MultiPolygon"}},
                                        {"type": "Feature",
                                         "properties": {"id": 1},
                                         "geometry": {"coordinates": [
                                             [[[13, 51], [13, 51.1], [13.1, 51.1], [13.1, 51], [13, 51]]],
                                             [[[14, 51], [14, 51.1], [14.1, 51.1], [14.1, 51], [14, 51]]]],
                                             "type": "MultiPolygon"}}
                                        ])

    bpolys_df = gpd.GeoDataFrame().from_features(bpolys)
    timeperiod = "2017-01-01,2018-01-01"
    keys = ["amenity"]
    values = [""]
    format = "json"
    properties = ["metadata"]

    # WHEN
    client = ohsome.OhsomeClientParallel(chunksize=1)
    response = client.users.count.groupBy.boundary.post(bpolys=bpolys_df, time=timeperiod, keys=keys, values=values,
                                                           format=format, properties=properties)
    result = response.as_dataframe()
    del client

    # THEN
    assert result["value"][0] == 33.
