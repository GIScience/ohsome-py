#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for utility functions"""

from ohsome.helper import find_groupby_names


def test_find_groupby_names_one_group():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    url = "https://api.ohsome.org/v0.9/elements/count/groupBy/boundary"
    expected = ["boundary"]
    result = find_groupby_names(url)
    assert expected == result


def test_find_groupby_names_two_groups():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    url = "https://api.ohsome.org/v0.9/elements/count/groupBy/boundary/groupBy/tag"
    expected = ["boundary", "tag"]
    result = find_groupby_names(url)
    assert expected == result
