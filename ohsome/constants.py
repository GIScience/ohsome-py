#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Constants and default values"""
from pathlib import Path

OHSOME_BASE_API_URL = "https://api.ohsome.org/v1/"
DEFAULT_LOG = True
DEFAULT_LOG_DIR = Path("./ohsome_log")
# update version in pyproject.toml as well
OHSOME_VERSION = "0.3.0"
