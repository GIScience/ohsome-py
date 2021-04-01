#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ohsome API client for Python"""

from .exceptions import OhsomeException
from .response import OhsomeResponse
from .clients import OhsomeClient
import logging

log_format = "%(asctime)s  %(module)8s  %(levelname)5s:  %(message)s"
logging.basicConfig(level="INFO", format=log_format)
