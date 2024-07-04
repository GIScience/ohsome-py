#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for utility functions"""
import datetime
import json
import logging
import os

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely import Polygon

from ohsome import OhsomeException
from ohsome.helper import (
    find_groupby_names,
    extract_error_message_from_invalid_json,
    format_time,
    convert_arrays,
    format_list_parameters,
    format_bpolys,
)

script_path = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)


def test_find_groupby_names_one_group():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    url = "https://api.ohsome.org/v0.9/elements/count/groupBy/boundary"
    expected = ["boundary"]
    result = find_groupby_names(url)
    assert expected == result


def test_find_groupby_names_two_groups():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    url = "https://api.ohsome.org/v0.9/elements/count/groupBy/boundary/groupBy/tag"
    expected = ["boundary", "tag"]
    result = find_groupby_names(url)
    assert expected == result


def test_extract_error_message_from_invalid_json():
    """
    Test whether error code and message are extracted correctly
    :return:
    """

    invalid_response = f"{script_path}/data/invalid_response.txt"
    with open(invalid_response) as src:
        invalid_response_text = src.read()

    expected_error_code = 500
    expected_message = (
        "A broken response has been received: java.lang.RuntimeException: "
        "java.lang.RuntimeException: java.lang.RuntimeException: "
        "java.sql.SQLTransientConnectionException: HikariPool-1 - Connection is not available, request "
        'timed out after 30000ms.; "error" : "OK"; "timestamp" : "2020-05-19T07:07:25.356+0000"; '
        '"path" : "/elements/geometry"; "status" : 200'
    )

    error_code, message = extract_error_message_from_invalid_json(invalid_response_text)

    assert expected_message == message
    assert expected_error_code == error_code


def test_extract_error_message_from_invalid_json_no_message():
    """
    Test whether error code and message are extracted correctly if there is no message in the json response
    :return:
    """

    invalid_response = f"{script_path}/data/invalid_response_no_message.txt"
    with open(invalid_response) as src:
        invalid_response_text = src.read()

    expected_error_code = 500
    expected_message = "A broken response has been received"

    error_code, message = extract_error_message_from_invalid_json(invalid_response_text)

    assert expected_message == message
    assert expected_error_code == error_code


def test_extract_error_message_from_invalid_json_outOfMemory():
    """
    Test whether error code and message are extracted correctly if the server reports out of memory
    :return:
    """

    invalid_response = f"{script_path}/data/invalid_response_outOfMemory.txt"
    with open(invalid_response) as src:
        invalid_response_text = src.read()

    expected_error_code = 507
    expected_message = (
        'A broken response has been received: java.lang.OutOfMemoryError; "error" : "OK"; '
        '"timestamp" : "2021-06-01T11:38:52.821+0000"; "path" : "/elements/geometry"; "status" : 200'
    )

    error_code, message = extract_error_message_from_invalid_json(invalid_response_text)

    assert expected_message == message
    assert expected_error_code == error_code


def test_extract_error_message_from_invalid_json_custonErrorCode():
    """
    Test whether error code and message are extracted correctly if the server reports out of memory
    :return:
    """

    invalid_response = f"{script_path}/data/invalid_response_customCode.txt"
    with open(invalid_response) as src:
        invalid_response_text = src.read()

    expected_error_code = 413
    expected_message = (
        "A broken response has been received: The given query is too large in respect to the given "
        'timeout. Please use a smaller region and/or coarser time period.; "timestamp" : '
        '"2021-06-02T10:07:46.438591"; "requestUrl" : "http://localhost:8080/elements/geometry"; '
        '"status" : 413'
    )

    error_code, message = extract_error_message_from_invalid_json(invalid_response_text)

    assert error_code == expected_error_code
    assert message == expected_message


def test_array_conversion():
    """Tests whether numpy arrays are supported as input parameters"""
    method_input = {"bbox": np.ones(3)}

    output = convert_arrays(method_input)

    assert isinstance(output["bbox"], list)


def test_convert_arrays_multi_dim():
    """Test error raising on multi dim array."""
    method_input = {"bbox": np.ndarray(shape=(2, 2))}
    with pytest.raises(
        AssertionError,
        match="Only one dimensional arrays are supported for parameter bbox",
    ):
        convert_arrays(method_input)


def test_format_time():
    """Test if the time formatter covers all cases."""
    parameters = {
        "time_str": {"input": "2022-01-01", "output": "2022-01-01"},
        "time_datetime": {
            "input": datetime.datetime(2022, 1, 1),
            "output": "2022-01-01T00:00:00",
        },
        "time_date": {"input": datetime.date(2022, 1, 1), "output": "2022-01-01"},
        "time_list": {
            "input": ["2022-01-01", "2022-01-02"],
            "output": "2022-01-01,2022-01-02",
        },
        "time_pandas_index": {
            "input": pd.date_range("2022-01-01", periods=2, freq="D"),
            "output": "2022-01-01T00:00:00,2022-01-02T00:00:00",
        },
        "time_pandas_series": {
            "input": pd.Series(["2022-01-01", "2022-01-02"]),
            "output": "2022-01-01,2022-01-02",
        },
    }

    for k, v in parameters.items():
        output = format_time(v["input"])
        assert v["output"] == output, f"Input type {k} not correctly formatted."


def test_format_time_error_format_not_supported():
    """Test weather a time with wrong type (e.g. a dict) raises an error."""
    with pytest.raises(
        ValueError,
        match="The given time format <class 'dict'> is not supported. Feel free to open an "
        "issue in the ohsome-py repository for a feature request.",
    ):
        format_time({})


def test_format_list_parameters():
    """Test if formatting of list-like parameters works, and does not affect other parameters."""
    method_input = {
        "groupByKeys": ["k1", "k2"],
        "groupByValues": ["v1", "v2"],
        "otherParam": ["l"],
        "properties": ["p1"],
    }

    expected_output = {
        "groupByKeys": "k1,k2",
        "groupByValues": "v1,v2",
        "otherParam": ["l"],
        "properties": "p1",
    }

    output = format_list_parameters(method_input)

    assert output == expected_output


def test_format_bpolys():
    """Test if the formatting of bounding polys works correctly."""
    with pytest.raises(OhsomeException) as e:
        format_bpolys({})
        assert (
            e.value.message
            == "bolys must be a geojson string, a shapely polygonal object or a geopandas object"
        )

    geojson = json.dumps(
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": "0",
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]]
                        ],
                    },
                }
            ],
        }
    )

    assert format_bpolys(geojson) == geojson

    polygon = Polygon(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)))
    assert format_bpolys(polygon) == geojson

    series = gpd.GeoSeries(
        data=[polygon],
        crs="EPSG:4326",
    )
    assert format_bpolys(series) == geojson

    df = gpd.GeoDataFrame(
        geometry=[polygon],
        crs="EPSG:4326",
    )
    assert format_bpolys(df) == geojson
