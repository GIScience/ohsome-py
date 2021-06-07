#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Class to handle error codes of ohsome API"""

import datetime as dt
import json
import os


class OhsomeException(Exception):
    """Exception to handle ohsome API errors"""

    def __init__(
        self, message=None, url=None, params=None, error_code=None, response=None
    ):
        """Initialize OhsomeException object"""
        super(Exception, self).__init__(message)
        self.message = message
        self.url = url
        if params:
            self.parameters = {k: v for k, v in params.items() if v is not None}
        self.error_code = error_code
        self.response = response
        self.timestamp = dt.datetime.now().isoformat()

    def log(self, log_dir):
        """
        Logs OhsomeException
        :return:
        """
        log_file_name = f"ohsome_{dt.datetime.now().strftime('%Y-%m-%dT%H%M%S')}"
        self.log_bpolys(log_dir, log_file_name)
        self.log_parameter(log_dir, log_file_name)
        if self.response is not None:
            self.log_response(log_dir, log_file_name)
        # self.log_query(log_dir, log_file_name)

    def log_response(self, log_dir, log_file_name):
        """
        Log raw response. This may duplicate much data but is helpful for debugging to know the exact raw answer by the
        ohsome-api.
        """
        log_file = os.path.join(
            log_dir,
            f"{log_file_name}_raw.txt",
        )
        with open(log_file, "w") as dst:
            dst.write(self.response.text)

    def log_parameter(self, log_dir, log_file_name):
        """
        Log query parameters to file
        :param log_dir:
        :return:
        """
        log_file = os.path.join(
            log_dir,
            f"{log_file_name}.json",
        )
        log = {
            "timestamp": self.timestamp,
            "status": self.error_code,
            "message": self.message,
            "requestUrl": self.url,
            "parameters": self.parameters,
        }
        with open(log_file, "w") as dst:
            json.dump(obj=log, fp=dst, indent=4)

    def log_bpolys(self, log_dir, log_file_name):
        """
        Log bpolys parameter to geojson file if it is included in the query
        :params log_file: Path to geojson file which should contain bpolys parameter
        :return:
        """
        if "bpolys" in self.parameters:
            log_file_bpolys = os.path.join(
                log_dir,
                f"{log_file_name}_bpolys.geojson",
            )
            bpolys = self.parameters.pop("bpolys")
            with open(log_file_bpolys, "w") as dst:
                json.dump(obj=json.loads(bpolys), fp=dst, indent=4)

    def log_query(self, log_dir, log_file_name):
        """
        Log ohsome response to file (not implemented)
        :param log_file_response:
        :return:
        """
        # log_file_response = os.path.join(
        #    log_dir,
        #    f"{log_file_name}_query.json",
        # )
        # with open(log_file_response, "w") as dst:
        # put code here to format and log query to a file so it can be easily reproduced

    def __str__(self):
        return f"OhsomeException ({self.error_code}): {self.message}"
