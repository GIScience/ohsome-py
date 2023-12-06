#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test OhsomeExceptions"""

import logging
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import geopandas as gpd
import pytest
import responses
from requests.exceptions import RequestException
from responses import registries
from urllib3 import Retry

import ohsome
from ohsome import OhsomeClient, OhsomeException

script_path = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger(__name__)


@pytest.mark.vcr
def test_timeout_error(base_client):
    """
    Test whether an OhsomeException is raised, if the ohsome API contains a JSONDecodeError
    :return:
    """
    bboxes = "8.67066,49.41423,8.68177,49.4204"
    time = "2010-01-01/2011-01-01/P1Y"
    fltr = "building=* and type:way"
    timeout = 0

    client = base_client
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.geometry.post(
            bboxes=bboxes, time=time, filter=fltr, timeout=timeout
        )
    assert (
        "The given query is too large in respect to the given timeout. Please use a smaller region and/or coarser "
        "time period." in e_info.value.message
    )


@pytest.mark.vcr
def test_invalid_url():
    """
    Test whether an OhsomeException is raises if the ohsome API url is invalid, i.e.
    https://api.ohsome.org/ instead of https://api.ohsome.org/v1
    :return:
    """
    base_api_url = "https://api.ohsome.org/"
    bboxes = "8.7137,49.4096,8.717,49.4119"
    time = "2018-01-01"
    fltr = "name=Krautturm and type:way"

    client = ohsome.OhsomeClient(base_api_url=base_api_url, log=False)
    with pytest.raises(ohsome.OhsomeException) as e_info:
        client.elements.count.post(bboxes=bboxes, time=time, filter=fltr)
    assert "Invalid URL:" in e_info.value.message


@pytest.mark.vcr
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


@pytest.mark.vcr
def test_disable_logging(base_client):
    """
    Tests whether logging is disabled so no new log file is created if an OhsomeException occurs
    :return:
    """
    base_client.log = False
    bboxes = [8.67555, 49.39885, 8.69637, 49.41122]
    fltr = "building=* and type:way"
    timeout = 0.001
    try:
        n_log_files_before = len(os.listdir(base_client.log_dir))
    except FileNotFoundError:
        n_log_files_before = 0
    with pytest.raises(ohsome.OhsomeException):
        base_client.elements.geometry.post(bboxes=bboxes, filter=fltr, timeout=timeout)

    if os.path.exists(base_client.log_dir):
        n_log_files_after = len(os.listdir(base_client.log_dir))
        assert n_log_files_after == n_log_files_before


@pytest.mark.vcr
def test_log_bpolys(base_client_without_log, tmpdir):
    """
    Test whether three log files are created when request fails (*bpolys.geojson, *.json and *_raw.txt)
    :return:
    """

    base_client_without_log.log = True
    base_client_without_log.log_dir = tmpdir.mkdir("logs").strpath

    bpolys = gpd.read_file(f"{script_path}/data/polygons.geojson")
    time = "2018-01-01"
    fltr = "amenity=restaurant and type:node"
    timeout = 0.001

    with pytest.raises(ohsome.OhsomeException):
        base_client_without_log.elements.count.post(
            bpolys=bpolys, time=time, filter=fltr, timeout=timeout
        )
    log_file_patterns = [
        "ohsome_*_bpolys.geojson",
        "ohsome_*_curl.sh",
        "ohsome_*.json",
        "ohsome_*raw.txt",
    ]
    for p in log_file_patterns:
        log_file = list(Path(base_client_without_log.log_dir).glob(p))
        assert len(log_file) == 1, f"Log file {p} not found"
        logger.info(f"Found log file: {log_file[0].name}")
        log_file[0].unlink()


