#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Class to handle error codes of ohsome API"""

import datetime as dt
import json
import os


class OhsomeException(Exception):
    """Exception to handle ohsome API errors"""

    def __init__(self, message=None, url=None, params=None, error_code=None):
        """Initialize OhsomeException object"""
        super(Exception, self).__init__(message)
        self.message = message
        self.url = url
        if params:
            self.parameters = {k: v for k, v in params.items() if v is not None}
        self.error_code = error_code
        self.timestamp = dt.datetime.now().isoformat()

    def __str__(self):
        return f"OhsomeException ({self.error_code}): {self.message}"

    def to_json(self, dir):
        """
        Exports the error message, url and parameters to a file.
        :return:
        """
        outfile = os.path.join(
            dir,
            f"ohsome_exception_{dt.datetime.now().strftime('%Y%m%dT%H%M%S')}.json",
        )
        log = {
            "timestamp": self.timestamp,
            "status": self.error_code,
            "message": self.message,
            "requestUrl": self.url,
            "parameters": self.parameters,
        }
        with open(outfile, "w") as dst:
            json.dump(obj=log, fp=dst, indent=4)
