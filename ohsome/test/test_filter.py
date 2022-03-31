#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import pytest

from ohsome.filter import OhsomeFilter
from ohsome.helper import format_filter, build_filter


def test_ohsomefilter():
    """Test whether OhsomeFilter object is created correctly"""

    filter_dict = {
        "tags": {"natural": ["tree", "tree_row"], "landuse": "forest"},
        "geoms": "polygon",
        "types": ["way", "relation"],
    }
    ohsome_filter = OhsomeFilter(**filter_dict)
    assert isinstance(ohsome_filter, OhsomeFilter)
    assert ohsome_filter.geoms == ["polygon"]
    assert ohsome_filter.types == ["way", "relation"]
    assert ohsome_filter.tags == filter_dict["tags"]


def test_ohsomefilter_typo():
    """Test whether an error is thrown when an unknown parameter is passed to OhsomeFilter"""

    filter_dict = {
        "tags": {"natural": ["tree", "tree_row"], "landuse": "forest"},
        "geos": "polygon",
    }
    with pytest.raises(TypeError):
        OhsomeFilter(**filter_dict)


def test_build_filter():
    """Test whether filter parameter is built correctly from OhsomeFilter object"""
    filter_dict = {
        "tags": {"natural": ["tree", "tree_row"], "landuse": "forest"},
        "geoms": "polygon",
        "types": ["way", "relation"],
    }
    ohsome_filter = OhsomeFilter(**filter_dict)
    filter_str = build_filter(ohsome_filter)
    assert filter_str is not None
    assert isinstance(filter_str, str)
    assert (
        filter_str
        == "(natural in (tree, tree_row) or landuse=forest) and (geometry:polygon) and (type:way or type:relation)"
    )


def test_format_filter():
    """Test whether filter parameter is formatted correctly from OhsomeFilter object"""
    filter_dict = {
        "tags": {"natural": ["tree", "tree_row"], "landuse": "forest"},
        "geoms": "polygon",
        "types": ["way", "relation"],
    }
    ohsome_filter = OhsomeFilter(**filter_dict)
    formatted_filter = format_filter(ohsome_filter)
    assert formatted_filter is not None
    assert isinstance(formatted_filter, str)
    assert (
        formatted_filter
        == "(natural in (tree, tree_row) or landuse=forest) and (geometry:polygon) and (type:way or type:relation)"
    )


def test_format_filter_string():
    """Test whether filter parameter is formatted correctly from String object"""
    filter_str = "(natural in (tree, tree_row) or landuse=forest) and (geometry:polygon) and (type:way or type:relation)"
    formated_filter = format_filter(filter_str)
    assert formated_filter is not None
    assert isinstance(formated_filter, str)
    assert formated_filter == filter_str
