#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tests for utility functions """

import ohsome


def test_find_groupby_names_one_group():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    # GIVEN
    url = 'https://api.ohsome.org/v0.9/elements/count/groupBy/boundary'
    # Expected
    expected = ["boundary"]
    # WHEN
    result = ohsome.find_groupby_names(url)

    # THEN
    assert expected == result


def test_find_groupby_names_two_groups():
    """
    Tests counting elements within a bounding box for two timestamps
    :return:
    """
    # GIVEN
    url = 'https://api.ohsome.org/v0.9/elements/count/groupBy/boundary/groupBy/tag'
    # Expected
    expected = ["boundary", "tag"]
    # WHEN
    result = ohsome.find_groupby_names(url)

    # THEN
    assert expected == result