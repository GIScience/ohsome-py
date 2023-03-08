#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Conftest for shared pytest fixtures"""
import logging
import os
import pytest
import ohsome

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def custom_client(tmpdir_factory):
    """Session-wide test client."""
    temp_directory = tmpdir_factory.mktemp("custom_client").mkdir("logs").strpath
    ohsome_url = os.getenv("OHSOME_URL", "https://api.ohsome.org/v1")
    ohsome_port = os.getenv("OHSOME_PORT", "80")

    client = ohsome.OhsomeClient(
        base_api_url=f"http://{ohsome_url}:{ohsome_port}/", log_dir=temp_directory
    )

    yield client


@pytest.fixture(scope="session")
def custom_client_without_log(tmpdir_factory):
    """Session-wide test client."""
    ohsome_url = os.getenv("OHSOME_URL", "https://api.ohsome.org/v1")
    ohsome_port = os.getenv("OHSOME_PORT", "80")

    client = ohsome.OhsomeClient(
        base_api_url=f"http://{ohsome_url}:{ohsome_port}/", log=False
    )

    yield client


@pytest.fixture(scope="session")
def custom_client_with_wrong_url(tmpdir_factory):
    """Session-wide test client."""
    temp_directory = tmpdir_factory.mktemp("custom_client").mkdir("logs").strpath
    ohsome_url = os.getenv("OHSOME_URL", "imwrong")
    ohsome_port = os.getenv("OHSOME_PORT", "8080")

    client = ohsome.OhsomeClient(
        base_api_url=f"http://{ohsome_url}:{ohsome_port}/",
        log_dir=temp_directory,
    )

    yield client


@pytest.fixture(scope="module")
def vcr_config():
    """Get custom VCR configuration for tests."""
    return {
        "match_on": [
            "method",
            "scheme",
            "host",
            "port",
            "path",
            "query",
            "body",
            "headers",
        ]
    }
