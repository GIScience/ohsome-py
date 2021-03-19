#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test OhsomeExceptions"""

import os
import pytest
import logging
import geopandas as gpd
import ohsome


script_path = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)


def test_elements_count_exception(custom_client):
    """
    Tests whether a AssertionError is raised if the result cannot be converted to a geodataframe object
    :return:
    """
    # GIVEN
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01/2011-01-01/P1Y"
    fltr = "building=* and type:way"

    client = custom_client
    response = client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)

    with pytest.raises(AssertionError):
        response.as_geodataframe()


def test_timeout_error(custom_client):
    """
    Test whether an OhsomeException is raised, if the ohsome API contains a JSONDecodeError
    :return:
    """
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01/2011-01-01/P1Y"
    fltr = "building=* and type:way"
    timeout = 0

    client = custom_client
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.geometry.post(
            bboxes=bboxes, time=time, filter=fltr, timeout=timeout
        )
    assert (
        e_info.value.message
        == "The given query is too large in respect to the given timeout. Please use a smaller region and/or coarser time period."
    )


def test_invalid_url():
    """
    Test whether request can be sent to alternative url
    :return:
    """
    base_api_url = "https://api.ohsme.org/v0.9/"
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2018-01-01"
    fltr = "name=Krautturm and type:way"

    client = ohsome.OhsomeClient(base_api_url=base_api_url, log=False)
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)
    assert (
        e_info.value.message
        == "Connection Error: Query could not be sent. Make sure there are no network problems and "
        f"that the ohsome API URL {base_api_url}elements/count is valid."
    )


def test_invalid_endpoint():
    """
    Test whether request can be sent to alternative url
    :return:
    """
    base_api_url = "https://api.ohsme.org/v0.9/"
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2018-01-01"
    fltr = "name=Krautturm and type:way"

    client = ohsome.OhsomeClient(base_api_url=base_api_url, log=False)
    with pytest.raises(AttributeError):
        client.elements.cout.post(bboxes=bboxes, time=time, filter=fltr)


def test_disable_logging(custom_client):
    """
    Tests whether logging is disabled so no new log file if created if an OhsomeException occurs
    :return:
    """
    custom_client.log = False
    bboxes = [8.67555, 49.39885, 8.69637, 49.41122]
    fltr = "building=* and type:way"
    timeout = 0.001
    try:
        n_log_files_before = len(os.listdir(custom_client.log_dir))
    except FileNotFoundError:
        n_log_files_before = 0
    with pytest.raises(ohsome.OhsomeException):
        custom_client.elements.geometry.post(
            bboxes=bboxes, filter=fltr, timeout=timeout
        )

    if os.path.exists(custom_client.log_dir):
        n_log_files_after = len(os.listdir(custom_client.log_dir))
        assert n_log_files_before == n_log_files_after


def test_enable_logging(custom_client_without_log, tmpdir):
    """
    Tests whether logging is disabled so no new log file if created if an OhsomeException occurs
    :return:
    """
    custom_client_without_log.log = True
    custom_client_without_log.log_dir = tmpdir.mkdir("logs").strpath

    bboxes = [8.67555, 49.39885, 8.69637, 49.41122]
    fltr = "building=* and type:way"
    timeout = 0.001
    n_log_files_before = len(os.listdir(custom_client_without_log.log_dir))

    with pytest.raises(ohsome.OhsomeException):
        custom_client_without_log.elements.geometry.post(
            bboxes=bboxes, filter=fltr, timeout=timeout
        )

    n_log_files_after = len(os.listdir(custom_client_without_log.log_dir))
    assert n_log_files_before + 1 == n_log_files_after


def test_log_bpolys(custom_client_without_log, tmpdir):
    """
    Test whether a GeoDataFrame obejct is formatted correctly for ohsome api.
    :return:
    """

    custom_client_without_log.log = True
    custom_client_without_log.log_dir = tmpdir.mkdir("logs").strpath

    bpolys = gpd.read_file(f"{script_path}/data/polygons.geojson")
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:node"
    timeout = 0.001

    n_log_files_before = len(os.listdir(custom_client_without_log.log_dir))

    with pytest.raises(ohsome.OhsomeException):
        custom_client_without_log.elements.count.post(
            bpolys=bpolys, time=time, filter=fltr, timeout=timeout
        )
    n_log_files_after = len(os.listdir(custom_client_without_log.log_dir))
    assert n_log_files_before + 2 == n_log_files_after


def test_metadata_invalid_baseurl(custom_client_with_wrong_url):
    """
    Throw exception if the ohsome API is not available
    :return:
    """

    with pytest.raises(ohsome.OhsomeException):
        custom_client_with_wrong_url.metadata
