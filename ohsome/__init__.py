#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Ohsome API client for Python"""
import warnings

from .clients import OhsomeClient  # noqa

# The order of imports here must remain to prevent circular imports
from .exceptions import OhsomeException  # noqa
from .response import OhsomeResponse  # noqa

warnings.warn(
    message="After October 2026, this version of `ohsome-py` will no longer work. "
    "The ohsome API V1 is reaching end-of-life in October 2026 and is replaced by V2. "
    "The ohsome-py library currently only supports ohsome API V1. "
    "The fate of the ohsome-py library is not yet decided, a newer version MAY support ohsome-API V2. "
    "To migrate independently of the `ohsome-py` library to the new ohsome API V2, please refer to the "
    "official documentation at https://docs.ohsome.org/ohsome-api/.",
    category=DeprecationWarning,
    stacklevel=1,
)
