#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test OhsomeExceptions"""

import os
import pytest
import ohsome


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


def test_catch_incomplete_response_error():
    """
    Tests whether a AssertionError is raised if the result cannot be converted to a geodataframe object
    :return:
    """
    # todo: Find test case
    # client = ohsome.OhsomeClient()
    # bboxes = [8.67555, 49.39885, 8.69637, 49.41122]
    # fltr = "building=* and type:way"
    # try:
    #   client.elements.geometry.post(bboxes=bboxes, filter=fltr)
    # except ohsome.OhsomeException as e:
    #    print(e)
    pass


def test_disable_logging():
    """
    Tests whether logging is disabled so no new log file if created if an OhsomeException occurs
    :return:
    """
    client = ohsome.OhsomeClient(log=False)
    bboxes = [8.67555, 49.39885, 8.69637, 49.41122]
    fltr = "building=* and type:way"
    timeout = 0.001
    n_log_files_before = len(os.listdir(client.log_dir))

    with pytest.raises(ohsome.OhsomeException):
        client.elements.geometry.post(bboxes=bboxes, filter=fltr, timeout=timeout)

    n_log_files_after = len(os.listdir(client.log_dir))
    assert n_log_files_before == n_log_files_after


def test_enable_logging():
    """
    Tests whether logging is disabled so no new log file if created if an OhsomeException occurs
    :return:
    """
    client = ohsome.OhsomeClient(log=True)
    bboxes = [8.67555, 49.39885, 8.69637, 49.41122]
    fltr = "building=* and type:way"
    timeout = 0.001
    n_log_files_before = len(os.listdir(client.log_dir))

    with pytest.raises(ohsome.OhsomeException):
        client.elements.geometry.post(bboxes=bboxes, filter=fltr, timeout=timeout)

    n_log_files_after = len(os.listdir(client.log_dir))
    assert n_log_files_before + 1 == n_log_files_after

    logfile = os.path.join(client.log_dir, os.listdir(client.log_dir)[0])
    os.unlink(logfile)


def test_metadata_invalid_baseurl():
    """
    Throw exception if the ohsome API is not available
    :return:
    """
    ohsome_url = os.getenv("OHSOME_URL", "localhot")
    ohsome_port = os.getenv("OHSOME_PORT", "8080")

    client = ohsome.OhsomeClient(base_api_url=f"http://{ohsome_url}:{ohsome_port}/")

    with pytest.raises(ohsome.OhsomeException):
        client.metadata
