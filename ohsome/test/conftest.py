#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Conftest for shared pytest fixtures"""
import logging
import pytest
import ohsome

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def base_client(tmpdir_factory):
    """Session-wide test client."""
    temp_directory = tmpdir_factory.mktemp("base_client").mkdir("logs").strpath
    client = ohsome.OhsomeClient(log_dir=temp_directory)
    assert client.metadata  # call metadata once to ensure it is cached
    yield client


@pytest.fixture(scope="session")
def base_client_without_log():
    """Session-wide test client."""
    client = ohsome.OhsomeClient(log=False)
    assert client.metadata  # call metadata once to ensure it is cached
    yield client


@pytest.fixture(scope="session")
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
