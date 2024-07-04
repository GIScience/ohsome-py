#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for ohsome client"""
import datetime as dt
import logging
import os

import geopandas as gpd
import pandas as pd
import pytest

import ohsome
from ohsome import OhsomeClient
from ohsome.constants import OHSOME_VERSION

script_path = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)


def test_start_end_time_is_datetime(base_client):
    """Test if the start_ end end_timestamp is in datetime format without timezone."""
    assert isinstance(base_client.start_timestamp, dt.datetime)
    assert isinstance(base_client.end_timestamp, dt.datetime)
    assert base_client.start_timestamp.tzinfo is None
    assert base_client.end_timestamp.tzinfo is None


def test_api_version(base_client):
    """
    Get ohsome API version
    :return:
    """
    assert isinstance(base_client.api_version, str)


@pytest.mark.vcr(match_on=["method", "headers"])
def test_user_agent(base_client):
    """
    Checks user agent set by ohsome-py
    :return:
    """
    resp = base_client._session().get(base_client._metadata_url)
    used_user_agent = resp.request.headers["user-agent"]
    assert used_user_agent == f"ohsome-py/{OHSOME_VERSION}"


@pytest.mark.vcr
def test_check_time_parameter_list(base_client):
    """
    Checks whether time provided as list of strings is converted correctly
    :return:
    """
    time = pd.date_range("2018-01-01", periods=3, freq="D")
    time = time.strftime("%Y-%m-%dT%H:%M:%S").tolist()
    bcircles = gpd.read_file(f"{script_path}/data/points.geojson")
    fltr = "amenity=restaurant and type:way"

    client = base_client
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)


@pytest.mark.vcr
def test_check_time_parameter_datetime(base_client):
    """
    Checks whether time provided as pandas.Series is converted correctly
    :return:
    """
    bcircles = gpd.read_file(f"{script_path}/data/points.geojson")
    fltr = "amenity=restaurant and type:way"
    client = base_client

    time = [
        dt.datetime.strptime("2018-01-01", "%Y-%m-%d"),
        dt.datetime.strptime("2018-01-02", "%Y-%m-%d"),
    ]
    response = client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)
    result = response.as_dataframe()
    assert len(result) == 2


@pytest.mark.vcr
def test_end_timestamp_as_time_input(base_client):
    """
    Test whether the end_timestamp value can be used as input to a query as time
    :return:
    """
    bcircles = gpd.read_file(f"{script_path}/data/points.geojson")
    fltr = "amenity=restaurant and type:way"
    client = base_client

    time = client.end_timestamp
    response = client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)
    result = response.as_dataframe()
    assert len(result) == 1


@pytest.mark.vcr
def test_format_bcircles_dataframe(base_client):
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

    client = base_client
    client.elements.count.groupByBoundary.post(
        bcircles=bcircles, time=time, filter=fltr
    )


@pytest.mark.vcr
def test_format_bcircles_list(base_client):
    """
    Test whether a DataFrame object given as 'bcircles' is formatted correctly.
    :return:
    """
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:node"
    client = base_client

    bcircles = [[8.695, 49.41, 200], [8.696, 49.41, 200]]
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)

    bcircles = {1: [8.695, 49.41, 200], 2: [8.696, 49.41, 200]}
    client.elements.count.groupByBoundary.post(
        bcircles=bcircles, time=time, filter=fltr
    )

    bcircles = ["1:8.695, 49.41, 200", "2:8.696, 49.41, 200"]
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)

    bcircles = "1:8.695, 49.41, 200"
    client.elements.count.post(bcircles=bcircles, time=time, filter=fltr)


@pytest.mark.vcr
def test_format_bcircles_pandas(base_client):
    """
    Test whether a pandas.DataFrame object given as 'bcircles' is formatted correctly.
    :return:
    """
    bcircles = gpd.read_file(f"{script_path}/data/points.geojson")
    time = "2014-01-01/2017-01-01/P1Y"
    fltr = "amenity=restaurant and type:way"

    client = base_client
    client.elements.count.groupByBoundary.post(
        bcircles=bcircles, time=time, filter=fltr
    )


