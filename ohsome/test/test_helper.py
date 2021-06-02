#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for utility functions"""

from ohsome.helper import find_groupby_names, extract_error_message_from_invalid_json
import os
import logging


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
    expected_message = 'A broken response has been received: java.lang.RuntimeException: java.lang.RuntimeException: java.lang.RuntimeException: java.sql.SQLTransientConnectionException: HikariPool-1 - Connection is not available, request timed out after 30000ms.; "error" : "OK"; "timestamp" : "2020-05-19T07:07:25.356+0000"; "path" : "/elements/geometry"; "status" : 200'

    error_code, message = extract_error_message_from_invalid_json(invalid_response_text)

    assert expected_message == message
    assert expected_error_code == error_code


def test_extract_error_message_from_invalid_json_no_message():
    """
    Test whether error code and message are extracted correctly if theres is no message in the json response
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
    expected_message = 'A broken response has been received: java.lang.OutOfMemoryError; "error" : "OK"; "timestamp" : "2021-06-01T11:38:52.821+0000"; "path" : "/elements/geometry"; "status" : 200'

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
    expected_message = 'A broken response has been received: The given query is too large in respect to the given timeout. Please use a smaller region and/or coarser time period.; "timestamp" : "2021-06-02T10:07:46.438591"; "requestUrl" : "http://localhost:8080/elements/geometry"; "status" : 413'

    error_code, message = extract_error_message_from_invalid_json(invalid_response_text)

    assert error_code == expected_error_code
    assert message == expected_message
