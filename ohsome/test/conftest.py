#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Conftest for shared pytest fixtures"""
import logging
from unittest.mock import patch, PropertyMock

import pytest
from urllib3 import Retry

import ohsome

logger = logging.getLogger(__name__)


@pytest.fixture
def mocked_metadata():
    """A default metadata dictionary.

    @return:
    """
    return {
        "attribution": {
            "url": "https://ohsome.org/copyrights",
            "text": "© OpenStreetMap contributors",
        },
        "apiVersion": "1.10.1",
        "timeout": 600.0,
        "extractRegion": {
            "spatialExtent": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-180.0, -90.0],
                        [180.0, -90.0],
                        [180.0, 90.0],
                        [-180.0, 90.0],
                        [-180.0, -90.0],
                    ]
                ],
            },
            "temporalExtent": {
                "fromTimestamp": "2007-10-08T00:00:00Z",
                "toTimestamp": "2023-11-25T13:00:00Z",
            },
            "replicationSequenceNumber": 99919,
        },
    }


@pytest.fixture
def base_client(mocked_metadata, tmpdir_factory):
    """Session-wide test client."""
    temp_directory = tmpdir_factory.mktemp("base_client").mkdir("logs").strpath
    with patch(
        "ohsome.clients._OhsomeInfoClient.metadata",
        new_callable=PropertyMock,
        return_value=mocked_metadata,
    ):
        client = ohsome.OhsomeClient(log_dir=temp_directory)
        yield client


@pytest.fixture
def base_client_without_log(mocked_metadata):
    """Session-wide test client."""
    with patch(
        "ohsome.clients._OhsomeInfoClient.metadata",
        new_callable=PropertyMock,
        return_value=mocked_metadata,
    ):
        client = ohsome.OhsomeClient(log=False)
        yield client


@pytest.fixture
def custom_client_with_wrong_url(tmpdir_factory):
    """Session-wide test client."""
    temp_directory = tmpdir_factory.mktemp("base_client").mkdir("logs").strpath
    client = ohsome.OhsomeClient(
        base_api_url="https://imwrong",
        log_dir=temp_directory,
    )
    yield client


@pytest.fixture(scope="module")
def vcr_config():
    """Get custom VCR configuration for tests."""
    return {
        "match_on": [
            "method",
            "host",
            "path",
            "query",
            "body",
            "headers",
        ]
    }