@pytest.mark.vcr
def test_format_bcircles_geodataframe_geometry_error(base_client):
    """
    Test whether a GeoDataFrame object given as 'bcircles' is formatted correctly.
    :return:
    """
    bcircles = gpd.read_file(f"{script_path}/data/polygons.geojson")
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:way"

    client = base_client
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.count.groupByBoundary.post(
            bcircles=bcircles, time=time, filter=fltr
        )
    assert (
        "The geometry of the 'bcircles' GeoDataFrame may only include 'Point' geometry types and requires a 'radius' "
        "column." in e_info.value.message
    )
    del client


@pytest.mark.vcr
def test_format_bboxes_dataframe(base_client):
    """
    Tests whether input parameter given as a pandas.DataFrame is formatted correctly to a string
    :return:
    """
    data = gpd.read_file(f"{script_path}/data/polygons.geojson")
    bboxes = data.bounds
    time = "2010-01-01"
    fltr = "amenity=restaurant and type:node"

    client = base_client
    client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)


@pytest.mark.vcr
def test_format_bboxes_dataframe_missing_columns(base_client):
    """
    Tests whether input parameter given as a pandas.DataFrame is formatted correctly to a string
    :return:
    """
    data = gpd.read_file(f"{script_path}/data/polygons.geojson")
    bboxes = data.bounds
    bboxes.drop(columns="minx", inplace=True)
    time = "2010-01-01"
    fltr = "amenity=restaurant and type:node"

    client = base_client
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)
    if "occurred at index 0" in e_info.value.message:
        # Python 3.6 does some weird stuff with the output. So it differs a bit.
        assert (
            "Column ('minx', 'occurred at index 0') is missing in the dataframe provided as 'bboxes'."
            in e_info.value.message
        )
    else:
        assert (
            "Column 'minx' is missing in the dataframe provided as 'bboxes'."
            in e_info.value.message
        )


@pytest.mark.vcr
def test_format_bboxes_geodataframe(base_client):
    """
    Tests whether input parameter given as a pandas.DataFrame is formatted correctly to a string
    :return:
    """
    data = gpd.read_file(f"{script_path}/data/polygons.geojson")
    time = "2010-01-01/2011-01-01/P1Y"
    fltr = "amenity=restaurant and type:node"

    client = base_client
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.count.post(bboxes=data, time=time, filter=fltr)

    assert (
        "Use the 'bpolys' parameter to specify the boundaries using a "
        "geopandas object." in e_info.value.message
    )


@pytest.mark.vcr
def test_format_bboxes_list(base_client):
    """
    Tests whether parameter bboxes given as a list is formatted correctly
    :return:
    """
    time = "2010-01-01"
    fltr = "amenity=restaurant and type:node"

    client = base_client

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


@pytest.mark.vcr
def test_post_with_endpoint_string(base_client):
    """
    Tests whether a request can be sent of by providing the endpoint url as a string to post()
    :return:
    """
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2015-01-01,2016-01-01"
    filter = "name=Krautturm and type:way"

    endpoint = "contributions/latest/bbox"
    client = base_client
    response = client.post(endpoint=endpoint, bboxes=bboxes, time=time, filter=filter)
    result = response.as_dataframe()
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 1

    # Test query with leading and ending slashes
    endpoint = "/contributions/latest/bbox/"
    client = base_client
    response = client.post(endpoint=endpoint, bboxes=bboxes, time=time, filter=filter)
    result = response.as_dataframe()

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 1


def test_none_init():
    """Test if the input parameters can set to None explicitly."""
    assert OhsomeClient(
        base_api_url=None,
        log=None,
        log_dir=None,
        cache=None,
        user_agent=None,
        retry=None,
    )
