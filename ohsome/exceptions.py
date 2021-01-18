#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Classes to handles error codes of ohsome API """


class OhsomeException(Exception):
    """
    Exception that is called whenever ohsome API returns an error code
    """

    def __init__(self, message=None, url=None, params=None, status_code=None):
        Exception.__init__(self, message)
        self.message = message
        self.url = url
        self.params = params
        self.status_code = status_code

    def __str__(self):
        return "OhsomeException ({}): {}".format(self.status_code, self.message)
