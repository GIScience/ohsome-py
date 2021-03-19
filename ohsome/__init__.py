#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ohsome API client for Python"""
import logging

from .exceptions import OhsomeException
from .response import OhsomeResponse
from .client import OhsomeClient

log_format = "%(asctime)s  %(module)8s  %(levelname)5s:  %(message)s"
logging.basicConfig(level="INFO", format=log_format)
