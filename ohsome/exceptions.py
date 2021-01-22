#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Class to handle error codes of ohsome API """

import os
import json
import datetime as dt


class OhsomeException(Exception):
    """
    Exception to handle ohsome API errors
    """

    def __init__(self, message=None, url=None, params=None, status=None):
        Exception.__init__(self, message)
        self.message = message
        self.url = url
        self.parameters = params
        self.status = status

    def __str__(self):
        return "OhsomeException ({}): {}".format(self.status, self.message)

    def to_json(self, dir):
        """
        Exports the error message, url and parameters to a file.
        :return:
        """
        outfile = os.path.join(
            dir,
            "ohsome_exception_{}.json".format(
                dt.datetime.now().strftime("%Y%m%dT%H%M%S")
            ),
        )
        print(outfile)
        out = {
            "url": self.url,
            "parameters": self.parameters,
            "status": self.status,
            "message": self.message,
        }
        with open(outfile, "w") as dst:
            json.dump(obj=out, fp=dst, indent=4)
