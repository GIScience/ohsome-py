#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Conftest for shared pytest fixtures"""
import logging
import os

import pytest

import ohsome
from ohsome import OhsomeException

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def custom_client(tmpdir_factory):
    """Session-wide test client."""
    temp_directory = tmpdir_factory.mktemp("custom_client").mkdir("logs").strpath
    ohsome_url = os.getenv("OHSOME_URL", "localhost")
    ohsome_port = os.getenv("OHSOME_PORT", "8080")

    client = ohsome.OhsomeClient(
        base_api_url=f"http://{ohsome_url}:{ohsome_port}/", log_dir=temp_directory
    )

    try:
        client.metadata
    except OhsomeException as err:
        logger.warning(
            f"Local/custom ohsome-api endpoint not found. Using the public  one as fallback: "
            f"https://api.ohsome.org/v1/. It is highly recommended to use a local endpoint for testing and development."
            f" The error while searching for a local one: {err}"
        )
        client = ohsome.OhsomeClient(
            base_api_url="https://api.ohsome.org/v1/", log_dir=temp_directory
        )

    yield client


@pytest.fixture(scope="session")
def custom_client_without_log(tmpdir_factory):
    """Session-wide test client."""
    ohsome_url = os.getenv("OHSOME_URL", "localhost")
    ohsome_port = os.getenv("OHSOME_PORT", "8080")

    client = ohsome.OhsomeClient(
        base_api_url=f"http://{ohsome_url}:{ohsome_port}/", log=False
    )

    try:
        client.metadata
    except OhsomeException as err:
        logger.warning(
            f"Local/custom ohsome-api endpoint not found. Using the public  one as fallback: "
            f"https://api.ohsome.org/v1/. It is highly recommended to use a local endpoint for testing and development."
            f" The error while searching for a local one: {err}"
        )
        client = ohsome.OhsomeClient(
            base_api_url="https://api.ohsome.org/v1/", log=False
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