@pytest.mark.vcr
def test_log_curl(base_client_without_log, tmpdir):
    """
    Test whether log file containing curl command is created when request fails
    :return:
    """

    base_client_without_log.log = True
    base_client_without_log.log_dir = tmpdir.mkdir("logs").strpath

    bboxes = [8.67555, 49.39885, 8.69637, 49.41122]
    timeout = 0.001

    with pytest.raises(ohsome.OhsomeException):
        base_client_without_log.elements.count.post(bboxes=bboxes, timeout=timeout)

    log_file = list(Path(base_client_without_log.log_dir).glob("ohsome_*_curl.sh"))
    with open(log_file[0]) as file:
        assert file.read() == (
            'curl -X POST -H "user-agent: ohsome-py/0.3.0" -H "Accept-Encoding: gzip, '
            'deflate" -H "Accept: */*" -H "Connection: keep-alive" -H "Content-Length: 60" '
            '-H "Content-Type: application/x-www-form-urlencoded" '
            "-d 'bboxes=8.67555%2C49.39885%2C8.69637%2C49.41122&timeout=0.001' "
            "https://api.ohsome.org/v1/elements/count"
        )


def test_metadata_invalid_baseurl(custom_client_with_wrong_url):
    """
    Throw exception if the ohsome API is not available
    :return:
    """

    with pytest.raises(ohsome.OhsomeException):
        _ = custom_client_with_wrong_url.metadata


@pytest.mark.vcr
def test_exception_invalid_parameters(base_client):
    """
    Test whether error message from ohsome API is forwarded to user
    :param base_client:
    :return:
    """
    bboxes = [8.6577, 49.3958, 8.7122, 49.4296]
    time = "2010-01-01/2020-01-01/P1M"
    fltr = "highway=* and type:way"
    with pytest.raises(ohsome.OhsomeException) as e_info:
        base_client.elements.count.groupByTag.post(
            bboxes=bboxes, time=time, filter=fltr
        )
        assert "You need to give one groupByKey parameter" in e_info.value.message


@pytest.mark.vcr
def test_exception_connection_reset(base_client):
    """
    Test whether error without response (e.g. connection reset) is handled correctly
    :param base_client:
    :return:
    """

    with patch(
        "requests.Response.raise_for_status",
        MagicMock(
            side_effect=RequestException(
                "This request was failed on purpose without response!"
            )
        ),
    ), patch("ohsome.OhsomeException.log_response", MagicMock()) as mock_func:
        bpolys = gpd.read_file(f"{script_path}/data/polygons.geojson")
        time = "2018-01-01"
        fltr = "name=Krautturm and type:way"

        with pytest.raises(ohsome.OhsomeException):
            base_client.elements.count.post(bpolys=bpolys, time=time, filter=fltr)

        mock_func.assert_not_called()


@responses.activate
def test_connection_error():
    """Test if the connection error response is correctly given."""
    url = "https://mock.com/"
    bboxes = "8.7137,49.4096,8.717,49.4119"

    responses.add(
        responses.PUT,
        url,
        status=503,
    )

    client = OhsomeClient(base_api_url=url, retry=False)

    with pytest.raises(OhsomeException) as e:
        client.post(bboxes=bboxes)

    assert e.value.message == (
        "Connection Error: Query could not be sent. Make sure there are no network problems "
        f"and that the ohsome API URL {url} is valid."
    )


@responses.activate(registry=registries.OrderedRegistry)
def test_max_retry_error():
    """Test if the retry mechnaism can be set and works as expected.

    Especially if a last retry is done, does not shadow its cause or enter an infinite recursion loop.
    """
    url = "https://mock.com"
    bboxes = "8.7137,49.4096,8.717,49.4119"

    rsp1 = responses.post(url, json={"message": "Try: ignored"}, status=500)
    rsp2 = responses.post(url, json={"message": "Retry 1: ignored"}, status=500)
    rsp3 = responses.post(url, json={"message": "Final try: raised"}, status=500)

    client = OhsomeClient(
        base_api_url=url,
        retry=Retry(total=1, status_forcelist=[500], allowed_methods=["GET", "POST"]),
    )

    with pytest.raises(OhsomeException, match="Final try: raised") as e:
        client.post(bboxes=bboxes)

    assert e.value.error_code == 500
    assert rsp1.call_count == 1
    assert rsp2.call_count == 1
    assert rsp3.call_count == 1
