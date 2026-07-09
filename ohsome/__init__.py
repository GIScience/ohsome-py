#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ohsome API client for Python"""
import warnings

# The order of imports here must remain to prevent circular imports
from .exceptions import OhsomeException  # noqa
from .response import OhsomeResponse  # noqa
from .clients import OhsomeClient  # noqa

warnings.warn(
    message="Ohsome-API V1 is reaching end-of-life in October 2026. "
    "The ohsome-py library currently only supports ohsome API v1. "
    "This version of ohsome-py will stop working in October 2026. "
    "The fate of the ohsome-py library is not yet decided, a newer version MAY support ohsome-API V2. "
    "To move to Ohsome-API V2 independently please see the migration instructions at https://api.heigit.org/ohsome-api-staging/v2/docs.",
    category=DeprecationWarning,
    stacklevel=1,
)
