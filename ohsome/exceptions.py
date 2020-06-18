#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ohsome exception class """

import json


class OhsomeException(Exception):
    """
    Exception that is called whenever ohsome API returns an error code
    """
    def __init__(self, message=None, params=None, url=None, error_code=None, error=None, response=None):

        Exception.__init__(self, message)
        self.message = message
        self.url = url
        self.params = params
        self.error_code = error_code
        self.error = error

        if response is not None:
            self.response = response
            if not url:
                self.url = response.request.url
            if not params:
                self.params = response.request.body
            if not error_code:
                self.error_code = response.status_code
            if not message:
                self.message = json.loads(response.text)["message"]
            if not error:
                try:
                    self.error = json.loads(response.text)["error"]
                except KeyError:
                    self.error = ""
                except json.decoder.JSONDecodeError:
                    self.error = ""

    def __str__(self):
        return "OhsomeException - %s (%s): %s" % (self.error, self.error_code, self.message)
